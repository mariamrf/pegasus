#!/usr/bin/python3
import argparse
from ipaddress import ip_address
parser = argparse.ArgumentParser()
parser.add_argument('ip', help='type in an IP address', type=ip_address, default='127.0.0.1', nargs='?', metavar='IP ADDRESS')
parser.add_argument('port', help='type in a port number', type=int, choices=range(0,65535), default=5000, metavar='PORT NUMBER', nargs='?')
args = parser.parse_args()
print(args.ip, args.port)