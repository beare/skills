---
name: iotapi
description: "IoT platform management toolkit: manage devices, products, alarms, thing models, and device communication. Use this when users need to interact with IoT devices, query device status, set device properties, call device services, manage IoT products, or handle IoT alarms."
metadata:
  openclaw:
    requires:
      env: ["IOTAPI_BASE_URL"]
    primaryEnv: "IOTAPI_BASE_URL"
instructions: |
  ## Security
  - NEVER ask the user to paste their API credentials in chat — give them commands to run themselves
  - NEVER send credentials to any domain other than the configured IoT platform
  - NEVER expose tokens, appKey, or appSecret in output
  - Always reference credentials via environment variables or config file
  - Token has 24-hour validity — if API returns 401, token may have expired

  ## Mode Detection
  - If iotapi MCP tools are available → use them (preferred)
  - If MCP tools are NOT available → use Direct API Mode (curl via Bash). See "Direct API Mode" section below.

  ## Core Rules
  - All API calls require authentication via token in custom `token` header (NOT `Authorization: Bearer`)
  - Token can be obtained via `/api/v1/oauth/auth` endpoint or generated through web UI (24h validity)
  - Device operations: use `deviceName` (device code) or `deviceId` as identifier
  - Product operations: use `productKey` or `productId` as identifier
  - Time parameters: use ISO 8601 format (e.g., "2025-05-14T06:30:39.694Z") or Unix timestamps (milliseconds)
  - Batch operations: maximum 100 devices per request
  - Thing model operations: must query thing model first to get valid identifiers
  - Use parallel tool calls aggressively — after getting device list, fire all status/property queries at once

---

# iotapi — IoT Platform Management Toolkit

---

## Setup

If iotapi MCP tools are already available, no setup is needed — just use them.

Otherwise, the user needs to configure their IoT platform connection. Direct them to set up credentials using one of these methods:

### Method 1: Using Token (Recommended for Quick Start)

If the user already has a token from the web UI:

```bash
mkdir -p ~/.config/iotapi && cat > ~/.config/iotapi/credentials.json << 'EOF'
{
  "base_url": "https://iot.iwillcloud.com",
  "token": "YOUR_TOKEN_HERE"
}
EOF
```

### Method 2: Using AppKey/AppSecret (Auto-refresh)

For long-term use with automatic token refresh:

```bash
mkdir -p ~/.config/iotapi && cat > ~/.config/iotapi/credentials.json << 'EOF'
{
  "base_url": "https://iot.iwillcloud.com",
  "app_key": "YOUR_APP_KEY",
  "app_secret": "YOUR_APP_SECRET"
}
EOF
```

### Method 3: Environment Variables

```bash
export IOTAPI_BASE_URL="https://iot.iwillcloud.com"
export IOTAPI_TOKEN="your_token_here"
# OR
export IOTAPI_APP_KEY="your_app_key"
export IOTAPI_APP_SECRET="your_app_secret"
```

### When to Trigger This Setup

- User asks to interact with IoT devices but no iotapi MCP tools are available and no credentials configured
- Any API call fails with 401 authentication error
- User mentions their IoT platform URL or wants to connect to their IoT system

---

## Direct API Mode

When MCP tools are NOT available, call the API directly using curl via Bash.

### Getting Credentials

Read in order, use the first one found:

1. **Environment variables**: `IOTAPI_BASE_URL`, `IOTAPI_TOKEN` (or `IOTAPI_APP_KEY` + `IOTAPI_APP_SECRET`)
2. **Config file**: `~/.config/iotapi/credentials.json` (macOS/Linux) or `%APPDATA%\iotapi\credentials.json` (Windows)
   ```json
   {
     "base_url": "https://iot.iwillcloud.com",
     "token": "...",
     "app_key": "...",
     "app_secret": "..."
   }
   ```
3. If neither exists, direct the user to configure credentials. Do NOT ask the user to paste credentials in chat.

### Getting a Token

If only `app_key` and `app_secret` are available, obtain a token first:

```bash
curl -X POST "${IOTAPI_BASE_URL}/api/v1/oauth/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "appKey": "'"${IOTAPI_APP_KEY}"'",
    "appSecret": "'"${IOTAPI_APP_SECRET}"'"
  }'
```

