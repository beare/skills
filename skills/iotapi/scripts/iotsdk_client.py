"""
IoT Client Module
Standalone IoT platform client implementation
"""

import requests
import json
import logging
from typing import Dict, Optional


class IoTClient:
    """IoT cloud platform client"""

    def __init__(self, base_url: str, token: str, logger=None):
        """
        Initialize IoT client

        Args:
            base_url: API base URL
            token: Authentication token
            logger: Optional logger instance
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.logger = logger or logging.getLogger('iotsdk')

        if not self.base_url:
            raise ValueError("Invalid base_url")
        if not self.token:
            raise ValueError("Invalid token")

    @classmethod
    def from_credentials(cls, base_url: str, app_id: str, app_secret: str, logger=None):
        """
        Initialize client using app credentials

        Args:
            base_url: API base URL
            app_id: Application ID
            app_secret: Application secret
            logger: Optional logger instance

        Returns:
            IoTClient: Initialized client instance
        """
        logger = logger or logging.getLogger('iotsdk')

        # Build authentication URL
        auth_url = f"{base_url.rstrip('/')}/api/v1/oauth/auth"

        # Prepare authentication request
        headers = {"Content-Type": "application/json"}
        payload = {
            "appId": app_id,
            "appSecret": app_secret
        }

        try:
            # Send authentication request
            response = requests.post(auth_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Check if response is successful
            if not result.get("success") or result.get("code") != 200:
                error_msg = result.get("errorMessage", "Unknown error")
                raise ValueError(f"Authentication failed: {error_msg}")

            # Get token and create client instance
            token = result["data"]
            logger.info("Authentication successful")

            return cls(base_url=base_url, token=token, logger=logger)

        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication request error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Authentication response parse error: {e}")
            raise ValueError(f"Cannot parse authentication response as JSON: {e}")

    def _make_request(self,
                     endpoint: str,
                     payload: Dict = None,
                     method: str = 'POST',
                     additional_headers: Dict = None) -> Dict:
        """
        Send API request

        Args:
            endpoint: API endpoint path
            payload: Request body data
            method: HTTP method (default POST)
            additional_headers: Additional request headers

        Returns:
            Dict: API response result
        """
        # Build full URL
        url = f"{self.base_url}{endpoint}"

        # Set request headers
        headers = {
            "Content-Type": "application/json",
            "token": self.token
        }

        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)

        # Prepare request data
        payload_data = json.dumps(payload) if payload else None

        try:
            # Send request
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=payload_data)
            elif method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=payload)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check HTTP status code
            response.raise_for_status()

            # Parse response
            result = response.json()

            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            raise ValueError(f"Cannot parse response as JSON: {e}")

    def check_response(self, response: Dict) -> bool:
        """
        Check if API response is successful

        Args:
            response: API response

        Returns:
            bool: Whether successful
        """
        if not response:
            return False

        success = response.get("success", False)

        if not success:
            error_msg = response.get("errorMessage", "Unknown error")
            self.logger.warning(f"API call failed: {error_msg}")

        return success
