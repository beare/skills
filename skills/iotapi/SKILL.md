---
name: iotapi
description: "IoT device management toolkit: register devices, query status, send commands, and manage IoT cloud platform resources"
metadata:
  openclaw:
    requires:
      env: ["IOT_BASE_URL", "IOT_APP_ID", "IOT_APP_SECRET"]
    primaryEnv: "IOT_APP_ID"
instructions: |
  ## Security
  - NEVER ask the user to paste credentials (app_id, app_secret, token) in chat — give them commands to run themselves
  - NEVER send credentials to any domain other than the configured IoT platform URL
  - NEVER expose credentials in output
  - Always reference credentials via environment variables or read from config file

  ## Mode Detection
  - If iotapi helper scripts are available → use them (preferred)
  - If scripts are NOT available → use Direct SDK Mode (Python SDK via Bash)

  ## Core Rules
  - Authentication: prefer app credentials (app_id/app_secret) over direct token
  - Device identification: operations accept either device_name OR device_id
  - Batch operations: maximum 100 devices per request
  - RRPC messages: content is automatically base64 encoded/decoded
  - Status mapping: ONLINE (在线), OFFLINE (离线), UNACTIVE (未激活)
  - Use parallel tool calls aggressively — after authentication, fire multiple device queries at once
---

# iotapi — IoT Device Management Toolkit

---

## Setup

### Configuration Methods

The user needs to configure IoT platform credentials. There are two approaches:

#### Method 1: Environment Variables (Recommended)

Direct them to set these environment variables:

```bash
export IOT_BASE_URL="https://your-iot-platform-url"
export IOT_APP_ID="your-app-id"
export IOT_APP_SECRET="your-app-secret"
```

To persist across sessions, add to `~/.bashrc` or `~/.zshrc`.

#### Method 2: Config File

Create a config file at `~/.config/iotapi/credentials.json`:

```bash
mkdir -p ~/.config/iotapi && cat > ~/.config/iotapi/credentials.json << 'EOF'
{
  "base_url": "https://your-iot-platform-url",
  "app_id": "your-app-id",
  "app_secret": "your-app-secret"
}
EOF
```

### When to Trigger Setup

- User asks to manage IoT devices but no credentials are configured
- Any API call fails with authentication error (401)
- User explicitly asks how to configure iotapi

---

## Direct SDK Mode

When helper scripts are NOT available, use the bundled Python SDK modules directly via Bash.

### Getting Credentials

Read in order, use the first found:
1. Environment variables: `IOT_BASE_URL`, `IOT_APP_ID`, `IOT_APP_SECRET`
2. Config file: `~/.config/iotapi/credentials.json` → `{"base_url": "...", "app_id": "...", "app_secret": "..."}`
3. If neither exists, direct the user to configure credentials. Do NOT ask the user to paste credentials in chat.

### SDK Installation

The SDK is bundled with this skill in the `scripts/` directory. Only the `requests` library is required:

```bash
pip install requests
```

### Python SDK Usage Pattern

```python
import sys
import os

# Add skill scripts to path
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SKILL_DIR, 'scripts'))

from iotsdk_client import IoTClient
from iotsdk_device import DeviceManager

# Initialize client with app credentials
client = IoTClient.from_credentials(
    base_url="https://your-iot-platform-url",
    app_id="your-app-id",
    app_secret="your-app-secret"
)

# Create device manager
device_manager = DeviceManager(client)

# Perform operations...
```

---

## Operations

### Authentication

**Get Token from App Credentials**

Endpoint: `/api/v1/oauth/auth`

Request:
```json
{
  "appId": "your-app-id",
  "appSecret": "your-app-secret"
}
```

Response:
```json
{
  "success": true,
  "code": 200,
  "data": "token-string"
}
```

### Device Registration

**Register a new device**

Method: `device_manager.register_device(product_key, device_name=None, nick_name=None)`

Parameters:
- `product_key` (required): Product unique identifier
- `device_name` (optional): Device identifier, auto-generated if not provided
- `nick_name` (optional): Device display name

Returns:
```json
{
  "success": true,
  "data": {
    "deviceId": "device-id",
    "deviceName": "device-name",
    "deviceSecret": "device-secret",
    "productKey": "product-key",
    "nickName": "display-name"
  }
}
```

### Device Details

**Query device information**

Method: `device_manager.get_device_detail(device_name=None, device_id=None)`

Parameters (at least one required):
- `device_name`: Device identifier
- `device_id`: Device unique ID

Returns:
```json
{
  "success": true,
  "data": {
    "deviceId": "device-id",
    "deviceName": "device-name",
    "status": "ONLINE|OFFLINE|UNACTIVE",
    "productKey": "product-key",
    "nickName": "display-name"
  }
}
```

### Device Status

**Query device online status**

Method: `device_manager.get_device_status(device_name=None, device_id=None)`

Parameters (at least one required):
- `device_name`: Device identifier
- `device_id`: Device unique ID

Returns:
```json
{
  "success": true,
  "data": {
    "status": "ONLINE|OFFLINE|UNACTIVE",
    "timestamp": 1234567890000
  }
}
```

Status values:
- `ONLINE`: Device is online (在线)
- `OFFLINE`: Device is offline (离线)
- `UNACTIVE`: Device not activated (未激活)