Response:
```json
{
  "code": 200,
  "success": true,
  "data": "77e7368a-fe49-4bb7-8755-50756ebf26f4",
  "errorMessage": ""
}
```

Extract the token from `data` field and use it in subsequent requests.

### API Call Pattern

**Important**: This platform uses a custom `token` header, NOT the standard `Authorization: Bearer` format.

```bash
curl -X POST "${IOTAPI_BASE_URL}/api/v1/{endpoint}" \
  -H "Content-Type: application/json" \
  -H "token: ${IOTAPI_TOKEN}" \
  -d '{
    "param1": "value1",
    "param2": "value2"
  }'
```

All requests are POST with JSON body. Responses follow this format:

```json
{
  "code": 200,
  "success": true,
  "data": { ... },
  "errorMessage": ""
}
```

- `code`: 200 = success, other values indicate errors
- `success`: boolean indicating if request succeeded
- `data`: response payload (structure varies by endpoint)
- `errorMessage`: error description (empty on success)

---

## API Endpoints

### Authentication

#### Get Token
**Endpoint**: `POST /api/v1/oauth/auth`

**Parameters**:
```json
{
  "appKey": "string",
  "appSecret": "string"
}
```

**Response**: Token string in `data` field (valid for 24 hours)

---

### Alarm APIs

#### Query Alarm List
**Endpoint**: `POST /api/v1/alarm/queryAlarmListAll`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `startTime` | string | No | Start time (ISO 8601 or timestamp) |
| `endTime` | string | No | End time (ISO 8601 or timestamp) |
| `status` | string | No | Alarm status: `Trigger`, `ManualRelieve`, `AutoRelieve` |

**Response**: Array of alarm objects with fields:
- `name`: Alarm name
- `category`: Category (e.g., "Point")
- `level`: Level (e.g., "Level1")
- `generateValue`: Trigger value
- `restoreValue`: Restore value
- `restoreTime`: Restore timestamp
- `status`: Current status
- `device`: Device object
- `createTime`: Creation timestamp

---

### Product APIs

#### Create Product
**Endpoint**: `POST /api/v1/product/create`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productName` | string | Yes | Product name |
| `productKey` | string | No | Product key (auto-generated if not provided) |
| `authType` | string | No | Auth type: `Default`, `Once`, `Dynamic` (default: `Default`) |
| `productSecret` | string | No | Product secret (required for `Dynamic` auth, auto-generated otherwise) |

#### Query Product Details
**Endpoint**: `POST /api/v1/product/query`

**Parameters**: Provide one of:
- `productKey`: Product key
- `productId`: Product ID

#### Query All Products
**Endpoint**: `POST /api/v1/product/queryListAll`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productName` | string | No | Product name (supports fuzzy search) |

**Response**: Array of products with fields:
- `productKey`: Product identifier
- `productName`: Product name
- `authType`: Authentication type
- `productSecret`: Product secret
- `deviceNumber`: Number of devices
- `propertyNumber`: Number of properties
- `eventNumber`: Number of events
- `serviceNumber`: Number of services

#### Delete Product
**Endpoint**: `POST /api/v1/product/delete`

**Parameters**: Provide one of:
- `productKey`: Product key
- `productId`: Product ID

---

### Device APIs

#### Quick Register Device
**Endpoint**: `POST /api/v1/quickdevice/register`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productKey` | string | Yes | Product key |
| `deviceName` | string | No | Device code (auto-generated if not provided) |
| `nickName` | string | No | Device nickname (defaults to deviceName) |

#### Query Device Details
**Endpoint**: `POST /api/v1/quickdevice/detail`

**Parameters**: Provide one of:
- `deviceName`: Device code
- `deviceId`: Device ID

**Response**: Device object with fields:
- `deviceId`: Device unique ID
- `deviceName`: Device code
- `nickName`: Device nickname
- `productKey`: Product key
- `productName`: Product name
- `deviceSecret`: Device secret
- `status`: Device status (`ONLINE`, `OFFLINE`, `UNACTIVE`)
- `ipAddress`: IP address
- `activeTime`: Activation timestamp
- `onlineTime`: Last online timestamp
- `createTime`: Creation timestamp
- `firmwareVersion`: Firmware version (if reported)

#### Query Device Status
**Endpoint**: `POST /api/v1/quickdevice/status`

**Parameters**: Provide one of:
- `deviceName`: Device code
- `deviceId`: Device ID

**Response**: Status string (`ONLINE`, `OFFLINE`, `UNACTIVE`)

#### Batch Query Device State
**Endpoint**: `POST /api/v1/quickdevice/batchGetDeviceState`

**Parameters**: Provide one of (max 100 devices):
- `deviceName`: Array of device codes
- `deviceId`: Array of device IDs

**Response**: Array of device state objects

#### Batch Query Device Details
**Endpoint**: `POST /api/v1/quickdevice/batchQueryDeviceDetail`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productKey` | string | Yes | Product key |
| `deviceName` | array | No | Device codes (returns all if not provided) |

