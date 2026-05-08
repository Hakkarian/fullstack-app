# Fullstack App API Documentation

## Overview

This document describes the REST API endpoints available in the Fullstack App backend. The API is built with FastAPI and uses JWT-based authentication via OAuth2 password flow.

**Base URL:** `http://localhost:8000` (development)

**Authentication:** Most endpoints require a JWT bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## Endpoints

### Health Check

#### `GET /health`

Check if the API is running and healthy.

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### Authentication

#### `POST /api/auth/token`

Authenticate user credentials and receive a JWT access token.

**Authentication:** Not required (this is the login endpoint)

**Request Body:** Form data (application/x-www-form-urlencoded)
- `username` (string, required) - The user's username
- `password` (string, required) - The user's password

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK` - Authentication successful
- `400 Bad Request` - Incorrect username or password

**Example:**
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

---

### Tasks

All task endpoints require authentication. Include the bearer token in the Authorization header.

#### `GET /api/tasks`

Retrieve all tasks.

**Authentication:** Required (Bearer token)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Sample task",
    "completed": false
  }
]
```

**Status Codes:**
- `200 OK` - Tasks retrieved successfully
- `401 Unauthorized` - Invalid or missing token

**Example:**
```bash
curl -X GET "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer <your_access_token>"
```

---

#### `POST /api/tasks`

Create a new task.

**Authentication:** Required (Bearer token)

**Request Body:** (application/json)
```json
{
  "title": "New task title"
}
```

**Response:**
```json
{
  "id": 2,
  "title": "New task title",
  "completed": false
}
```

**Status Codes:**
- `200 OK` - Task created successfully
- `401 Unauthorized` - Invalid or missing token

**Example:**
```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "New task"}'
```

---

#### `PUT /api/tasks/{task_id}/complete`

Mark a specific task as completed.

**Authentication:** Required (Bearer token)

**Path Parameters:**
- `task_id` (integer, required) - The ID of the task to mark as complete

**Response:**
```json
{
  "id": 1,
  "title": "Sample task",
  "completed": true
}
```

**Status Codes:**
- `200 OK` - Task marked as completed
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Task with the specified ID does not exist

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/tasks/1/complete" \
  -H "Authorization: Bearer <your_access_token>"
```

---

#### `DELETE /api/tasks/{task_id}`

Delete a specific task.

**Authentication:** Required (Bearer token)

**Path Parameters:**
- `task_id` (integer, required) - The ID of the task to delete

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Task deleted successfully
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Task with the specified ID does not exist

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/tasks/1" \
  -H "Authorization: Bearer <your_access_token>"
```

---

## Data Models

### Task
```json
{
  "id": "integer (auto-generated)",
  "title": "string (required)",
  "completed": "boolean (default: false)"
}
```

### CreateTaskRequest
```json
{
  "title": "string (required)"
}
```

---

## Authentication Flow

1. **Login** - Send POST request to `/api/auth/token` with username and password
2. **Receive Token** - The response contains the JWT access token
3. **Use Token** - Include the token in the Authorization header for all subsequent requests:
   ```
   Authorization: Bearer <access_token>
   ```

---

## Notes

- Tasks are stored in memory and will be lost on server restart
- Task IDs are auto-incremented integers starting from 1
- All task endpoints require authentication via JWT bearer token
- The API uses OAuth2 password flow for authentication
