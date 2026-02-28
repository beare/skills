#!/usr/bin/env python3
"""
Device Status Monitor
Continuously monitor device status and alert on changes
"""

import sys
import os
import json
import time
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


def monitor_devices(device_names, interval=60, alert_on_change=True):
    """Monitor device status continuously"""
    base_url, app_id, app_secret = load_credentials()
    client = IoTClient.from_credentials(base_url, app_id, app_secret)
    device_manager = DeviceManager(client)

    previous_status = {}

    print(f"Monitoring {len(device_names)} devices (interval: {interval}s)")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Checking devices...")

            # Query devices in batches
            current_status = {}
            for i in range(0, len(device_names), 100):
                batch = device_names[i:i+100]
                response = device_manager.batch_get_device_status(device_name_list=batch)

                if client.check_response(response):
                    for device in response['data']:
                        device_name = device.get('deviceName')
                        status = device.get('deviceStatus', {}).get('status')
                        current_status[device_name] = status

            # Check for changes
            changes = []
            for device_name, status in current_status.items():
                if device_name in previous_status:
                    if previous_status[device_name] != status:
                        changes.append({
                            'device': device_name,
                            'old': previous_status[device_name],
                            'new': status
                        })

            # Report changes
            if changes:
                print(f"  ⚠️  Status changes detected:")
                for change in changes:
                    print(f"    {change['device']}: {change['old']} → {change['new']}")
            else:
                # Print summary
                status_counts = {'ONLINE': 0, 'OFFLINE': 0, 'UNACTIVE': 0}
                for status in current_status.values():
                    if status in status_counts:
                        status_counts[status] += 1
                print(f"  ✓ Online: {status_counts['ONLINE']}, "
                      f"Offline: {status_counts['OFFLINE']}, "
                      f"Unactive: {status_counts['UNACTIVE']}")

            previous_status = current_status
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped")


def main():
    parser = argparse.ArgumentParser(description='Monitor device status continuously')
    parser.add_argument('--devices', nargs='+', help='Device names to monitor')
    parser.add_argument('--file', help='File containing device names (one per line)')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')

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

    monitor_devices(device_names, args.interval)


if __name__ == '__main__':
    main()
