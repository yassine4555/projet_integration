# SAVING_SERVER Integration Guide for Server Team

## 📋 Overview

This document provides the server team with everything needed to integrate with the SAVING_SERVER API.

**Service Information:**
- **Name:** SAVING_SERVER
- **Version:** 1.0
- **Base URL:** `http://localhost:5001` (development)
- **Protocol:** HTTP/REST
- **Data Format:** JSON
- **Authentication:** API Key

---

## 🔐 Authentication

### Required Header
All requests must include:
```http
X-Internal-Key: nexus-internal-secret-key-123
Content-Type: application/json
```

### Example Request
```bash
curl -X GET http://localhost:5001/users/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json"
```

---

## 🚀 Getting Started

### Step 1: Verify Service is Running
```bash
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "SAVING_SERVER",
  "version": "1.0"
}
```

### Step 2: Check Database Connection
```bash
curl http://localhost:5001/
```

Expected response:
```json
{
  "status": "SAVING_SERVER Ready",
  "db_connection": "OK"
}
```

### Step 3: Test Authentication
```bash
curl -X GET http://localhost:5001/users/ \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

---

## 📡 Core Integration Workflows

### Workflow 1: User Registration & Management

#### 1.1 Create a New User
```http
POST /users/
Content-Type: application/json
X-Internal-Key: nexus-internal-secret-key-123

{
  "email": "newuser@company.com",
  "userID": "auth0_xyz123",
  "role": "employee",
  "first_name": "Jane",
  "last_name": "Smith",
  "department": "Engineering"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "newuser@company.com",
  "userID": "auth0_xyz123",
  "role": "employee",
  "first_name": "Jane",
  "last_name": "Smith",
  "department": "Engineering",
  "created_at": "2025-12-07T10:30:00Z"
}
```

#### 1.2 Update User Information
```http
PUT /users/newuser@company.com
Content-Type: application/json
X-Internal-Key: nexus-internal-secret-key-123

{
  "department": "Product",
  "role": "manager"
}
```

#### 1.3 Get All Users
```http
GET /users/
X-Internal-Key: nexus-internal-secret-key-123
```

---

### Workflow 2: Meeting Management

#### 2.1 Create a Meeting
```http
POST /meetings/
Content-Type: application/json
X-Internal-Key: nexus-internal-secret-key-123

