# Teammates API - Documentation for Server Team

## Overview

The Teammates API allows employees to discover their coworkers who share the same manager. This is useful for team collaboration features, chat systems, team dashboards, and social features within the application.

---

## Endpoints

### 1. Get Teammates (Simple)

**Endpoint:** `GET /users/<email>/teammates`

**Description:** Returns all teammates of an employee (other employees under the same manager, excluding the requesting employee).

**Authentication:** Required via `X-Internal-Key` header

**URL Parameters:**
- `email` (string, required) - The email address of the employee

**Query Parameters:**
- `include_details` (boolean, optional, default: false) - If `true`, returns full user objects instead of just email addresses
- `include_manager` (boolean, optional, default: false) - If `true`, includes manager information in the response

---

### 2. Get Full Team

**Endpoint:** `GET /users/<email>/team`

**Description:** Returns complete team information including the employee, their manager, and all teammates with full details.

**Authentication:** Required via `X-Internal-Key` header

**URL Parameters:**
- `email` (string, required) - The email address of the employee

---

## Use Cases

### Use Case 1: Display Teammate List
An employee wants to see who else is on their team.

### Use Case 2: Team Chat/Messaging
Populate a list of team members for messaging features.

### Use Case 3: Team Dashboard
Show team composition and structure.

### Use Case 4: Collaboration Features
Enable team-based features like shared documents, projects, etc.

---

## Request Examples

### Example 1: Basic Teammates List (Emails Only)

**Request:**
```bash
curl -X GET "http://localhost:5001/users/alice@company.com/teammates" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "success": true,
  "employee": "alice@company.com",
  "teammates": [
    "bob@company.com",
    "charlie@company.com",
    "diana@company.com"
  ],
  "teammates_count": 3
}
```

---

### Example 2: Teammates with Full Details

**Request:**
```bash
curl -X GET "http://localhost:5001/users/alice@company.com/teammates?include_details=true" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "success": true,
  "employee": "alice@company.com",
  "teammates": [
    {
      "id": 2,
      "email": "bob@company.com",
      "userID": "auth0_bob_123",
      "first_name": "Bob",
      "last_name": "Smith",
      "role": "employee",
      "department": "Engineering",
      "address": null,
      "date_of_birth": null,
      "employeesList": [],
      "created_at": "2025-12-01T10:00:00Z"
    },
    {
      "id": 3,
      "email": "charlie@company.com",
      "userID": "auth0_charlie_456",
      "first_name": "Charlie",
      "last_name": "Johnson",
      "role": "employee",
      "department": "Engineering",
      "address": "123 Main St",
      "date_of_birth": "1990-05-15",
      "employeesList": [],
      "created_at": "2025-12-02T11:30:00Z"
    },
    {
      "id": 4,
      "email": "diana@company.com",
      "userID": "auth0_diana_789",
      "first_name": "Diana",
      "last_name": "Williams",
      "role": "employee",
      "department": "Engineering",
      "address": null,
      "date_of_birth": null,
      "employeesList": [],
      "created_at": "2025-12-03T09:15:00Z"
    }
  ],
  "teammates_count": 3
}
```

---

### Example 3: Teammates with Manager Information

**Request:**
```bash
curl -X GET "http://localhost:5001/users/alice@company.com/teammates?include_manager=true" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "success": true,
  "employee": "alice@company.com",
  "manager": {
    "email": "manager@company.com",
    "first_name": "John",
    "last_name": "Manager",
    "department": "Engineering"
  },
  "teammates": [
    "bob@company.com",
    "charlie@company.com",
    "diana@company.com"
  ],
  "teammates_count": 3
}
```

---

### Example 4: Teammates with Both Details and Manager

**Request:**
```bash
curl -X GET "http://localhost:5001/users/alice@company.com/teammates?include_details=true&include_manager=true" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "success": true,
  "employee": "alice@company.com",
  "manager": {
    "email": "manager@company.com",
    "first_name": "John",
    "last_name": "Manager",
    "department": "Engineering"
  },
  "teammates": [
    {
      "id": 2,
      "email": "bob@company.com",
      "first_name": "Bob",
      "last_name": "Smith",
      "role": "employee",
      "department": "Engineering"
    },
    {
      "id": 3,
      "email": "charlie@company.com",
      "first_name": "Charlie",
      "last_name": "Johnson",
      "role": "employee",
      "department": "Engineering"
    }
  ],
  "teammates_count": 2
}
```

---

### Example 5: Get Full Team Information

