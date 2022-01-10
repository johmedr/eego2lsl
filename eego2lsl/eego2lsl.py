import argparse
from .utils import cmd_list, cmd_stream


def main():
	parser = argparse.ArgumentParser()
	subparser = parser.add_subparsers(dest='command')


	list_parser = subparser.add_parser('list')
	list_parser.set_defaults(func=cmd_list)

	stream_parser = subparser.add_parser('stream')
	stream_parser.set_defaults(func=cmd_stream)

	stream_parser.add_argument('type', type=str, help="One of 'eeg', 'imp'")
	stream_parser.add_argument('--stream-name', dest='stream_name', type=str, default="eego_stream")
	stream_parser.add_argument('--amp', type=int, default=0)
	stream_parser.add_argument('--chunks', type=int, default=8)
	stream_parser.add_argument('--rate', type=int, default=1000)
	stream_parser.add_argument('--bip', action='store_true')
	stream_parser.add_argument('--headcap', type=str, default='waveguard_net')
	stream_parser.add_argument('--no-eeg', action='store_true', dest='no_eeg')
	stream_parser.add_argument('--eeg-range', dest='eeg_range', type=float, default=0.75)
	stream_parser.add_argument('--bip-range', dest='bip_range', type=float, default=1.5)
	stream_parser.add_argument('-c', '--channel_file', dest='channel_file', type=str, default='')

	args = parser.parse_args()
	if args.command is None:
		parser.print_help()
	else: 
		res = args.func(args)
		if res is False:
			parser.print_help()