{
  "title": "Q4 Planning Meeting",
  "object": "Quarterly planning",
  "description": "Review Q4 goals and objectives",
  "created_by": "manager@company.com",
  "password": "meeting2025",
  "invited_employees": [
    "employee1@company.com",
    "employee2@company.com"
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "meeting_id": "mtg_a1b2c3d4e5f6",
  "title": "Q4 Planning Meeting",
  "invitation_link": "http://localhost:5001/join/mtg_a1b2c3d4e5f6",
  "password": "meeting2025",
  "created_by": "manager@company.com",
  "invited_employees_list": ["employee1@company.com"],
  "is_active": true,
  "created_at": "2025-12-07T10:30:00Z"
}
```

#### 2.2 Start Meeting
```http
POST /meetings/mtg_a1b2c3d4e5f6/start
X-Internal-Key: nexus-internal-secret-key-123
```

#### 2.3 Log Meeting Activity
```http
POST /meetings/mtg_a1b2c3d4e5f6/log
Content-Type: application/json
X-Internal-Key: nexus-internal-secret-key-123

{
  "log_entry": "User John Doe joined the meeting"
}
```

#### 2.4 End Meeting
```http
POST /meetings/mtg_a1b2c3d4e5f6/end
X-Internal-Key: nexus-internal-secret-key-123
```

#### 2.5 Get Meeting Log
```http
GET /meetings/mtg_a1b2c3d4e5f6/log
X-Internal-Key: nexus-internal-secret-key-123
```

#### 2.6 Download Meeting Log
```http
GET /meetings/mtg_a1b2c3d4e5f6/log?download=true
X-Internal-Key: nexus-internal-secret-key-123
```

---

### Workflow 3: File Upload & Download

#### 3.1 Upload a File
```bash
curl -X POST http://localhost:5001/file/upload \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -F "file=@/path/to/document.pdf" \
  -F "user_email=user@company.com"
```

**Response (200):**
```json
{
  "success": true,
  "filename": "document.pdf",
  "file_id": "file_abc123xyz",
  "url": "/file/get/document.pdf"
}
```

#### 3.2 Download a File
```http
GET /file/get/document.pdf
X-Internal-Key: nexus-internal-secret-key-123
```

#### 3.3 List User's Files
```http
GET /file/getAll?user_email=user@company.com
X-Internal-Key: nexus-internal-secret-key-123
```

---

### Workflow 4: Manager Promotion System

#### 4.1 HR Creates Promotion Code
```http
POST /manager_codes/becameManagerCode
Content-Type: application/json
X-Internal-Key: nexus-internal-secret-key-123

{
  "hrid": "hr_user_456",
  "code": "PROMO2025Q1",
  "max_uses": 1
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Code saved successfully",
  "data": {
    "id": 1,
    "code": "PROMO2025Q1",
    "hrid": "hr_user_456",
    "max_uses": 1,
    "used_count": 0,
    "is_active": true,
    "created_at": "2025-12-07T10:30:00Z"
  }
}
```

#### 4.2 Employee Uses Promotion Code
```http
POST /manager_codes/validateBecameManagerCode
Content-Type: application/json
X-Internal-Key: nexus-internal-secret-key-123

{
  "code": "PROMO2025Q1",
  "userMail": "employee@company.com"
}
```

**Response (200):**
```json
{
  "valid": true,
  "hrid": "hr_user_456",
  "message": "User promoted to manager successfully",
  "user": {
    "id": 5,
    "email": "employee@company.com",
    "role": "manager",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### 4.3 Check Code Status
```http
GET /manager_codes/becameManagerCode/PROMO2025Q1
X-Internal-Key: nexus-internal-secret-key-123
```

#### 4.4 List HR's Codes
```http
GET /manager_codes/becameManagerCode?hrid=hr_user_456
X-Internal-Key: nexus-internal-secret-key-123
```

---

## 🔄 Response Handling

### Success Responses

**Standard Success (200):**
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { /* result */ }
}
```

**Resource Created (201):**
```json
{
  "id": 1,
  "email": "user@company.com",
  /* resource data */
}
```

### Error Responses

**Missing Field (422):**
```json
{
  "error": "Missing required field: email"
}
```

**Not Found (404):**
```json
{
  "error": "User not found"
}
```

**Conflict (409):**
```json
{
  "error": "Email or UserID already exists"
}
```

**Unauthorized (401):**
```json
{
  "error": "Unauthorized"
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Onboard New Employee

```python
import requests

BASE_URL = "http://localhost:5001"
HEADERS = {
    "X-Internal-Key": "nexus-internal-secret-key-123",
    "Content-Type": "application/json"
}

# Step 1: Create user
user_data = {
    "email": "newemployee@company.com",
    "userID": "auth0_newuser",
    "role": "employee",
    "first_name": "Alice",
    "last_name": "Johnson",
    "department": "Sales"
}
response = requests.post(f"{BASE_URL}/users/", headers=HEADERS, json=user_data)
user = response.json()
print(f"User created: {user['email']}")

# Step 2: Manager creates welcome meeting
meeting_data = {
    "title": "Welcome Meeting",
    "created_by": "manager@company.com",
    "invited_employees": ["newemployee@company.com"],
    "description": "Onboarding session"
}
response = requests.post(f"{BASE_URL}/meetings/", headers=HEADERS, json=meeting_data)
meeting = response.json()
print(f"Meeting created: {meeting['invitation_link']}")
```

---

### Use Case 2: Schedule and Log Team Meeting

```python
# Step 1: Create meeting
meeting_data = {
    "title": "Sprint Planning",
    "created_by": "manager@company.com",
    "invited_employees": [
        "dev1@company.com",
        "dev2@company.com",
        "dev3@company.com"
    ]
}
response = requests.post(f"{BASE_URL}/meetings/", headers=HEADERS, json=meeting_data)
meeting = response.json()
meeting_id = meeting['meeting_id']

# Step 2: Start meeting
requests.post(f"{BASE_URL}/meetings/{meeting_id}/start", headers=HEADERS)

# Step 3: Log activities
log_entries = [
    "Meeting started with 5 participants",
    "Reviewed last sprint achievements",
    "Planned upcoming sprint tasks",
    "Assigned tasks to team members"
]

for entry in log_entries:
    requests.post(
        f"{BASE_URL}/meetings/{meeting_id}/log",
        headers=HEADERS,
        json={"log_entry": entry}
    )

# Step 4: End meeting
requests.post(f"{BASE_URL}/meetings/{meeting_id}/end", headers=HEADERS)

# Step 5: Download log
response = requests.get(
    f"{BASE_URL}/meetings/{meeting_id}/log?download=true",
    headers=HEADERS
)
with open(f"meeting_{meeting_id}_log.txt", "wb") as f:
    f.write(response.content)
```

---

### Use Case 3: Promote Employee to Manager

```python
# Step 1: HR creates promotion code
code_data = {
    "hrid": "hr_director_123",
    "code": "PROMOTE_ALICE_2025",
    "max_uses": 1
}
response = requests.post(
    f"{BASE_URL}/manager_codes/becameManagerCode",
    headers=HEADERS,
    json=code_data
)
code = response.json()
print(f"Promotion code created: {code['data']['code']}")

# Step 2: Use the code to promote employee
promotion_data = {
    "code": "PROMOTE_ALICE_2025",
    "userMail": "alice@company.com"
}
response = requests.post(
    f"{BASE_URL}/manager_codes/validateBecameManagerCode",
    headers=HEADERS,
    json=promotion_data
)
result = response.json()
if result['valid']:
    print(f"User promoted: {result['user']['email']} is now a {result['user']['role']}")
```

---

## ⚠️ Important Notes

### Data Validation
- **Email**: Must be unique and valid format
- **UserID**: Must be unique (from Auth0)
- **Role**: Must be one of: `hr`, `manager`, `employee`, `guest`
- **Date Format**: Use `YYYY-MM-DD` for dates

### Rate Limiting
Currently no rate limiting is implemented. Consider adding:
- Request throttling
- API key quotas
- Per-endpoint limits

### File Uploads
- **Max Size**: 10MB (configurable via `MAX_CONTENT_LENGTH`)
- **Storage**: Files stored in `./storage/files/`
- **Allowed Types**: No restrictions (add validation as needed)

### Meeting Logs
- Logs are stored as text files in `./storage/meeting_logs/`
- Automatically created when meeting is created
- Append-only operations

### Manager Codes
- Single-use by default
- Cannot be reused after `max_uses` reached
- Automatically deactivated after use

---

## 🔍 Testing & Debugging

### Test with cURL
```bash
# Test health
curl http://localhost:5001/health

# Test authentication
curl -H "X-Internal-Key: nexus-internal-secret-key-123" \
  http://localhost:5001/users/

# Test with invalid key (should fail)
curl -H "X-Internal-Key: wrong-key" \
  http://localhost:5001/users/
```

### Run Test Suite
```bash
cd d:\iset\3eme\S1\integration\projet\work\DataBase\masoud\nexus
python verify_api.py
```

### Check Server Logs
Monitor the Flask console for detailed error messages and request logs.

---

## 📞 Support & Resources

### Documentation Files
1. **[COMPLETE_API_DOCUMENTATION.md](COMPLETE_API_DOCUMENTATION.md)** - Comprehensive reference
2. **[API_ENDPOINTS_SUMMARY.md](API_ENDPOINTS_SUMMARY.md)** - Quick endpoint list
3. **[QUICK_START.md](QUICK_START.md)** - Getting started guide
4. **[MANAGER_CODE_API.md](MANAGER_CODE_API.md)** - Manager promotion details
5. **[MEETINGS_API.md](MEETINGS_API.md)** - Meeting system details

### Quick Reference Table

| Resource | Endpoint Pattern | Methods |
|----------|-----------------|---------|
| Users | `/users/` | POST, GET, PUT |
| Meetings | `/meetings/` | POST, GET, PUT, DELETE |
| Files | `/file/` | POST, GET |
| Manager Codes | `/manager_codes/` | POST, GET |
| Health | `/health` | GET |

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Change `INTERNAL_API_KEY` to a secure value
- [ ] Set `DEBUG=False` in configuration
- [ ] Configure proper database credentials
- [ ] Set up HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Set up monitoring/alerts
- [ ] Configure backup strategy
- [ ] Add file upload validation
- [ ] Review CORS settings
- [ ] Set up CI/CD pipeline

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**API Version:** 1.0
