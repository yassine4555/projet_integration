# 🚀 Gateway API Documentation

**Version:** 1.0.0  
**Service:** Gateway (Central API Gateway)  
**Port:** 7050 (HTTPS)  
**Base URL:** `https://localhost:7050`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Environment Variables](#environment-variables)
4. [Authentication](#authentication)
5. [HTTP REST APIs](#http-rest-apis)
6. [WebSocket APIs](#websocket-apis)
7. [Data Models](#data-models)
8. [Error Handling](#error-handling)
9. [Integration Examples](#integration-examples)

---

## 🎯 Overview

The Gateway service acts as a **central API Gateway** that:
- Routes HTTP requests to backend microservices
- Manages WebSocket connections for real-time features (Games & Meetings)
- Handles JWT authentication
- Provides health check endpoints for Kubernetes
- Implements CORS for cross-origin requests

### Key Features
- ✅ JWT-based authentication
- ✅ WebSocket support for real-time communication
- ✅ File upload/download through data service
- ✅ Meeting management (create, join, CRUD operations)
- ✅ Game matching and multiplayer support
- ✅ Health checks for Kubernetes deployments

---

## 🏗️ Architecture

```
┌─────────────────┐
│   UI/Frontend   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Gateway (Port 7050)             │
│  ┌─────────────────────────────────┐   │
│  │   HTTP REST Endpoints           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   WebSocket Namespaces          │   │
│  │   - /game                       │   │
│  │   - /meeting                    │   │
│  └─────────────────────────────────┘   │
└───────┬─────────────┬─────────────┬─────┘
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│ Auth Service │ │  Game    │ │ Meeting  │
│ (Port 7051)  │ │  Service │ │  Service │
└──────────────┘ │(Port7054)│ │(Port7053)│
┌──────────────┐ └──────────┘ └──────────┘
│ User Service │
│ (Port 7052)  │
└──────────────┘
┌──────────────┐
│ Data Service │
│ (Port 7055)  │
└──────────────┘
```

---

## ⚙️ Environment Variables

The Gateway reads configuration from `.env` file:

```bash
AUTH_SERVER="192.168.0.94:7051"          # Authentication service
UserServices_server="192.168.0.94:7052"  # User management service
SAVING_server="192.168.148.94:5001"      # Data saving service
Game_server="http://192.168.100.190:7054" # Game service (WebSocket)
Meet_server="https://192.168.0.94:7053"   # Meeting service (WebSocket)
DATA_SERVICE="192.168.0.94:7055"          # File storage service
```

### Internal Configuration
- **JWT Secret:** `your-super-secret-jwt-token-with-at-least-32-characters-long`
- **CORS:** Enabled for all origins (`*`)
- **SSL/TLS:** Uses certificates from `meetingService/certifs/`

---

## 🔐 Authentication

### JWT Token System

The Gateway uses **JWT (JSON Web Tokens)** for authentication. Most endpoints require a valid JWT token.

#### How to Include JWT in Requests

**HTTP Requests:**
```javascript
headers: {
  'Authorization': 'Bearer <your_jwt_token>',
  'Content-Type': 'application/json'
}
```

**WebSocket Connections:**
```javascript
// JWT should be sent during connection or in handshake
const socket = io('https://localhost:7050/meeting', {
  auth: {
    token: 'your_jwt_token'
  }
});
```

#### Getting a JWT Token

1. **Login** to get a token (see [Login API](#1-login))
2. **Signup** to create account and get token (see [Signup API](#2-signup))
3. Store the token securely (localStorage, sessionStorage, or secure cookie)

---

## 📡 HTTP REST APIs

### Health & Monitoring Endpoints

#### 1. Health Check (Kubernetes)
**Endpoint:** `GET /health`  
**Authentication:** ❌ Not Required  
**Description:** Kubernetes health check with downstream service status

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:7050
X-Health-Check: readiness  # Optional: 'readiness' for detailed check
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "gateway",
  "version": "1.0.0",
  "timestamp": "2025-11-30T12:34:56.789Z",
  "pod_name": "gateway-pod-xyz",
  "pod_ip": "10.0.1.23",
  "downstream_services": {
    "auth-service": {
      "status": "healthy",
      "response_time": 0.045
    },
    "user-service": {
      "status": "healthy",
      "response_time": 0.038
    },
    "saving-service": {
      "status": "unhealthy",
      "error": "Connection refused"
    }
  }
}
```

**Response Codes:**
- `200` - All services healthy
- `503` - Some services degraded/unhealthy

---

#### 2. Readiness Check
**Endpoint:** `GET /ready`  
**Authentication:** ❌ Not Required  

**Response:**
```json
{
  "status": "ready"
}
```

---

#### 3. Liveness Check
**Endpoint:** `GET /live`  
**Authentication:** ❌ Not Required  

**Response:**
```json
{
  "status": "alive"
}
```

---

#### 4. Metrics (Prometheus)
**Endpoint:** `GET /metrics`  
**Authentication:** ❌ Not Required  
**Content-Type:** `text/plain`

**Response:**
```
# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total 0
```

---

### Authentication Endpoints

#### 1. Login
**Endpoint:** `POST /login`  
**Authentication:** ❌ Not Required  
**Description:** Authenticate user and receive JWT token

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id": "user_id_12345",
  "email": "user@example.com",
  "role": "EMPLOYER"
}
```

**Response Codes:**
- `200` - Login successful
- `401` - Missing credentials or invalid credentials
- `500` - Server error

**UI Integration Example:**
```javascript
async function login(email, password) {
  const response = await fetch('https://localhost:7050/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Store token for future requests
    localStorage.setItem('jwt_token', data.Token);
    localStorage.setItem('user_id', data.id);
    return data;
  } else {
    throw new Error('Login failed');
  }
}
```

---

#### 2. Signup
**Endpoint:** `POST /signup`  
**Authentication:** ❌ Not Required  
**Description:** Create new user account

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "Password": "SecurePassword123!",
  "FirstName": "John",
  "LastName": "Doe",
  "DateOfBirth": "1990-01-15",
  "Address": "123 Main Street, City",
  "managercode": "MNGR-12345"  // Optional: for employee registration
}
```

**Response (200 OK):**
```json
{
  "AuthToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "id": "user_id_67890"
}
```

**Response Codes:**
- `200` - Signup successful
- `400` - Missing required fields
- `500` - Error from auth service

**Required Fields:**
- ✅ `email`
- ✅ `Password`
- ✅ `FirstName`
- ✅ `LastName`
- ✅ `DateOfBirth`
- ✅ `Address`
- ⚠️ `managercode` (optional)

**UI Integration Example:**
```javascript
async function signup(userData) {
  const response = await fetch('https://localhost:7050/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });
  
  const data = await response.json();
  
  if (response.ok) {
    localStorage.setItem('jwt_token', data.AuthToken);
    localStorage.setItem('user_id', data.id);
    return data;
  } else {
    throw new Error(data.error || 'Signup failed');
  }
}
```

---

#### 3. Get Manager Code
**Endpoint:** `POST /getCodeForManager`  
**Authentication:** ✅ Required (JWT)  
**Description:** Get manager code for employee registration

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "managermail": "manager@company.com"
}
```

**Response (200 OK):**
```json
{
  "code": "MNGR-12345",
  "manager_email": "manager@company.com",
  "valid_until": "2025-12-31T23:59:59Z"
}
```

**Response Codes:**
- `200` - Code retrieved successfully
- `400` - Manager email required
- `503` - Service communication error
- `500` - Internal error

---

### Meeting Management Endpoints

#### 1. Create Meeting
**Endpoint:** `POST /create-meet`  
**Authentication:** ✅ Required (JWT)  
**Description:** Create a new meeting room

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Team Standup",
  "description": "Daily standup meeting",
  "creator_email": "user@example.com",
  "invited_employees": [
    "employee1@example.com",
    "employee2@example.com"
  ]
}
```

**Response (200 OK):**
```json
{
  "meeting_id": "meet_abc123xyz",
  "invitation_link": "https://localhost:7050/room/meet_abc123xyz/user@example.com",
  "created_at": "2025-11-30T12:00:00Z",
  "status": "created"
}
```

**Response Codes:**
- `200` - Meeting created successfully
- `500` - Gateway error

---

#### 2. Join Meeting
**Endpoint:** `POST /join-meet`  
**Authentication:** ❌ Not Required  
**Description:** Join an existing meeting

**Request Body:**
```json
{
  "meeting_id": "meet_abc123xyz",
  "user_email": "participant@example.com"
}
```

**Response (200 OK):**
```json
{
  "redirectUrl": "https://localhost:7050/room/meet_abc123xyz/participant@example.com",
  "meeting_id": "meet_abc123xyz",
  "status": "success"
}
```

**UI Integration:**
```javascript
async function joinMeeting(meetingId, userEmail) {
  const response = await fetch('https://localhost:7050/join-meet', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      meeting_id: meetingId,
      user_email: userEmail
    })
  });
  
  const data = await response.json();
  
  if (response.ok && data.redirectUrl) {
    // Redirect to meeting room
    window.location.href = data.redirectUrl;
  }
}
```

---

#### 3. Get Meeting Room Page
**Endpoint:** `GET /room/<meeting_id>/<user_email>`  
**Authentication:** ❌ Not Required  
**Description:** Get HTML page for meeting room

**Example:**
```
GET /room/meet_abc123xyz/user@example.com
```

**Response:** HTML page with WebRTC interface

---

#### 4. Get All Meetings
**Endpoint:** `GET /meetings`  
**Authentication:** ✅ Required (JWT)  
**Description:** Get list of all meetings (with optional filters)

**Query Parameters:**
- `user_email` (optional): Filter by user email
- `is_active` (optional): Filter by active status (`true`/`false`)

**Request:**
```http
GET /meetings?user_email=user@example.com&is_active=true HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "meetings": [
    {
      "ID": "meet_abc123",
      "Title": "Team Standup",
      "Object": "Daily sync",
      "InvitationLink": "https://localhost:7050/room/meet_abc123/...",
      "Description": "Daily standup meeting",
      "Creator": "manager@example.com",
      "InvitedEmployeesList": ["emp1@example.com", "emp2@example.com"],
      "is_active": true,
      "created_at": "2025-11-30T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

#### 5. Get Meeting by ID
**Endpoint:** `GET /meetings/<meeting_id>`  
**Authentication:** ✅ Required (JWT)  
**Description:** Get details of a specific meeting

**Request:**
```http
GET /meetings/meet_abc123 HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "ID": "meet_abc123",
  "Title": "Team Standup",
  "Object": "Daily sync",
  "InvitationLink": "https://localhost:7050/room/meet_abc123/...",
  "LogPath": "/logs/meet_abc123.log",
  "Description": "Daily standup meeting",
  "Creator": "manager@example.com",
  "InvitedEmployeesList": ["emp1@example.com", "emp2@example.com"],
  "is_active": true,
  "started_at": "2025-11-30T10:05:00Z",
  "ended_at": null
}
```

---

#### 6. Update Meeting
**Endpoint:** `PUT /meetings/<meeting_id>`  
**Authentication:** ✅ Required (JWT)  
**Description:** Update meeting details

**Request Body:**
```json
{
  "Title": "Updated Team Meeting",
  "Description": "Updated description",
  "InvitedEmployeesList": [
    "emp1@example.com",
    "emp2@example.com",
    "emp3@example.com"
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Meeting updated successfully",
  "meeting_id": "meet_abc123"
}
```

---

#### 7. Delete Meeting
**Endpoint:** `DELETE /meetings/<meeting_id>`  
**Authentication:** ✅ Required (JWT)  
**Description:** Delete a meeting

**Request:**
```http
DELETE /meetings/meet_abc123 HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "Meeting deleted successfully",
  "meeting_id": "meet_abc123"
}
```

---

#### 8. Start Meeting
**Endpoint:** `POST /meetings/<meeting_id>/start`  
**Authentication:** ✅ Required (JWT)  
**Description:** Mark meeting as started

**Response (200 OK):**
```json
{
  "message": "Meeting started",
  "meeting_id": "meet_abc123",
  "started_at": "2025-11-30T10:05:00Z"
}
```

---

#### 9. End Meeting
**Endpoint:** `POST /meetings/<meeting_id>/end`  
**Authentication:** ✅ Required (JWT)  
**Description:** Mark meeting as ended

**Response (200 OK):**
```json
{
  "message": "Meeting ended",
  "meeting_id": "meet_abc123",
  "ended_at": "2025-11-30T11:00:00Z",
  "duration_minutes": 55
}
```

---

#### 10. Add Meeting Log Entry
**Endpoint:** `POST /meetings/<meeting_id>/log`  
**Authentication:** ✅ Required (JWT)  
**Description:** Add a log entry to meeting

**Request Body:**
```json
{
  "action": "participant_joined",
  "user_email": "user@example.com",
  "timestamp": "2025-11-30T10:06:00Z",
  "details": "User joined the meeting"
}
```

**Response (200 OK):**
```json
{
  "message": "Log entry added",
  "meeting_id": "meet_abc123"
}
```

---

#### 11. Get Meeting Log
**Endpoint:** `GET /meetings/<meeting_id>/log`  
**Authentication:** ✅ Required (JWT)  
**Description:** Get meeting log entries

**Query Parameters:**
- `download` (optional): Set to `true` to download as file

**Request:**
```http
GET /meetings/meet_abc123/log HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "meeting_id": "meet_abc123",
  "log_entries": [
    {
      "timestamp": "2025-11-30T10:05:00Z",
      "action": "meeting_started",
      "user_email": "manager@example.com"
    },
    {
      "timestamp": "2025-11-30T10:06:00Z",
      "action": "participant_joined",
      "user_email": "user@example.com"
    }
  ]
}
```

**Download Log:**
```http
GET /meetings/meet_abc123/log?download=true HTTP/1.1
Authorization: Bearer <jwt_token>
```
Returns file download with log content.

---

### File Management Endpoints

#### 1. Upload File
**Endpoint:** `POST /upload`  
**Authentication:** ⚠️ Currently Disabled (for testing)  
**Description:** Upload a file to data service

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** Form data with file field

**Request Example (JavaScript):**
```javascript
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('https://localhost:7050/upload', {
    method: 'POST',
    // headers: {
    //   'Authorization': 'Bearer ' + token  // Add when JWT enabled
    // },
    body: formData
  });
  
  return await response.json();
}
```

**cURL Example:**
```bash
curl -X POST https://localhost:7050/upload \
  -F "file=@/path/to/file.pdf"
```

**Response (200 OK):**
```json
{
  "message": "File uploaded successfully",
  "filename": "document.pdf",
  "file_id": "file_xyz789",
  "size": 1048576,
  "uploaded_by": "test@example.com",
  "uploaded_at": "2025-11-30T12:00:00Z"
}
```

**Response Codes:**
- `200` - File uploaded successfully
- `400` - No file provided or empty filename
- `503` - Cannot connect to data service
- `504` - Data service timeout
- `500` - Gateway error

---

#### 2. Get All Files
**Endpoint:** `GET /getAllfiles`  
**Authentication:** ⚠️ Currently Disabled (for testing)  
**Description:** Get list of all uploaded files

**Request:**
```http
GET /getAllfiles HTTP/1.1
Host: localhost:7050
```

**Response (200 OK):**
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "file_id": "file_xyz789",
      "size": 1048576,
      "uploaded_by": "user@example.com",
      "uploaded_at": "2025-11-30T12:00:00Z",
      "mime_type": "application/pdf"
    },
    {
      "filename": "image.png",
      "file_id": "file_abc456",
      "size": 524288,
      "uploaded_by": "user@example.com",
      "uploaded_at": "2025-11-29T15:30:00Z",
      "mime_type": "image/png"
    }
  ],
  "total": 2
}
```

**UI Integration:**
```javascript
async function getAllFiles() {
  const response = await fetch('https://localhost:7050/getAllfiles', {
    method: 'GET',
    // headers: {
    //   'Authorization': 'Bearer ' + token  // Add when JWT enabled
    // }
  });
  
  const data = await response.json();
  return data.files;
}
```

---

#### 3. Get/Download File
**Endpoint:** `GET /file/get/<filename>`  
**Authentication:** ⚠️ Currently Disabled (for testing)  
**Description:** Download a specific file

**Request:**
```http
GET /file/get/document.pdf HTTP/1.1
Host: localhost:7050
```

**Response (200 OK):**
- File download with appropriate `Content-Type` header
- `Content-Disposition: attachment; filename="document.pdf"`

**Response Codes:**
- `200` - File retrieved successfully
- `404` - File not found
- `500` - Gateway error

**UI Integration:**
```javascript
async function downloadFile(filename) {
  const response = await fetch(`https://localhost:7050/file/get/${filename}`, {
    method: 'GET'
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
}
```

---

## 🔌 WebSocket APIs

The Gateway provides two WebSocket namespaces for real-time communication:

### Connection URL Format
```
wss://localhost:7050/<namespace>
```

### Namespaces
1. **`/game`** - Game matching and multiplayer gaming
2. **`/meeting`** - Video conferencing and WebRTC signaling

---

### 🎮 Game Namespace (`/game`)

**Connection URL:** `wss://localhost:7050/game`

#### Connection Example
```javascript
import io from 'socket.io-client';

const gameSocket = io('https://localhost:7050/game', {
  transports: ['websocket'],
  secure: true,
  rejectUnauthorized: false  // For self-signed certificates
});

gameSocket.on('connect', () => {
  console.log('Connected to game server');
  console.log('Socket ID:', gameSocket.id);
});
```

---

#### Events from Client to Server

##### 1. `createMatch`
**Description:** Create a new game match  
**Payload:** None

**Example:**
```javascript
gameSocket.emit('createMatch');
```

**Server Response:** Triggers `matchCreated` event

---

##### 2. `joinMatch`
**Description:** Join an existing match using match code  
**Payload:** `match_code` (string)

**Example:**
```javascript
const matchCode = 'ABCD1234';
gameSocket.emit('joinMatch', matchCode);
```

**Server Response:** Triggers `matchJoined` event

---

##### 3. `makeMove`
**Description:** Make a move in the game  
**Payload:** Object with move data

**Example:**
```javascript
gameSocket.emit('makeMove', {
  position: 5,      // Board position (0-8 for tic-tac-toe)
  player: 'X',
  timestamp: Date.now()
});
```

**Server Response:** Triggers `gameState` event

---

##### 4. `restartGame`
**Description:** Request to restart the game  
**Payload:** `match_code` (string)

**Example:**
```javascript
gameSocket.emit('restartGame', matchCode);
```

**Server Response:** Triggers `gameState` event with new game state

---

#### Events from Server to Client

##### 1. `matchCreated`
**Description:** Match successfully created  
**Payload:**
```json
{
  "matchCode": "ABCD1234",
  "creatorId": "socket_id_xyz",
  "status": "waiting",
  "created_at": "2025-11-30T12:00:00Z"
}
```

**Example:**
```javascript
gameSocket.on('matchCreated', (data) => {
  console.log('Match created:', data.matchCode);
  // Display match code to user for sharing
  displayMatchCode(data.matchCode);
});
```

---

##### 2. `matchJoined`
**Description:** Successfully joined a match  
**Payload:**
```json
{
  "matchCode": "ABCD1234",
  "players": [
    {
      "id": "socket_id_1",
      "symbol": "X",
      "name": "Player 1"
    },
    {
      "id": "socket_id_2",
      "symbol": "O",
      "name": "Player 2"
    }
  ],
  "status": "ready",
  "yourSymbol": "O"
}
```

**Example:**
```javascript
gameSocket.on('matchJoined', (data) => {
  console.log('Joined match:', data.matchCode);
  console.log('You are playing as:', data.yourSymbol);
  startGame(data);
});
```

---

##### 3. `gameState`
**Description:** Current game state update  
**Payload:**
```json
{
  "matchCode": "ABCD1234",
  "board": ["X", "", "O", "X", "O", "", "", "X", ""],
  "currentPlayer": "X",
  "winner": null,
  "gameOver": false,
  "lastMove": {
    "position": 7,
    "player": "X"
  }
}
```

**Example:**
```javascript
gameSocket.on('gameState', (data) => {
  updateGameBoard(data.board);
  
  if (data.gameOver) {
    if (data.winner) {
      showMessage(`${data.winner} wins!`);
    } else {
      showMessage('Draw!');
    }
  } else {
    showMessage(`Current turn: ${data.currentPlayer}`);
  }
});
```

---

##### 4. `error`
**Description:** Error occurred  
**Payload:**
```json
{
  "message": "Match not found",
  "code": "MATCH_NOT_FOUND"
}
```

**Example:**
```javascript
gameSocket.on('error', (data) => {
  console.error('Game error:', data.message);
  alert('Error: ' + data.message);
});
```

---

#### Complete Game Flow Example

```javascript
class TicTacToeGame {
  constructor() {
    this.socket = io('https://localhost:7050/game', {
      transports: ['websocket'],
      secure: true
    });
    
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    this.socket.on('connect', () => {
      console.log('Connected to game server');
    });
    
    this.socket.on('matchCreated', (data) => {
      this.matchCode = data.matchCode;
      this.showMatchCode(data.matchCode);
    });
    
    this.socket.on('matchJoined', (data) => {
      this.mySymbol = data.yourSymbol;
      this.startGame(data);
    });
    
    this.socket.on('gameState', (data) => {
      this.updateBoard(data);
      
      if (data.gameOver) {
        this.endGame(data);
      }
    });
    
    this.socket.on('error', (data) => {
      alert('Error: ' + data.message);
    });
  }
  
  createMatch() {
    this.socket.emit('createMatch');
  }
  
  joinMatch(code) {
    this.socket.emit('joinMatch', code);
  }
  
  makeMove(position) {
    this.socket.emit('makeMove', {
      position: position,
      player: this.mySymbol
    });
  }
  
  restartGame() {
    this.socket.emit('restartGame', this.matchCode);
  }
  
  updateBoard(gameState) {
    // Update UI with game state
    gameState.board.forEach((cell, index) => {
      document.getElementById(`cell-${index}`).textContent = cell;
    });
  }
}
```

---

### 🎥 Meeting Namespace (`/meeting`)

**Connection URL:** `wss://localhost:7050/meeting?user_email=<email>`

**Note:** User email should be passed as query parameter during connection.

#### Connection Example
```javascript
const userEmail = 'user@example.com';
const meetingSocket = io('https://localhost:7050/meeting', {
  transports: ['websocket'],
  secure: true,
  rejectUnauthorized: false,
  query: {
    user_email: userEmail
  }
});

meetingSocket.on('connect', () => {
  console.log('Connected to meeting server');
});
```

---

#### Events from Client to Server

##### 1. `join`
**Description:** Join a meeting room  
**Payload:**
```json
{
  "room": "meet_abc123",
  "user_email": "user@example.com"
}
```

**Example:**
```javascript
meetingSocket.emit('join', {
  room: 'meet_abc123',
  user_email: 'user@example.com'
});
```

---

##### 2. `leave`
**Description:** Leave a meeting room  
**Payload:**
```json
{
  "room": "meet_abc123",
  "user_email": "user@example.com"
}
```

**Example:**
```javascript
meetingSocket.emit('leave', {
  room: 'meet_abc123',
  user_email: 'user@example.com'
});
```

---

##### 3. `offer` (WebRTC)
**Description:** Send WebRTC offer to establish peer connection  
**Payload:**
```json
{
  "targetId": "peer_socket_id",
  "sdp": {
    "type": "offer",
    "sdp": "v=0\r\no=- 123456789 2 IN IP4 127.0.0.1..."
  }
}
```

**Example:**
```javascript
// Create WebRTC offer
const offer = await peerConnection.createOffer();
await peerConnection.setLocalDescription(offer);

meetingSocket.emit('offer', {
  targetId: targetPeerId,
  sdp: offer
});
```

---

##### 4. `answer` (WebRTC)
**Description:** Send WebRTC answer in response to an offer  
**Payload:**
```json
{
  "targetId": "peer_socket_id",
  "sdp": {
    "type": "answer",
    "sdp": "v=0\r\no=- 987654321 2 IN IP4 127.0.0.1..."
  }
}
```

**Example:**
```javascript
const answer = await peerConnection.createAnswer();
await peerConnection.setLocalDescription(answer);

meetingSocket.emit('answer', {
  targetId: targetPeerId,
  sdp: answer
});
```

---

##### 5. `ice-candidate` (WebRTC)
**Description:** Send ICE candidate for WebRTC connection  
**Payload:**
```json
{
  "targetId": "peer_socket_id",
  "candidate": {
    "candidate": "candidate:1 1 UDP 2130706431 192.168.1.1 54321 typ host",
    "sdpMLineIndex": 0,
    "sdpMid": "0"
  }
}
```

**Example:**
```javascript
peerConnection.onicecandidate = (event) => {
  if (event.candidate) {
    meetingSocket.emit('ice-candidate', {
      targetId: targetPeerId,
      candidate: event.candidate
    });
  }
};
```

---

#### Events from Server to Client

##### 1. `room-joined`
**Description:** Successfully joined a meeting room  
**Payload:**
```json
{
  "room": "meet_abc123",
  "peerId": "your_socket_id",
  "peers": ["peer1_id", "peer2_id"],
  "timestamp": "2025-11-30T12:00:00Z"
}
```

**Example:**
```javascript
meetingSocket.on('room-joined', (data) => {
  console.log('Joined room:', data.room);
  console.log('Your peer ID:', data.peerId);
  console.log('Existing peers:', data.peers);
  
  // Initiate connections with existing peers
  data.peers.forEach(peerId => {
    createPeerConnection(peerId);
  });
});
```

---

##### 2. `new-peer`
**Description:** A new peer joined the meeting  
**Payload:**
```json
{
  "peerId": "new_peer_socket_id",
  "user_email": "newuser@example.com"
}
```

**Example:**
```javascript
meetingSocket.on('new-peer', (data) => {
  console.log('New peer joined:', data.peerId);
  createPeerConnection(data.peerId);
  
  // Send offer to new peer
  sendOffer(data.peerId);
});
```

---

##### 3. `peer-disconnected`
**Description:** A peer left the meeting  
**Payload:**
```json
{
  "peerId": "disconnected_peer_id"
}
```

**Example:**
```javascript
meetingSocket.on('peer-disconnected', (data) => {
  console.log('Peer disconnected:', data.peerId);
  removePeerConnection(data.peerId);
  removeVideoElement(data.peerId);
});
```

---

##### 4. `offer` (WebRTC)
**Description:** Received WebRTC offer from a peer  
**Payload:**
```json
{
  "peerId": "sender_socket_id",
  "sdp": {
    "type": "offer",
    "sdp": "v=0\r\no=- 123456789 2 IN IP4..."
  }
}
```

**Example:**
```javascript
meetingSocket.on('offer', async (data) => {
  const peerConnection = getPeerConnection(data.peerId);
  await peerConnection.setRemoteDescription(data.sdp);
  
  const answer = await peerConnection.createAnswer();
  await peerConnection.setLocalDescription(answer);
  
  meetingSocket.emit('answer', {
    targetId: data.peerId,
    sdp: answer
  });
});
```

---

##### 5. `answer` (WebRTC)
**Description:** Received WebRTC answer from a peer  
**Payload:**
```json
{
  "peerId": "sender_socket_id",
  "sdp": {
    "type": "answer",
    "sdp": "v=0\r\no=- 987654321 2 IN IP4..."
  }
}
```

**Example:**
```javascript
meetingSocket.on('answer', async (data) => {
  const peerConnection = getPeerConnection(data.peerId);
  await peerConnection.setRemoteDescription(data.sdp);
});
```

---

##### 6. `ice-candidate` (WebRTC)
**Description:** Received ICE candidate from a peer  
**Payload:**
```json
{
  "peerId": "sender_socket_id",
  "candidate": {
    "candidate": "candidate:1 1 UDP...",
    "sdpMLineIndex": 0,
    "sdpMid": "0"
  }
}
```

**Example:**
```javascript
meetingSocket.on('ice-candidate', async (data) => {
  const peerConnection = getPeerConnection(data.peerId);
  await peerConnection.addIceCandidate(data.candidate);
});
```

---

##### 7. `error`
**Description:** Error occurred  
**Payload:**
```json
{
  "message": "Room is full",
  "code": "ROOM_FULL"
}
```

---

##### 8. `room-full`
**Description:** Cannot join - room is at capacity  
**Payload:**
```json
{
  "message": "Room has reached maximum capacity",
  "room": "meet_abc123"
}
```

---

#### Complete WebRTC Meeting Implementation

```javascript
class VideoMeeting {
  constructor(meetingId, userEmail) {
    this.meetingId = meetingId;
    this.userEmail = userEmail;
    this.peerConnections = new Map();
    this.localStream = null;
    
    this.socket = io('https://localhost:7050/meeting', {
      transports: ['websocket'],
      secure: true,
      rejectUnauthorized: false,
      query: { user_email: userEmail }
    });
    
    this.setupSocketListeners();
  }
  
  async initialize() {
    // Get local media stream
    this.localStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });
    
    // Display local video
    document.getElementById('local-video').srcObject = this.localStream;
    
    // Join the meeting room
    this.socket.emit('join', {
      room: this.meetingId,
      user_email: this.userEmail
    });
  }
  
  setupSocketListeners() {
    this.socket.on('room-joined', (data) => {
      console.log('Joined room');
      // Create connections with existing peers
      data.peers.forEach(peerId => {
        this.createPeerConnection(peerId, true);
      });
    });
    
    this.socket.on('new-peer', (data) => {
      console.log('New peer:', data.peerId);
      this.createPeerConnection(data.peerId, false);
    });
    
    this.socket.on('peer-disconnected', (data) => {
      this.removePeer(data.peerId);
    });
    
    this.socket.on('offer', async (data) => {
      const pc = this.peerConnections.get(data.peerId);
      await pc.setRemoteDescription(data.sdp);
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      
      this.socket.emit('answer', {
        targetId: data.peerId,
        sdp: answer
      });
    });
    
    this.socket.on('answer', async (data) => {
      const pc = this.peerConnections.get(data.peerId);
      await pc.setRemoteDescription(data.sdp);
    });
    
    this.socket.on('ice-candidate', async (data) => {
      const pc = this.peerConnections.get(data.peerId);
      if (pc) {
        await pc.addIceCandidate(data.candidate);
      }
    });
  }
  
  createPeerConnection(peerId, shouldCreateOffer) {
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });
    
    // Add local stream tracks
    this.localStream.getTracks().forEach(track => {
      pc.addTrack(track, this.localStream);
    });
    
    // Handle incoming tracks
    pc.ontrack = (event) => {
      this.displayRemoteVideo(peerId, event.streams[0]);
    };
    
    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        this.socket.emit('ice-candidate', {
          targetId: peerId,
          candidate: event.candidate
        });
      }
    };
    
    this.peerConnections.set(peerId, pc);
    
    // Create and send offer if we're the initiator
    if (shouldCreateOffer) {
      this.createOffer(peerId);
    }
    
    return pc;
  }
  
  async createOffer(peerId) {
    const pc = this.peerConnections.get(peerId);
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    
    this.socket.emit('offer', {
      targetId: peerId,
      sdp: offer
    });
  }
  
  displayRemoteVideo(peerId, stream) {
    let video = document.getElementById(`video-${peerId}`);
    if (!video) {
      video = document.createElement('video');
      video.id = `video-${peerId}`;
      video.autoplay = true;
      document.getElementById('remote-videos').appendChild(video);
    }
    video.srcObject = stream;
  }
  
  removePeer(peerId) {
    const pc = this.peerConnections.get(peerId);
    if (pc) {
      pc.close();
      this.peerConnections.delete(peerId);
    }
    
    const video = document.getElementById(`video-${peerId}`);
    if (video) {
      video.remove();
    }
  }
  
  leaveMeeting() {
    this.socket.emit('leave', {
      room: this.meetingId,
      user_email: this.userEmail
    });
    
    // Clean up
    this.peerConnections.forEach(pc => pc.close());
    this.localStream.getTracks().forEach(track => track.stop());
    this.socket.disconnect();
  }
}

// Usage
const meeting = new VideoMeeting('meet_abc123', 'user@example.com');
meeting.initialize();
```

---

## 📊 Data Models

### User Roles (Enum)
```python
class ROLE(Enum):
    GUEST = "GUEST"
    MANAGER = "MANAGER"
    EMPLOYER = "EMPLOYER"
    HR = "HR"
    ADMIN = "ADMIN"
```

### Departments (Enum)
```python
class Department(Enum):
    HR = "HR"
    IT = "IT"
    SALES = "SALES"
    MARKETING = "MARKETING"
```

### Meeting Model
```python
{
    "ID": str,                          # Unique meeting ID
    "Title": str,                       # Meeting title
    "Object": str,                      # Meeting subject/object
    "InvitationLink": str,              # Join link
    "LogPath": str,                     # Path to log file
    "Description": str,                 # Meeting description
    "InvitedEmployeesList": List[str],  # List of invited emails
    "Creator": str,                     # Creator email
    "created_at": str,                  # ISO 8601 timestamp
    "started_at": str,                  # ISO 8601 timestamp (nullable)
    "ended_at": str,                    # ISO 8601 timestamp (nullable)
    "is_active": bool                   # Active status
}
```

---

## ⚠️ Error Handling

### HTTP Error Codes

| Code | Meaning | When It Happens |
|------|---------|----------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Missing required fields or invalid data |
| `401` | Unauthorized | Missing or invalid JWT token |
| `404` | Not Found | Resource not found |
| `500` | Internal Server Error | Server-side error |
| `503` | Service Unavailable | Backend service unreachable |
| `504` | Gateway Timeout | Backend service timeout |

### Error Response Format

```json
{
  "error": "Error description",
  "details": "Detailed error message",
  "code": "ERROR_CODE"  // Optional
}
```

### WebSocket Error Format

```json
{
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

**Authentication Errors:**
- `MISSING_TOKEN` - JWT token not provided
- `INVALID_TOKEN` - JWT token is invalid or expired

**Meeting Errors:**
- `ROOM_FULL` - Meeting room at capacity
- `ROOM_NOT_FOUND` - Meeting ID doesn't exist
- `MEETING_NOT_FOUND` - Meeting not found

**Game Errors:**
- `MATCH_NOT_FOUND` - Game match doesn't exist
- `MATCH_FULL` - Match already has 2 players
- `INVALID_MOVE` - Move is not valid

**File Errors:**
- `NO_FILE_PROVIDED` - File not included in upload
- `FILE_NOT_FOUND` - Requested file doesn't exist

---

## 🔧 Integration Examples

### React Integration Example

```jsx
import { useState, useEffect } from 'react';
import io from 'socket.io-client';

// API Service
class GatewayAPI {
  constructor(baseUrl = 'https://localhost:7050') {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('jwt_token');
  }
  
  setToken(token) {
    this.token = token;
    localStorage.setItem('jwt_token', token);
  }
  
  async login(email, password) {
    const response = await fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) throw new Error('Login failed');
    
    const data = await response.json();
    this.setToken(data.Token);
    return data;
  }
  
  async createMeeting(meetingData) {
    const response = await fetch(`${this.baseUrl}/create-meet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(meetingData)
    });
    
    if (!response.ok) throw new Error('Failed to create meeting');
    return await response.json();
  }
  
  async getMeetings(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${this.baseUrl}/meetings?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    
    if (!response.ok) throw new Error('Failed to get meetings');
    return await response.json();
  }
  
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) throw new Error('Upload failed');
    return await response.json();
  }
}

// React Component Example
function MeetingApp() {
  const [api] = useState(() => new GatewayAPI());
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadMeetings();
  }, []);
  
  async function loadMeetings() {
    setLoading(true);
    try {
      const data = await api.getMeetings({ is_active: true });
      setMeetings(data.meetings);
    } catch (error) {
      console.error('Error loading meetings:', error);
    } finally {
      setLoading(false);
    }
  }
  
  async function handleCreateMeeting(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
      const result = await api.createMeeting({
        title: formData.get('title'),
        description: formData.get('description'),
        creator_email: 'user@example.com',
        invited_employees: []
      });
      
      alert('Meeting created! Code: ' + result.meeting_id);
      loadMeetings();
    } catch (error) {
      alert('Error creating meeting: ' + error.message);
    }
  }
  
  return (
    <div>
      <h1>Meetings</h1>
      
      <form onSubmit={handleCreateMeeting}>
        <input name="title" placeholder="Meeting Title" required />
        <input name="description" placeholder="Description" />
        <button type="submit">Create Meeting</button>
      </form>
      
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {meetings.map(meeting => (
            <li key={meeting.ID}>
              <h3>{meeting.Title}</h3>
              <p>{meeting.Description}</p>
              <a href={meeting.InvitationLink}>Join</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

### Vue.js Integration Example

```vue
<template>
  <div id="app">
    <h1>Gateway API Demo</h1>
    
    <!-- Login Form -->
    <form @submit.prevent="login" v-if="!isLoggedIn">
      <input v-model="loginForm.email" placeholder="Email" type="email" />
      <input v-model="loginForm.password" placeholder="Password" type="password" />
      <button type="submit">Login</button>
    </form>
    
    <!-- Meetings List -->
    <div v-if="isLoggedIn">
      <h2>Your Meetings</h2>
      <button @click="loadMeetings">Refresh</button>
      
      <div v-for="meeting in meetings" :key="meeting.ID" class="meeting-card">
        <h3>{{ meeting.Title }}</h3>
        <p>{{ meeting.Description }}</p>
        <button @click="joinMeeting(meeting.ID)">Join</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loginForm: { email: '', password: '' },
      isLoggedIn: false,
      token: null,
      meetings: [],
      baseUrl: 'https://localhost:7050'
    };
  },
  
  methods: {
    async login() {
      try {
        const response = await fetch(`${this.baseUrl}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.loginForm)
        });
        
        const data = await response.json();
        this.token = data.Token;
        this.isLoggedIn = true;
        localStorage.setItem('jwt_token', data.Token);
        
        await this.loadMeetings();
      } catch (error) {
        alert('Login failed: ' + error.message);
      }
    },
    
    async loadMeetings() {
      try {
        const response = await fetch(`${this.baseUrl}/meetings`, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        });
        
        const data = await response.json();
        this.meetings = data.meetings;
      } catch (error) {
        console.error('Error loading meetings:', error);
      }
    },
    
    joinMeeting(meetingId) {
      window.location.href = `${this.baseUrl}/room/${meetingId}/${this.loginForm.email}`;
    }
  },
  
  mounted() {
    const savedToken = localStorage.getItem('jwt_token');
    if (savedToken) {
      this.token = savedToken;
      this.isLoggedIn = true;
      this.loadMeetings();
    }
  }
};
</script>
```

---

## 📝 Best Practices

### 1. **Authentication**
- Always store JWT tokens securely (not in localStorage if possible)
- Include `Authorization` header in all protected requests
- Handle token expiration gracefully
- Implement token refresh mechanism

### 2. **WebSocket Connections**
- Handle reconnection logic
- Implement exponential backoff for retries
- Clean up connections on component unmount
- Handle network interruptions

### 3. **Error Handling**
- Always check response status codes
- Display user-friendly error messages
- Log errors for debugging
- Implement retry logic for transient failures

### 4. **File Uploads**
- Validate file size and type before upload
- Show upload progress to users
- Handle large files appropriately
- Implement chunked uploads for very large files

### 5. **Real-time Features**
- Use WebSocket for bidirectional communication
- Implement heartbeat/ping-pong to detect disconnections
- Buffer messages during connection loss
- Implement presence detection

---

## 🔒 Security Considerations

1. **HTTPS Only:** Always use HTTPS in production
2. **JWT Validation:** Validate JWT tokens on every protected endpoint
3. **CORS Configuration:** Configure CORS properly for production
4. **Rate Limiting:** Implement rate limiting to prevent abuse
5. **Input Validation:** Validate all user inputs
6. **File Upload Security:** 
   - Validate file types
   - Scan for malware
   - Limit file sizes
   - Store files securely

---

## 📞 Support & Troubleshooting

### Common Issues

**1. WebSocket Connection Failed**
- Check if SSL certificates are valid
- Verify WebSocket URL is correct
- Check firewall settings
- Ensure `transports: ['websocket']` is set

**2. JWT Token Expired**
- Implement token refresh
- Re-login to get new token
- Check token expiration time

**3. CORS Errors**
- Verify origin is allowed
- Check CORS configuration
- Include credentials if needed

**4. File Upload Fails**
- Check file size limits
- Verify content type
- Ensure proper form encoding

### Debug Mode

Enable debug logging in browser console:
```javascript
localStorage.debug = 'socket.io-client:socket';
```

---

## 📄 Changelog

### Version 1.0.0 (2025-11-30)
- Initial Gateway API documentation
- HTTP REST endpoints documented
- WebSocket namespaces documented
- Integration examples provided
- Security best practices added

---

## 📧 Contact

For API support or questions, contact the development team.

---

**End of Documentation**