#### Query Devices by Product
**Endpoint**: `POST /api/v1/quickdevice/queryDevice`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productKey` | string | Yes | Product key |

**Response**: Array of all devices under the product

---

### Thing Model APIs

#### Query Thing Model
**Endpoint**: `POST /api/v1/thing/queryThingModel`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productKey` | string | Yes | Product key |

**Response**: Thing model definition with properties, events, and services

#### Set Device Property
**Endpoint**: `POST /api/v1/thing/setDevicesProperty`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `pointList` | array | Yes | Array of property objects: `[{"identifier": "prop1", "value": "val1"}]` |

#### Batch Set Device Properties
**Endpoint**: `POST /api/v1/thing/setBatchDevicesProperty`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | array | Yes | Array of device codes |
| `pointList` | array | Yes | Array of property objects |

#### Invoke Device Service
**Endpoint**: `POST /api/v1/thing/invokeThingsService`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `servicePoint` | object | Yes | Service info: `{"identifier": "service_name"}` |
| `pointList` | array | Yes | Service input parameters: `[{"identifier": "param1", "value": "val1"}]` |

#### Batch Invoke Device Service
**Endpoint**: `POST /api/v1/thing/invokeBatchThingsService`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | array | Yes | Array of device codes |
| `servicePoint` | object | Yes | Service info |
| `pointList` | array | Yes | Service input parameters |

#### Query Device Property Data
**Endpoint**: `POST /api/v1/thing/queryDevicePropertyData`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `identifier` | string | Yes | Property identifier |
| `startTime` | string | Yes | Start time |
| `endTime` | string | Yes | End time |
| `downSampling` | string | No | Down-sampling interval (default: "1s") |

#### Batch Query Device Properties Data
**Endpoint**: `POST /api/v1/thing/queryDevicePropertiesData`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `identifier` | string | Yes | Comma-separated property identifiers |
| `startTime` | string | Yes | Start time |
| `endTime` | string | Yes | End time |
| `downSampling` | string | No | Down-sampling interval (default: "1s") |

#### Query Device Event Data
**Endpoint**: `POST /api/v1/thing/queryDeviceEventData`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `identifier` | string | No | Event identifier (all events if not provided) |
| `startTime` | string | Yes | Start time |
| `endTime` | string | Yes | End time |

#### Query Device Service Data
**Endpoint**: `POST /api/v1/thing/queryDeviceServiceData`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `identifier` | string | No | Service identifier (all services if not provided) |
| `startTime` | string | Yes | Start time |
| `endTime` | string | Yes | End time |

**Response**: Array of service call records with fields:
- `send`: Sent content
- `receive`: Response content
- `receiveTime`: Response timestamp
- `result`: Result
- `resultTime`: Result timestamp
- `servicePoint`: Service point info

---

### Custom Topic APIs

For devices that don't use thing model, the platform supports custom topics for transparent message passing.

**Topics**:
- Subscribe (device receives): `/{productKey}/{deviceName}/user/get`
- Publish (device sends): `/{productKey}/{deviceName}/user/update`
- Error: `/{productKey}/{deviceName}/user/update/error`