**Request:**
```bash
curl -X GET "http://localhost:5001/users/alice@company.com/team" \
  -H "X-Internal-Key: nexus-internal-secret-key-123" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "success": true,
  "employee": {
    "id": 1,
    "email": "alice@company.com",
    "userID": "auth0_alice_123",
    "first_name": "Alice",
    "last_name": "Johnson",
    "role": "employee",
    "department": "Engineering",
    "address": "456 Oak Ave",
    "date_of_birth": "1992-03-20",
    "employeesList": [],
    "created_at": "2025-12-01T08:00:00Z"
  },
  "manager": {
    "email": "manager@company.com",
    "userID": "auth0_manager_999",
    "first_name": "John",
    "last_name": "Manager",
    "department": "Engineering",
    "role": "manager"
  },
  "teammates": [
    {
      "id": 2,
      "email": "bob@company.com",
      "userID": "auth0_bob_123",
      "first_name": "Bob",
      "last_name": "Smith",
      "role": "employee",
      "department": "Engineering"
    },
    {
      "id": 3,
      "email": "charlie@company.com",
      "userID": "auth0_charlie_456",
      "first_name": "Charlie",
      "last_name": "Johnson",
      "role": "employee",
      "department": "Engineering"
    }
  ],
  "team_size": 3
}
```

---

## Error Responses

### Employee Not Found (404)

**Request:**
```bash
curl -X GET "http://localhost:5001/users/nonexistent@company.com/teammates" \
  -H "X-Internal-Key: nexus-internal-secret-key-123"
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Employee not found"
}
```

---

### No Manager Found (200)

