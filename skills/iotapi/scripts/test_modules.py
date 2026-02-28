#!/usr/bin/env python3
"""
Test script to verify iotapi skill modules work correctly
"""

import sys
import os

# Add scripts to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

try:
    from iotsdk_client import IoTClient
    from iotsdk_device import DeviceManager
    print("✓ Successfully imported IoTClient and DeviceManager")

    # Test credential loading
    def test_credentials():
        base_url = os.getenv('IOT_BASE_URL')
        app_id = os.getenv('IOT_APP_ID')
        app_secret = os.getenv('IOT_APP_SECRET')

        if base_url and app_id and app_secret:
            print("✓ Found credentials in environment variables")
            return True

        config_path = os.path.expanduser('~/.config/iotapi/credentials.json')
        if os.path.exists(config_path):
            print("✓ Found credentials in config file")
            return True

        print("✗ No credentials found")
        print("  Set IOT_BASE_URL, IOT_APP_ID, IOT_APP_SECRET environment variables")
        print("  or create ~/.config/iotapi/credentials.json")
        return False

    test_credentials()

    print("\nAll modules loaded successfully!")
    print("The iotapi skill is ready to use.")

except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
