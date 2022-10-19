import eego_sdk
import pylsl
import asyncio
import warnings
import time
import os
from .elc_parser import read_channels_positions


class FactorySingleton(eego_sdk.factory): 
    _instances = {}

    def __call__(cls, *args, **kwargs): 
        if cls not in cls._instances is None: 
            cls._instances[cls] = super(FactorySingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
            

def list_amplifiers():
    f = FactorySingleton()
    return f.getAmplifiers()

def fmt_list_to_str(l): 
    s = ''
    for i, e in enumerate(l):
        s += str(e)
        if i < len(l) - 1: 
            s += ', '
    return s

def cmd_list(*args): 
    amps = list_amplifiers()
    if len(amps) == 0:
        return 

    print("{:<4} {:<7} {:<10} {:<10} {:<15} {:<15} {:<15}"
        .format("num", "type", "serial n°", "firmware", "EEG range (V)", "BIP range (V)", "Rate (Hz)"))
    for i, amp in enumerate(amps):
        tk = "{:<4} {:<7} {:<10} {:<10} "\
            .format(i, amp.getType(), amp.getSerialNumber(), amp.getFirmwareVersion())
        print(tk, end="")

        eeg, bip, rate = amp.getReferenceRangesAvailable(), amp.getBipolarRangesAvailable(), amp.getSamplingRatesAvailable()
        for j in range(max(len(eeg), len(bip), len(rate))):
            if j != 0:
                print(" " * len(tk), end='') 
            print("{:<15} {:<15} {:<15}"\
                .format(
                    eeg[j] if j < len(eeg) else "",
                    bip[j] if j < len(bip) else "",
                    rate[j] if j < len(rate) else "",
                )
            )

def parse_channel_names(fname):
    ch_names = []
    with open(fname, 'r') as f:
        for l in f.readlines():
            ch_names.append(l.split('\n')[0])

    return ch_names

def cmd_stream(args):
    stream_name  = args.stream_name
    dtype        = args.type
    amp          = args.amp
    rate         = args.rate
    chunks       = args.chunks
    eeg_range    = args.eeg_range
    bip_range    = args.bip_range
    channel_file = args.channel_file
    headcap      = args.headcap
    has_eeg      = not args.no_eeg
    has_bip      = len(args.bip) > 0
    if has_bip:
        bip      = int(args.bip) if args.bip != 'all' else 10_000
    else: bip    = 0

    assert(has_bip or has_eeg)
    assert(dtype in ['data', 'impedance'])

    if has_eeg:
        if headcap not in ('net', 'original'): 
            raise AttributeError("Headcap must be either 'net' (for Waveguard Net) or 'original' (for Waveguard Original).")

    if has_bip: 
        pass


    amps = list_amplifiers()
    if len(amps) == 0:
        raise RuntimeError("No amplifier found!")

    amp      = amps[amp]
    channels = amp.getChannelList()

    if dtype == 'imp':
        rate = 60
        chunks = 1
    else: 
        if rate not in amp.getSamplingRatesAvailable():
            raise ValueError('Invalid rate.')

        if has_eeg and eeg_range not in amp.getReferenceRangesAvailable():
            raise ValueError('Invalid eeg range.')
        
        if bip and bip_range not in amp.getBipolarRangesAvailable():
            raise ValueError('Invalid bip range.')


    if rate % chunks != 0:
        warnings.warn(f"Rate {rate} is not divisible in {chunks} chunks! Packet losses may result.")
    lsl_rate = rate // chunks
    stream_channels = []

    nbip = 0
    for ch in channels:
        if has_bip and ch.getType() == eego_sdk.channel_type.bip and nbip < bip: 
            nbip += 1
            stream_channels.append({
                'index': ch.getIndex(),
                'name': f'BIP{nbip}', 
                'type': 'bip'
            })
        elif has_eeg and ch.getType() == eego_sdk.channel_type.ref:
            stream_channels.append({
                'index': ch.getIndex(),
                'name': str(ch), 
                'type': 'eeg'
            })

    if channel_file == "":
        this_dir     = os.path.realpath(os.path.dirname(__file__))
        extra_path   = os.path.join(this_dir, 'extra')
        cap_ch_count = len([_ for _ in stream_channels if _['type'] == 'eeg'])
        channel_file = os.path.join(extra_path, f"waveguard_{headcap}_{cap_ch_count}.txt")


    try: 
        ch_names = parse_channel_names(channel_file)
        
        assert(len(ch_names) == cap_ch_count)
        
        for name, ch in zip(ch_names, stream_channels):
            if ch['type'] == 'eeg':
                ch['name'] = name
                
        ch_pos, desc = read_channels_positions(f"waveguard_{headcap}_{cap_ch_count}.elc", return_desc=True)
        # if all(ch['name'] in ch_pos.keys() for ch in stream_channels):
        _stream_channels_ok = []
        for ch in stream_channels:
            try:
                ch['pos'] = ch_pos[ch['name']]
            except KeyError:
                ch['pos'] = (None, None, None)
            _stream_channels_ok.append(ch)
        stream_channels = _stream_channels_ok

    except Exception as e:
        print("Cannot get channel names. Got error:")
        print(e)
        print("Skipping. ")

    stream_info = pylsl.StreamInfo(
        name          =stream_name, 
        type          =dtype, 
        channel_format=pylsl.cf_float32, 
        channel_count =len(stream_channels), 
        nominal_srate =rate,
        source_id     =stream_name,
    )

    chann_desc = stream_info.desc().append_child('channels')
    if 'pos' in stream_channels[0].keys():
        for ch in stream_channels:
            chd = chann_desc.append_child('channel')
            chd.append_child_value('label', ch['name'])\
                .append_child_value('unit', 'V' if dtype == 'eeg' else 'Ohms')\
                .append_child_value('type', ch['type'])

            chd.append_child('location').append_child_value('X', str(ch['pos'][1]))\
                                    .append_child_value('Y', str(ch['pos'][0]))\
                                    .append_child_value('Z', str(ch['pos'][2]))\
                                    .append_child_value('unit', desc['UnitPosition'])

    else:
        for ch in stream_channels:
            chann_desc.append_child('channel')\
                .append_child_value('label', ch['name'])\
                .append_child_value('unit', 'V' if dtype == 'eeg' else 'Ohms')\
                .append_child_value('type', ch['type'])


    stream_outlet = pylsl.StreamOutlet(stream_info)


    print(  
        f'Stream configuration is: \n'
        f'  name: {stream_info.name()}\n'
        f'  type: {stream_info.type()}\n'
        f'  uid: {stream_info.source_id()}\n'
        f'  channels: {stream_info.channel_count()}\n'
        f'  rate: {stream_info.nominal_srate()}Hz\n'
        f'Now streaming!'
    )


    if dtype == "eeg":
        stream_amp = amp.OpenEegStream(rate, eeg_range, bip_range)
    elif dtype == "imp":
        stream_amp = amp.OpenImpedanceStream()

    loop = asyncio.get_event_loop()
    stopped = False

    ttarget = 1./lsl_rate
    
    while not stopped:
        try: 
            tstart = time.perf_counter()

            buffer = stream_amp.getData()

            chunk = [
                [buffer.getSample(c['index'], s) for c in stream_channels]
                for s in range(buffer.getSampleCount())
            ]
            stream_outlet.push_chunk(chunk)

            loop.run_until_complete(asyncio.sleep(max(ttarget - (tstart - time.perf_counter()), 0)))


        except (KeyboardInterrupt, SystemExit): 
            break