#!/usr/bin/env python3
"""
IoT Client Wrapper
Standalone script for quick IoT device operations
"""

import sys
import os
import json
import argparse

# Add local modules to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from iotsdk_client import IoTClient
from iotsdk_device import DeviceManager


def load_credentials():
    """Load credentials from environment or config file"""
    # Try environment variables first
    base_url = os.getenv('IOT_BASE_URL')
    app_id = os.getenv('IOT_APP_ID')
    app_secret = os.getenv('IOT_APP_SECRET')

    if base_url and app_id and app_secret:
        return base_url, app_id, app_secret

    # Try config file
    config_path = os.path.expanduser('~/.config/iotapi/credentials.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config['base_url'], config['app_id'], config['app_secret']

    raise ValueError("No credentials found. Set IOT_BASE_URL, IOT_APP_ID, IOT_APP_SECRET environment variables or create ~/.config/iotapi/credentials.json")


def create_client():
    """Create and return IoT client"""
    base_url, app_id, app_secret = load_credentials()
    return IoTClient.from_credentials(base_url, app_id, app_secret)


def register_device(args):
    """Register a new device"""
    client = create_client()
    device_manager = DeviceManager(client)

    response = device_manager.register_device(
        product_key=args.product_key,
        device_name=args.device_name,
        nick_name=args.nick_name
    )

    if client.check_response(response):
        print(json.dumps(response['data'], indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.get('errorMessage', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


def get_device_status(args):
    """Get device status"""
    client = create_client()
    device_manager = DeviceManager(client)

    response = device_manager.get_device_status(
        device_name=args.device_name,
        device_id=args.device_id
    )

    if client.check_response(response):
        print(json.dumps(response['data'], indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.get('errorMessage', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


def get_device_detail(args):
    """Get device details"""
    client = create_client()
    device_manager = DeviceManager(client)

    response = device_manager.get_device_detail(
        device_name=args.device_name,
        device_id=args.device_id
    )

    if client.check_response(response):
        print(json.dumps(response['data'], indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.get('errorMessage', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


def send_rrpc(args):
    """Send RRPC message"""
    client = create_client()
    device_manager = DeviceManager(client)

    response = device_manager.send_rrpc_message(
        device_name=args.device_name,
        product_key=args.product_key,
        message_content=args.message,
        timeout=args.timeout
    )

    if client.check_response(response):
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.get('errorMessage', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='IoT Device Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Register device
    register_parser = subparsers.add_parser('register', help='Register a new device')
    register_parser.add_argument('--product-key', required=True, help='Product key')
    register_parser.add_argument('--device-name', help='Device name (optional)')
    register_parser.add_argument('--nick-name', help='Device display name (optional)')
    register_parser.set_defaults(func=register_device)

    # Get status
    status_parser = subparsers.add_parser('status', help='Get device status')
    status_parser.add_argument('--device-name', help='Device name')
    status_parser.add_argument('--device-id', help='Device ID')
    status_parser.set_defaults(func=get_device_status)

    # Get details
    detail_parser = subparsers.add_parser('detail', help='Get device details')
    detail_parser.add_argument('--device-name', help='Device name')
    detail_parser.add_argument('--device-id', help='Device ID')
    detail_parser.set_defaults(func=get_device_detail)

    # Send RRPC
    rrpc_parser = subparsers.add_parser('rrpc', help='Send RRPC message')
    rrpc_parser.add_argument('--device-name', required=True, help='Device name')
    rrpc_parser.add_argument('--product-key', required=True, help='Product key')
    rrpc_parser.add_argument('--message', required=True, help='Message content')
    rrpc_parser.add_argument('--timeout', type=int, default=5000, help='Timeout in ms (default: 5000)')
    rrpc_parser.set_defaults(func=send_rrpc)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
