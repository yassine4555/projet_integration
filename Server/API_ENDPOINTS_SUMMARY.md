# SAVING_SERVER - API Endpoints Summary

**Service:** SAVING_SERVER  
**Base URL:** `http://localhost:5001`  
**Authentication:** API Key via `X-Internal-Key` header  
**API Key:** `nexus-internal-secret-key-123`

---

## Complete Endpoint List

### 🏥 Health & Status

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Service status and DB connection check | No |
| GET | `/health` | Health check with version info | No |

---

### 👥 User Management (`/users`)

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/users/` | Create new user | email, userID, role, first_name, last_name | User object (201) |
| GET | `/users/` | Get all users | - | Array of users (200) |
| PUT/PATCH | `/users/<email>` | Update user by email | Any user fields | Updated user (200) |

**Valid Roles:** `hr`, `manager`, `employee`, `guest`

---

### 🎫 Invite Management (`/invites`)

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/invites/` | Create invitation code | manager_id, code, max_uses | Invite object (201) |

---

### 📁 File Management (`/file`)

| Method | Endpoint | Description | Request Type | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/file/upload` | Upload a file | multipart/form-data | File info (200) |
| GET | `/file/get/<filename>` | Download file | - | File download (200) |
| GET | `/file/getAll` | List all files | Query: user_email (optional) | Array of files (200) |

---

### 📅 Meeting Management (`/meetings`)

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/meetings/` | Create meeting | title, created_by | Meeting object (201) |
| GET | `/meetings/` | List meetings | Query: user_email, is_active | Array of meetings (200) |
| GET | `/meetings/<meeting_id>` | Get meeting details | - | Meeting object (200) |
| PUT | `/meetings/<meeting_id>` | Update meeting | Any meeting fields | Updated meeting (200) |
| POST | `/meetings/<meeting_id>/start` | Start meeting | - | Meeting with start time (200) |
| POST | `/meetings/<meeting_id>/end` | End meeting | - | Meeting with end time (200) |
| POST | `/meetings/<meeting_id>/log` | Append log entry | log_entry | Success message (200) |
| GET | `/meetings/<meeting_id>/log` | Get meeting log | Query: download (true/false) | Log content or file (200) |
| DELETE | `/meetings/<meeting_id>` | Delete meeting (soft) | - | Success message (200) |

---

### 🔑 Manager Promotion Codes (`/manager_codes`)

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/manager_codes/becameManagerCode` | Create promotion code | hrid, code, max_uses | Code object (201) |
| POST | `/manager_codes/validateBecameManagerCode` | Validate & use code | code, userMail | Validation result + promoted user (200) |
| GET | `/manager_codes/becameManagerCode/<code>` | Get code details | - | Code object (200) |
| GET | `/manager_codes/becameManagerCode` | List all codes | Query: hrid, active_only | Array of codes (200) |

---

## Common Request Examples

### Headers for All Requests
```http
X-Internal-Key: nexus-internal-secret-key-123
Content-Type: application/json
```

### Create User
```json
POST /users/
{
  "email": "user@company.com",
  "userID": "auth0_123",
  "role": "employee",
  "first_name": "John",
  "last_name": "Doe",
  "department": "IT"
}
```

### Update User
```json
PUT /users/user@company.com
{
  "department": "Engineering",
  "role": "manager"
}
```

### Create Meeting
```json
POST /meetings/
{
  "title": "Team Standup",
  "created_by": "manager@company.com",
  "invited_employees": ["emp1@company.com", "emp2@company.com"]
}
```

### Upload File (multipart/form-data)
```
POST /file/upload
Fields:
  - file: [binary file data]
  - user_email: "user@company.com"
```

### Create Promotion Code
```json
POST /manager_codes/becameManagerCode
{
  "hrid": "hr_user_123",
  "code": "PROMOTE2025",
  "max_uses": 1
}
```

### Use Promotion Code
```json
POST /manager_codes/validateBecameManagerCode
{
  "code": "PROMOTE2025",
  "userMail": "employee@company.com"
}
```

---

## HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Invalid data (e.g., invalid role) |
| 401 | Unauthorized | Missing/invalid API key |
| 403 | Forbidden | User not authorized for action |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate email, code, etc. |
| 422 | Unprocessable Entity | Missing required fields |
| 500 | Internal Server Error | Server-side error |

---

## Error Response Format

```json
{
  "error": "Description of what went wrong"
}
```

---

## Success Response Format

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* response data */ }
}
```

---

## Query Parameters Reference

### GET /file/getAll
- `user_email` - Filter files by uploader email

### GET /meetings/
- `user_email` - Filter by creator or invited user
- `is_active` - Filter by active status (true/false)

### GET /manager_codes/becameManagerCode
- `hrid` - Filter by HR user ID
- `active_only` - Show only active codes (true/false)

### GET /meetings/<meeting_id>/log
- `download` - Download log file (true/false)

---

## Data Models

### User
```json
{
  "id": 1,
  "email": "user@company.com",
  "userID": "auth0_123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "employee",
  "department": "IT",
  "address": "123 Main St",
  "date_of_birth": "1990-05-15",
  "employeesList": [],
  "created_at": "2025-12-07T10:30:00Z"
}
```

### Meeting
```json
{
  "id": 1,
  "meeting_id": "mtg_abc123",
  "title": "Team Meeting",
  "created_by": "manager@company.com",
  "invitation_link": "http://localhost:5001/join/mtg_abc123",
  "invited_employees_list": ["emp@company.com"],
  "is_active": true,
  "started_at": "2025-12-07T10:00:00Z",
  "ended_at": null,
  "created_at": "2025-12-07T09:00:00Z"
}
```

### File
```json
{
  "id": 1,
  "file_id": "file_abc123",
  "filename": "document.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "uploaded_by": "user@company.com",
  "uploaded_at": "2025-12-07T10:30:00Z"
}
```

### Manager Code
```json
{
  "id": 1,
  "code": "PROMOTE2025",
  "hrid": "hr_user_123",
  "max_uses": 1,
  "used_count": 0,
  "used_by_email": null,
  "is_active": true,
  "created_at": "2025-12-07T10:30:00Z",
  "used_at": null
}
```

---

## Testing

Run the included test suite:
```bash
python verify_api.py
```

---

## Additional Resources

- **Complete Documentation:** `COMPLETE_API_DOCUMENTATION.md`
- **Quick Start Guide:** `QUICK_START.md`
- **Manager Code API:** `MANAGER_CODE_API.md`
- **Meetings API:** `MEETINGS_API.md`

---

**Last Updated:** December 7, 2025  
**Version:** 1.0