When an employee has no manager assigned (not in any manager's employees_list):

**Response (200 OK):**
```json
{
  "success": true,
  "employee": "alice@company.com",
  "message": "No manager found for this employee",
  "manager": null,
  "teammates": [],
  "teammates_count": 0
}
```

---

### Unauthorized (401)

Missing or invalid API key:

**Response (401 Unauthorized):**
```json
{
  "error": "Unauthorized"
}
```

---

## Code Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:5001"
API_KEY = "nexus-internal-secret-key-123"

def get_teammates(employee_email, include_details=False, include_manager=False):
    """Get teammates of an employee."""
    url = f"{BASE_URL}/users/{employee_email}/teammates"
    headers = {
        "X-Internal-Key": API_KEY,
        "Content-Type": "application/json"
    }
    params = {
        "include_details": str(include_details).lower(),
        "include_manager": str(include_manager).lower()
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def get_full_team(employee_email):
    """Get full team information."""
    url = f"{BASE_URL}/users/{employee_email}/team"
    headers = {
        "X-Internal-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

# Usage examples
if __name__ == "__main__":
    # Get simple list of teammate emails
    teammates = get_teammates("alice@company.com")
    print("Teammates:", teammates['teammates'])
    
    # Get teammates with full details
    teammates_detailed = get_teammates(
        "alice@company.com",
        include_details=True,
        include_manager=True
    )
    print("Manager:", teammates_detailed.get('manager'))
    print("Number of teammates:", teammates_detailed['teammates_count'])
    
    # Get full team info
    team = get_full_team("alice@company.com")
    print(f"Team size: {team['team_size']}")
    print(f"Manager: {team['manager']['first_name']} {team['manager']['last_name']}")
```

---

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5001';
const API_KEY = 'nexus-internal-secret-key-123';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'X-Internal-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

// Get teammates (simple)
async function getTeammates(employeeEmail, includeDetails = false, includeManager = false) {
  try {
    const response = await api.get(`/users/${employeeEmail}/teammates`, {
      params: {
        include_details: includeDetails,
        include_manager: includeManager
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching teammates:', error.response?.data || error.message);
    throw error;
  }
}

// Get full team
async function getFullTeam(employeeEmail) {
  try {
    const response = await api.get(`/users/${employeeEmail}/team`);
    return response.data;
  } catch (error) {
    console.error('Error fetching team:', error.response?.data || error.message);
    throw error;
  }
}

// Usage examples
(async () => {
  try {
    // Get simple teammate list
    const teammates = await getTeammates('alice@company.com');
    console.log('Teammates:', teammates.teammates);
    
    // Get teammates with details and manager
    const detailedTeammates = await getTeammates('alice@company.com', true, true);
    console.log('Manager:', detailedTeammates.manager);
    console.log('Teammates count:', detailedTeammates.teammates_count);
    
    // Get full team info
    const team = await getFullTeam('alice@company.com');
    console.log(`Team size: ${team.team_size}`);
    console.log(`Manager: ${team.manager.first_name} ${team.manager.last_name}`);
  } catch (error) {
    console.error('Error:', error);
  }
})();
```

---

### React Hook Example

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5001';
const API_KEY = 'nexus-internal-secret-key-123';

// Custom hook for teammates
export function useTeammates(employeeEmail, options = {}) {
  const [teammates, setTeammates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const { includeDetails = false, includeManager = false } = options;
  
  useEffect(() => {
    const fetchTeammates = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `${API_BASE}/users/${employeeEmail}/teammates`,
          {
            headers: { 'X-Internal-Key': API_KEY },
            params: {
              include_details: includeDetails,
              include_manager: includeManager
            }
          }
        );
        setTeammates(response.data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to fetch teammates');
      } finally {
        setLoading(false);
      }
    };
    
    if (employeeEmail) {
      fetchTeammates();
    }
  }, [employeeEmail, includeDetails, includeManager]);
  
  return { teammates, loading, error };
}

// Usage in component
function TeammatesDisplay({ userEmail }) {
  const { teammates, loading, error } = useTeammates(userEmail, {
    includeDetails: true,
    includeManager: true
  });
  
  if (loading) return <div>Loading teammates...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      <h3>Your Teammates</h3>
      {teammates.manager && (
        <div>
          <h4>Manager: {teammates.manager.first_name} {teammates.manager.last_name}</h4>
        </div>
      )}
      <ul>
        {teammates.teammates.map(teammate => (
          <li key={teammate.email}>
            {teammate.first_name} {teammate.last_name} ({teammate.email})
          </li>
        ))}
      </ul>
      <p>Total teammates: {teammates.teammates_count}</p>
    </div>
  );
}
```

---

## Response Fields Reference

### Teammates Endpoint Response

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `employee` | string | Email of the employee who made the request |
| `teammates` | array | List of teammates (emails or objects depending on `include_details`) |
| `teammates_count` | integer | Number of teammates found |
| `manager` | object/null | Manager information (only if `include_manager=true`) |
| `message` | string | Additional message (only in special cases like no manager) |

### Full Team Endpoint Response

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `employee` | object | Full user object of the requesting employee |
| `manager` | object/null | Manager information with key fields |
| `teammates` | array | Array of full user objects for each teammate |
| `team_size` | integer | Total team size (including the employee) |
| `message` | string | Additional message (only if no manager found) |

---

## Query Parameters Details

### `include_details` Parameter

- **Type:** Boolean (accepts `true`, `false`, `1`, `0`)
- **Default:** `false`
- **Effect:**
  - `false`: Returns array of email strings
  - `true`: Returns array of full user objects

**Example:**
```bash
# Without details
?include_details=false
# Returns: ["bob@company.com", "charlie@company.com"]

# With details
?include_details=true
# Returns: [{"id": 2, "email": "bob@company.com", ...}, {...}]
```

### `include_manager` Parameter

- **Type:** Boolean (accepts `true`, `false`, `1`, `0`)
- **Default:** `false`
- **Effect:**
  - `false`: Manager field not included in response
  - `true`: Adds `manager` field to response

---

## Business Logic

### How the System Finds Teammates

1. **Lookup Employee:** System finds the user record by email
2. **Find Manager:** Searches for any manager(s) whose `employees_list` contains the employee's email
3. **Extract Teammates:** Gets all emails from the manager's `employees_list`
4. **Filter Self:** Removes the requesting employee's email from the list
5. **Enrich Data:** If `include_details=true`, fetches full user objects for each teammate
6. **Return Response:** Returns the formatted response

### Edge Cases Handled

- **No Manager:** Employee not assigned to any manager → Returns empty teammates list
- **Multiple Managers:** Employee in multiple managers' lists → Returns combined unique teammates
- **Empty Team:** Employee is the only one in manager's list → Returns empty teammates list
- **Non-existent Employee:** Returns 404 error

---

## Performance Considerations

### Database Queries

- **Basic Request:** 1-2 queries (find employee, find manager)
- **With Details:** +1 query (fetch teammate details)
- **With Multiple Managers:** Queries scale with number of managers

### Optimization Tips

1. **Use Simple Mode:** If you only need emails, don't use `include_details=true`
2. **Cache Results:** Consider caching teammate lists for frequently accessed teams
3. **Batch Requests:** If fetching for multiple users, consider implementing a batch endpoint

---

## Integration Checklist

- [ ] Obtain API key from server team
- [ ] Test with a known employee email
- [ ] Handle 404 errors (employee not found)
- [ ] Handle empty teammates case
- [ ] Implement proper error handling
- [ ] Test with `include_details` parameter
- [ ] Test with `include_manager` parameter
- [ ] Implement caching if needed
- [ ] Add logging for debugging

---

## Troubleshooting

### Issue: Getting Empty Teammates List

**Possible Causes:**
1. Employee not assigned to any manager
2. Employee is the only one on the team
3. Manager's `employees_list` is empty

**Solution:**
- Check if employee is in any manager's `employees_list`
- Verify manager has other employees assigned

### Issue: 404 Error

**Cause:** Employee email doesn't exist in the database

**Solution:**
- Verify email is correct
- Check if user has been created in the system

### Issue: Slow Response

**Cause:** Large teams or `include_details=true` with many teammates

**Solution:**
- Implement pagination (feature request)
- Use caching
- Consider using websockets for real-time updates

---

## Future Enhancements

Potential improvements for future versions:

1. **Pagination:** Support for large teams
2. **Filtering:** Filter teammates by role, department, etc.
3. **Sorting:** Sort teammates by name, join date, etc.
4. **Team Hierarchy:** Include indirect reports and multi-level teams
5. **Batch Endpoint:** Get teammates for multiple employees in one request
6. **WebSocket Support:** Real-time team updates

---

## Support

For questions or issues with this API:
- Check the main API documentation: `COMPLETE_API_DOCUMENTATION.md`
- Review error messages in responses
- Enable debug logging in your application

---

**API Version:** 1.0  
**Last Updated:** December 7, 2025  
**Endpoint Base:** `http://localhost:5001/users`
