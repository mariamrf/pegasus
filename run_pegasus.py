#!/usr/bin/env python3
import argparse
from pegasus import app

parser = argparse.ArgumentParser()
parser.add_argument('-ip', help='type in an IP address', type=str, default='127.0.0.1', nargs='?', metavar='IP ADDRESS')
parser.add_argument('-port', help='type in a port number', type=int, choices=range(0, 65535), default=5000, metavar='PORT NUMBER', nargs='?')
parser.add_argument('--debug', dest='debug', action='store_true')
parser.add_argument('--no-debug', dest='debug', action='store_false')
parser.set_defaults(debug=True)
args = parser.parse_args()

app.run(host=args.ip, port=args.port, debug=args.debug)
