## Streem EEGO data to LSL

### Installing the package: 
This package requires the SDK distributed by ANT Neuro, as well as the Python bindings for eego SDK. The bindings are available at https://gitlab.com/smeeze/eego-sdk-pybind11 (a one-liner to install them is at the end of this document). 
Then, simply run 
```
pip install git+https://github.com/yop0/eego2lsl.git
```

### Usage:

 - Listing amplifiers
```
usage: eego2lsl list [-h]
```
 - Launching the stream 
```
usage: eego2lsl stream [-h] [--headcap HEADCAP] [--stream-name STREAM_NAME]
                       [--amp AMP] [--chunks CHUNKS] [--rate RATE] [--bip BIP]
                       [--no-eeg] [--eeg-range EEG_RANGE]
                       [--bip-range BIP_RANGE] [-c CHANNEL_FILE]
                       type

positional arguments:
  type                  One of 'data', 'impedance'

optional arguments:
  -h, --help            show this help message and exit
  --headcap HEADCAP     One of 'net', 'original'
  --stream-name STREAM_NAME
  --amp AMP
  --chunks CHUNKS
  --rate RATE           Amplifier rate
  --bip BIP             Either the number of BIP channels to include or 'all'
  --no-eeg
  --eeg-range EEG_RANGE
  --bip-range BIP_RANGE
  -c CHANNEL_FILE, --channel_file CHANNEL_FILE

```

### Examples: 
 - Stream EEG impedance with the Waveguard Net on a LSL outlet called `eeg-impedance` (e.g. for visualization in PlotJuggler): 
```
eego2lsl stream --headcap net --stream-name eeg-impedance impedance
```
 - Stream EEG data at 2,000Hz with the Waveguard Original on a LSL outlet called `eeg`:
```
eego2lsl stream --headcap original --stream-name eeg data --rate 2000 data
```
 - Stream EMG data for 3 bipolar channels at 1,000Hz on an outlet called `emg`:
```
eego2lsl stream --stream-name emg --rate 1000 --bip 3 --no-eeg data
```

### Troubleshooting:
 - Only one program can access the amplifier. If the amplifier is not found, kill other processes that might use it (e.g. `pkill eego2lsl`). 
 - There might be some issue in detecting the amplifiers on the first use because a new `udev` rule must be added. The solution is to add manually a new rule. 
 For the EEGO sport amplifier, the rule is: 
```bash
cat "ATTRS{idVendor}=="2a56", ATTRS{idProduct}=="ee01", SYMLINK+="eego3.%n", MODE:="0666", ENV{DEVTYPE}=="usb_device" | sudo tee /etc/udev/70-eego.rules
```
where the value `ee01` must be replaced for other amplifiers. The rules must then be reloaded with:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

--- 
#### Installing the Python bindings
Provided that the file `eego-SDK-x.x.x.xxxxx.zip` is at location `SDK_PATH`, the bindings can be installed (in the folder INSTALL_DIR) with the following one-liner:
```
INSTALL_DIR="." SDK_PATH="./eego-SDK-1.3.19.40453.zip" bash -c \
    'git clone https://gitlab.com/smeeze/eego-sdk-pybind11.git eego-bindings && \
    cd eego-bindings && echo "set(EEGO_SDK_ZIP $SDK_PATH)" > user.cmake && \
    mkdir build && cd build && cmake .. && make -j7 && sudo make install'
```