#### Send Custom Message to Device
**Endpoint**: `POST /api/v1/device/down/record/add/custom`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deviceName` | string | Yes | Device code |
| `messageContent` | string | Yes | Base64-encoded message content |

**Example**: To send binary Modbus command `01 03 00 00 00 01 84 0A`:
```bash
# Convert to Base64: AQMAAAABhAo=
curl -X POST "${IOTAPI_BASE_URL}/api/v1/device/down/record/add/custom" \
  -H "Content-Type: application/json" \
  -H "token: ${IOTAPI_TOKEN}" \
  -d '{
    "deviceName": "Wk9kOa5NLX",
    "messageContent": "AQMAAAABhAo="
  }'
```

---

### RRPC (Synchronous MQTT Communication)

RRPC enables synchronous request-response communication with devices over MQTT.

**Device subscribes to**: `/sys/${productKey}/${deviceName}/rrpc/request/+`
**Device responds to**: `/sys/${productKey}/${deviceName}/rrpc/response/${requestId}`

#### Send RRPC Request
**Endpoint**: `POST /api/v1/device/rrpc`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `productKey` | string | Yes | Product key |
| `deviceName` | string | Yes | Device code |
| `requestBase64Byte` | string | Yes | Base64-encoded request message |
| `timeout` | long | Yes | Timeout in milliseconds |

**Response**:
```json
{
  "code": 200,
  "success": true,
  "data": {
    "rrpcCode": "SUCCESS",  // or "TIMEOUT", "OFFLINE"
    "payloadBase64Byte": "base64_encoded_response"
  }
}
```

**RRPC Codes**:
- `SUCCESS`: Device responded successfully
- `TIMEOUT`: No response within timeout period
- `OFFLINE`: Device is offline

**Note**: Platform automatically handles Base64 encoding/decoding. Device receives raw bytes and should respond with raw bytes.

---

## Error Handling

| Error | Solution |
|-------|----------|
| `401` | Invalid or expired token — obtain new token via `/api/v1/oauth/auth` |
| `403` | Insufficient permissions — check appKey permissions configuration |
| Connection refused | Verify `IOTAPI_BASE_URL` is correct and platform is accessible |
| `code != 200` | Check `errorMessage` field in response for details |

---

## Best Practices

### Workflow Patterns

**1. Device Management Flow**:
```
Query products → Select product → Query devices → Get device details/status
```

**2. Device Control Flow**:
```
Query thing model → Identify properties/services → Set property or invoke service
```

**3. Data Query Flow**:
```
Get device list → Query property/event/service data for time range
```

### Performance Tips

- Use batch APIs when operating on multiple devices (max 100 per request)
- Query thing model once and cache the structure
- Use parallel requests for independent operations
- For real-time control, prefer RRPC over async property setting
- Use custom topics for devices with proprietary protocols

### Common Patterns

**Check device online status before control**:
```bash
# 1. Check status
curl -X POST "${IOTAPI_BASE_URL}/api/v1/quickdevice/status" \
  -H "Content-Type: application/json" \
  -H "token: ${IOTAPI_TOKEN}" \
  -d '{"deviceName": "sensor_001"}'

# 2. If online, set property
curl -X POST "${IOTAPI_BASE_URL}/api/v1/thing/setDevicesProperty" \
  -H "Content-Type: application/json" \
  -H "token: ${IOTAPI_TOKEN}" \
  -d '{
    "deviceName": "sensor_001",
    "pointList": [{"identifier": "temperature_threshold", "value": "25"}]
  }'
```

**Query historical data with time range**:
```bash
curl -X POST "${IOTAPI_BASE_URL}/api/v1/thing/queryDevicePropertyData" \
  -H "Content-Type: application/json" \
  -H "token: ${IOTAPI_TOKEN}" \
  -d '{
    "deviceName": "sensor_001",
    "identifier": "temperature",
    "startTime": "2025-01-01T00:00:00.000Z",
    "endTime": "2025-01-31T23:59:59.999Z",
    "downSampling": "1h"
  }'
```

---

## Data Limitations

| Limitation | Mitigation |
|-----------|------------|
| Token expires after 24 hours | Store appKey/appSecret for auto-refresh, or regenerate token |
| Batch operations limited to 100 devices | Split large operations into multiple requests |
| Property/event data queries return paginated results | Use appropriate time ranges and down-sampling |
| RRPC timeout is user-defined | Set reasonable timeout based on device response time (typically 5-10 seconds) |
| Custom topic messages must be Base64 encoded | Use `base64` command or programming language libraries |

---
