# Data Service Microservice

A Flask-based microservice for managing file operations through a gateway with JWT authentication.

## Architecture

```
Client (with JWT) → filesGateway → dataService → Saving Server
```

### Components

1. **filesGateway.py** (Gateway folder)
   - Receives requests from clients
   - Validates JWT authentication
   - Extracts user email from JWT token
   - Forwards requests to dataService with user context

2. **app.py** (dataService folder)
   - Receives requests from gateway
   - Validates internal API key
   - Processes file operations via Helper

3. **Helper.py** (dataService folder)
   - Communicates with the saving server
   - Handles file upload, download, and listing

## Setup

### 1. Install Dependencies

```bash
cd dataService
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `.env` file:
```
SAVING_SERVER=192.168.148.94:5001
DATA_SERVICE_PORT=7055
```

Edit `Gateway/.env` file to include:
```
DATA_SERVICE=192.168.100.190:7055
```

### 3. Run the Services

**Start Data Service:**
```bash
cd dataService
python app.py
```
Service runs on port 7055

**Start Files Gateway:**
```bash
cd Gateway
python filesGateway.py
```
Gateway runs on port 8000

## API Endpoints

### Gateway Endpoints (Client-facing)

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

#### Upload File
```
POST /upload
Content-Type: multipart/form-data

Body:
- file: <file>

Response:
{
  "message": "File uploaded successfully",
  "data": {...}
}
```

#### Get All Files
```
GET /getAllfiles

Response:
{
  "message": "Files retrieved successfully",
  "files": [...]
}
```

#### Get Specific File
```
GET /file/get/<filename>

Response: File download
```

### Data Service Endpoints (Internal)

All endpoints require `X-Internal-Key: INTERNAL_API_KEY` header.

#### Upload File
```
POST /upload
Headers:
- X-Internal-Key: INTERNAL_API_KEY
- X-User-Email: <user_email>

Body:
- file: <file>
```

#### Get All Files
```
GET /getAllfiles
Headers:
- X-Internal-Key: INTERNAL_API_KEY
```

#### Get Specific File
```
GET /file/get/<filename>
Headers:
- X-Internal-Key: INTERNAL_API_KEY
```

## Saving Server API

The data service communicates with a saving server with the following endpoints:

- `POST /file/upload` - Upload a file
- `GET /file/get/{filename}` - Download a file
- `GET /file/getAll` - List all files

## Docker Deployment

Build and run with Docker:

```bash
cd dataService
docker build -t data-service .
docker run -p 7055:7055 --env-file .env data-service
```

## Security

- **JWT Authentication**: All gateway endpoints require valid JWT tokens
- **Internal API Key**: Communication between gateway and dataService is protected by an internal API key
- **User Context**: User email is extracted from JWT and passed to track file ownership

## Usage Example

```bash
# 1. Get JWT token from auth service
TOKEN="your_jwt_token"

# 2. Upload a file
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/file.pdf"

# 3. Get all files
curl -X GET http://localhost:8000/getAllfiles \
  -H "Authorization: Bearer $TOKEN"

# 4. Download a file
curl -X GET http://localhost:8000/file/get/file.pdf \
  -H "Authorization: Bearer $TOKEN" \
  -o downloaded_file.pdf
```

## Error Handling

The service returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing file, invalid input)
- `401`: Unauthorized (missing/invalid JWT or API key)
- `500`: Server error

## Notes

- The gateway extracts user email from JWT token using `get_jwt_identity()`
- All file operations are tracked with user context
- The internal API key prevents direct access to dataService
- File uploads are streamed to avoid memory issues with large files