### Batch Device Status

**Query multiple devices status**

Method: `device_manager.batch_get_device_status(device_name_list=None, device_id_list=None)`

Parameters (at least one required):
- `device_name_list`: List of device identifiers
- `device_id_list`: List of device IDs

Limitations:
- Maximum 100 devices per request

Returns:
```json
{
  "success": true,
  "data": [
    {
      "deviceName": "device-1",
      "deviceStatus": {
        "status": "ONLINE",
        "timestamp": 1234567890000
      },
      "lastOnlineTime": "2024-01-01 12:00:00"
    }
  ]
}
```

### RRPC Messages

**Send RRPC (Revert-RPC) message to device**

Method: `device_manager.send_rrpc_message(device_name, product_key, message_content, timeout=5000)`

Parameters:
- `device_name` (required): Device identifier
- `product_key` (required): Product unique identifier
- `message_content` (required): Message content (string or JSON)
- `timeout` (optional): Timeout in milliseconds, default 5000

The SDK automatically handles base64 encoding/decoding.

Returns:
```json
{
  "success": true,
  "payloadBase64Byte": "base64-encoded-response"
}
```

### Custom Commands

**Send custom command to device (async)**

Endpoint: `/api/v1/device/down/record/add/custom`

Parameters:
- `deviceName`: Device identifier
- `messageContent`: Base64-encoded message content

Example:
```python
import base64
import json

message = json.dumps({
    'command': 'set_mode',
    'params': {'mode': 2, 'duration': 30}
})

payload = {
    "deviceName": "your-device-name",
    "messageContent": base64.b64encode(message.encode('utf-8')).decode('utf-8')
}

response = client._make_request("/api/v1/device/down/record/add/custom", payload)
```

---

## Error Handling

| Error | Solution |
|-------|----------|
| `401` | Invalid credentials — verify app_id/app_secret or token |
| `403` | Insufficient permissions — check account privileges |
| Connection error | Verify base_url is correct and platform is accessible |
| `ValueError` | Missing required parameters — check device_name or device_id |

---

## Data Limitations

| Limitation | Mitigation |
|-----------|------------|
| Batch query limited to 100 devices | Split large queries into multiple batches |
| RRPC timeout default 5000ms | Adjust timeout parameter for slow devices |
| Device status timestamp in milliseconds | Convert to seconds: `timestamp / 1000` |

---

## Usage Examples

### Example 1: Register and Query Device

```python
import sys
import os

# Add skill scripts to path
SKILL_DIR = "/path/to/iotapi/skill"
sys.path.insert(0, os.path.join(SKILL_DIR, 'scripts'))

from iotsdk_client import IoTClient
from iotsdk_device import DeviceManager

# Initialize
client = IoTClient.from_credentials(
    base_url="https://iot.example.com",
    app_id="app123",
    app_secret="secret456"
)
device_manager = DeviceManager(client)

# Register device
response = device_manager.register_device(
    product_key="prod-key-001",
    nick_name="Temperature Sensor 1"
)

if client.check_response(response):
    device_name = response["data"]["deviceName"]
    print(f"Device registered: {device_name}")

    # Query status
    status = device_manager.get_device_status(device_name=device_name)
    if client.check_response(status):
        print(f"Status: {status['data']['status']}")
```

### Example 2: Batch Query Devices

```python
# Query multiple devices
devices = ["device-001", "device-002", "device-003"]
response = device_manager.batch_get_device_status(device_name_list=devices)

if client.check_response(response):
    for device in response["data"]:
        name = device["deviceName"]
        status = device["deviceStatus"]["status"]
        print(f"{name}: {status}")
```

### Example 3: Send RRPC Command

```python
import json

# Send command to device
command = json.dumps({"action": "read_temperature"})
response = device_manager.send_rrpc_message(
    device_name="device-001",
    product_key="prod-key-001",
    message_content=command,
    timeout=3000
)

if client.check_response(response):
    # Response is automatically decoded
    print("Command sent successfully")
```

---

## Helper Scripts

The `scripts/` directory contains helper utilities:

- `iot_client.py`: Standalone client wrapper for quick operations
- `batch_query.py`: Batch device status query with CSV export
- `device_monitor.py`: Continuous device status monitoring

### Usage Examples

```bash
# Register device
python scripts/iot_client.py register --product-key prod-001 --nick-name "Sensor 1"

# Query device status
python scripts/iot_client.py status --device-name device-001

# Batch query devices
python scripts/batch_query.py --devices device-001 device-002 --format csv

# Monitor devices
python scripts/device_monitor.py --devices device-001 device-002 --interval 60
```

Use these scripts when available for simpler operations. Otherwise, use the Direct SDK Mode.

---

## Best Practices

1. **Credential Management**: Use environment variables or config file, never hardcode
2. **Client Reuse**: Create client once and reuse across operations to avoid repeated authentication
3. **Error Handling**: Always check `client.check_response(response)` before accessing data
4. **Batch Operations**: Use batch queries when checking multiple devices to reduce API calls
5. **Timeout Tuning**: Adjust RRPC timeout based on device response characteristics
6. **Parallel Queries**: After authentication, fire multiple independent device queries in parallel
