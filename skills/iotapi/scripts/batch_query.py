#!/usr/bin/env python3
"""
Batch Device Status Query
Query multiple devices and export to CSV
"""

import sys
import os
import json
import csv
import argparse
from datetime import datetime

# Add local modules to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from iotsdk_client import IoTClient
from iotsdk_device import DeviceManager


def load_credentials():
    """Load credentials from environment or config file"""
    base_url = os.getenv('IOT_BASE_URL')
    app_id = os.getenv('IOT_APP_ID')
    app_secret = os.getenv('IOT_APP_SECRET')

    if base_url and app_id and app_secret:
        return base_url, app_id, app_secret

    config_path = os.path.expanduser('~/.config/iotapi/credentials.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config['base_url'], config['app_id'], config['app_secret']

    raise ValueError("No credentials found")


def batch_query(device_names, output_format='json', output_file=None):
    """Query multiple devices and output results"""
    base_url, app_id, app_secret = load_credentials()
    client = IoTClient.from_credentials(base_url, app_id, app_secret)
    device_manager = DeviceManager(client)

    # Split into batches of 100
    results = []
    for i in range(0, len(device_names), 100):
        batch = device_names[i:i+100]
        response = device_manager.batch_get_device_status(device_name_list=batch)

        if client.check_response(response):
            results.extend(response['data'])
        else:
            print(f"Error querying batch {i//100 + 1}: {response.get('errorMessage')}", file=sys.stderr)

    # Output results
    if output_format == 'json':
        output = json.dumps(results, indent=2, ensure_ascii=False)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)

    elif output_format == 'csv':
        fieldnames = ['deviceName', 'status', 'timestamp', 'lastOnlineTime']

        if output_file:
            f = open(output_file, 'w', newline='', encoding='utf-8')
        else:
            f = sys.stdout

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for device in results:
            device_status = device.get('deviceStatus', {})
            writer.writerow({
                'deviceName': device.get('deviceName', ''),
                'status': device_status.get('status', ''),
                'timestamp': device_status.get('timestamp', ''),
                'lastOnlineTime': device.get('lastOnlineTime', '')
            })

        if output_file:
            f.close()

    # Print summary
    status_counts = {'ONLINE': 0, 'OFFLINE': 0, 'UNACTIVE': 0}
    for device in results:
        status = device.get('deviceStatus', {}).get('status', 'UNKNOWN')
        if status in status_counts:
            status_counts[status] += 1

    print(f"\nSummary: Total={len(results)}, Online={status_counts['ONLINE']}, "
          f"Offline={status_counts['OFFLINE']}, Unactive={status_counts['UNACTIVE']}",
          file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Batch query device status')
    parser.add_argument('--devices', nargs='+', help='Device names to query')
    parser.add_argument('--file', help='File containing device names (one per line)')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    parser.add_argument('--output', help='Output file (default: stdout)')

    args = parser.parse_args()

    # Get device list
    device_names = []
    if args.devices:
        device_names.extend(args.devices)
    if args.file:
        with open(args.file, 'r') as f:
            device_names.extend([line.strip() for line in f if line.strip()])

    if not device_names:
        print("Error: No devices specified. Use --devices or --file", file=sys.stderr)
        sys.exit(1)

    batch_query(device_names, args.format, args.output)


if __name__ == '__main__':
    main()
