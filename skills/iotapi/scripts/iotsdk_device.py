"""
Device Manager Module
Device management operations for IoT platform
"""

import base64
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime


class DeviceManager:
    """Device management module"""

    def __init__(self, client):
        """
        Initialize device manager

        Args:
            client: IoT client instance
        """
        self.client = client
        self.logger = client.logger

    def register_device(self,
                       product_key: str,
                       device_name: Optional[str] = None,
                       nick_name: Optional[str] = None) -> Dict:
        """
        Register a new device

        Args:
            product_key: Product unique identifier
            device_name: Device identifier (optional, auto-generated if not provided)
            nick_name: Device display name (optional)

        Returns:
            Dict: Registration result with device ID and secret
        """
        endpoint = "/api/v1/quickdevice/register"

        # Build request body
        payload = {
            "productKey": product_key
        }

        # Add optional parameters
        if device_name:
            payload["deviceName"] = device_name

        if nick_name:
            payload["nickName"] = nick_name

        # Send request
        response = self.client._make_request(endpoint, payload)

        # Check result and format output
        if self.client.check_response(response):
            device_info = response["data"]
            self.logger.info(f"Device registered successfully: {device_info['deviceName']}")

        return response

    def get_device_detail(self,
                         device_name: Optional[str] = None,
                         device_id: Optional[str] = None) -> Dict:
        """
        Query device details

        Args:
            device_name: Device identifier (optional)
            device_id: Device unique ID (optional)

        Returns:
            Dict: Device detail information

        Note:
            At least one of device_name or device_id must be provided
        """
        # Parameter validation
        if not device_name and not device_id:
            raise ValueError("At least one of device_name or device_id must be provided")

        endpoint = "/api/v1/quickdevice/detail"

        # Build request body
        payload = {}
        if device_name:
            payload["deviceName"] = device_name
        if device_id:
            payload["deviceId"] = device_id

        # Send request
        response = self.client._make_request(endpoint, payload)

        return response

    def get_device_status(self,
                         device_name: Optional[str] = None,
                         device_id: Optional[str] = None) -> Dict:
        """
        Query device online status

        Args:
            device_name: Device identifier (optional)
            device_id: Device unique ID (optional)

        Returns:
            Dict: Device status information

        Note:
            At least one of device_name or device_id must be provided
        """
        # Parameter validation
        if not device_name and not device_id:
            raise ValueError("At least one of device_name or device_id must be provided")

        endpoint = "/api/v1/quickdevice/status"

        # Build request body
        payload = {}
        if device_name:
            payload["deviceName"] = device_name
        if device_id:
            payload["deviceId"] = device_id

        # Send request
        response = self.client._make_request(endpoint, payload)

        return response

    def batch_get_device_status(self,
                               device_name_list: Optional[List[str]] = None,
                               device_id_list: Optional[List[str]] = None) -> Dict:
        """
        Batch query device status

        Args:
            device_name_list: List of device identifiers (optional)
            device_id_list: List of device IDs (optional)

        Returns:
            Dict: Batch device status information

        Note:
            At least one of device_name_list or device_id_list must be provided
            Maximum 100 devices per request
        """
        # Parameter validation
        if not device_name_list and not device_id_list:
            raise ValueError("At least one of device_name_list or device_id_list must be provided")

        # Check device count limit
        device_count = len(device_name_list or []) + len(device_id_list or [])
        if device_count > 100:
            raise ValueError(f"Maximum 100 devices per request, current request has {device_count} devices")

        endpoint = "/api/v1/quickdevice/batchGetDeviceState"

        # Build request body
        payload = {}
        if device_name_list:
            payload["deviceName"] = device_name_list
        if device_id_list:
            payload["deviceId"] = device_id_list

        # Send request
        response = self.client._make_request(endpoint, payload)

        return response

    def send_rrpc_message(self,
                         device_name: str,
                         product_key: str,
                         message_content: str,
                         timeout: int = 5000) -> Dict:
        """
        Send RRPC message to device

        Args:
            device_name: Device identifier
            product_key: Product unique identifier
            message_content: Message content
            timeout: Timeout in milliseconds (default 5000)

        Returns:
            Dict: Message send result
        """
        endpoint = "/api/v1/device/rrpc"

        # Base64 encode message content
        message_bytes = message_content.encode('utf-8')
        base64_message = base64.b64encode(message_bytes).decode('utf-8')

        # Build request body
        payload = {
            "deviceName": device_name,
            "productKey": product_key,
            "requestBase64Byte": base64_message,
            "timeout": timeout
        }

        # Send request
        response = self.client._make_request(endpoint, payload)

        # Check result and parse response
        if self.client.check_response(response):
            # Get base64 encoded response
            base64_payload = response.get("payloadBase64Byte")

            if base64_payload:
                # Decode base64 string
                try:
                    decoded_bytes = base64.b64decode(base64_payload)
                    decoded_string = decoded_bytes.decode('utf-8')
                    response["decoded_response"] = decoded_string

                    # Try to parse as JSON
                    try:
                        json_data = json.loads(decoded_string)
                        response["decoded_json"] = json_data
                    except json.JSONDecodeError:
                        pass

                except Exception as e:
                    self.logger.error(f"Failed to parse response content: {e}")

        return response

    def send_custom_command(self,
                           device_name: str,
                           message_content: str) -> Dict:
        """
        Send custom command to device (async)

        Args:
            device_name: Device identifier
            message_content: Message content (will be base64 encoded)

        Returns:
            Dict: Command send result
        """
        endpoint = "/api/v1/device/down/record/add/custom"

        # Base64 encode message content
        message_bytes = message_content.encode('utf-8')
        base64_message = base64.b64encode(message_bytes).decode('utf-8')

        # Build request body
        payload = {
            "deviceName": device_name,
            "messageContent": base64_message
        }

        # Send request
        response = self.client._make_request(endpoint, payload)

        return response
