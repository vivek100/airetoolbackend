# Internal App Builder API Documentation

## Overview
This API allows you to create and modify internal tools through natural language commands. It uses WebSocket for real-time updates and REST endpoints for managing applications.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required (to be implemented in future versions).

## API Endpoints

### 1. Create/Edit Application
Create a new application or edit an existing one.

**Endpoint:** `POST /agent/run`

**Request Body:**
```json
{
  "project_id": "string | null",  // Required for edit mode, optional for create
  "mode": "create" | "edit",      // Required
  "user_input": "string",         // Required - Natural language description
  "chat_history": "array | null", // Optional
  "user_id": "string | null"      // Optional
}
```

**Example Create Request:**
```json
{
  "mode": "create",
  "user_input": "Build a task management app with projects and tasks. Include a dashboard showing task completion metrics."
}
```

**Example Edit Request:**
```json
{
  "project_id": "abc123",
  "mode": "edit",
  "user_input": "Add a chart to the dashboard showing tasks by status"
}
```

**Response:**
```json
{
  "status": "started",
  "project_id": "abc123",
  "ws_channel": "agent-updates-abc123"
}
```

### 2. Get Project Details
Retrieve the configuration and data for a specific project.

**Endpoint:** `GET /project/{project_id}`

**Response:**
```json
{
  "project_id": "string",
  "appConfig": {
    // Full application configuration
    "pages": [...],
    "components": [...],
    ...
  },
  "mockData": {
    // Mock data for each entity
    "tasks": [...],
    "users": [...],
    ...
  }
}
```

## WebSocket Connection

### Connect to WebSocket
```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/${project_id}`);
```

### WebSocket Events

1. **Status Updates:**
```json
{
  "type": "status",
  "step": "analyze_user_intent",
  "message": "Analyzing user intent..."
}
```

2. **State Updates:**
```json
{
  "type": "state",
  "step": "generate_pages",
  "data": {
    "pages": [...]
  }
}
```

3. **Completion:**
```json
{
  "type": "complete",
  "message": "App successfully generated",
  "config": {...},
  "mockData": {...}
}
```

4. **Error:**
```json
{
  "type": "error",
  "step": "generate_mock_data",
  "error": "Error message"
}
```

## Example Usage (Frontend)

```typescript
// Example React/TypeScript code

async function createApp(description: string) {
  // 1. Start the generation process
  const response = await fetch('http://localhost:8000/agent/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mode: 'create',
      user_input: description
    })
  });
  
  const { project_id, ws_channel } = await response.json();
  
  // 2. Connect to WebSocket for updates
  const ws = new WebSocket(`ws://localhost:8000/ws/${project_id}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
      case 'status':
        // Update UI with status message
        console.log(`Status: ${data.message}`);
        break;
      
      case 'state':
        // Update UI with intermediate state
        console.log(`State update for ${data.step}:`, data.data);
        break;
      
      case 'complete':
        // Handle completion - load the generated app
        console.log('App generated:', data.config);
        loadGeneratedApp(data.config, data.mockData);
        break;
      
      case 'error':
        // Handle error
        console.error(`Error in ${data.step}:`, data.error);
        break;
    }
  };
}

// Example edit function
async function editApp(projectId: string, editDescription: string) {
  const response = await fetch('http://localhost:8000/agent/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      mode: 'edit',
      user_input: editDescription
    })
  });
  
  // Handle response and WebSocket similar to createApp
}
```

## Example Prompts

### Creating New Apps

1. Basic CRUD Application:
```
"Create a customer management system with a list of customers, their contact details, and order history"
```

2. Dashboard-focused App:
```
"Build a sales dashboard showing monthly revenue, top products, and sales by region"
```

3. Multi-entity Application:
```
"Create a project management tool with projects, tasks, and team members. Include a dashboard showing project progress and task status"
```

### Editing Existing Apps

1. Adding Components:
```
"Add a pie chart to the dashboard showing task distribution by assignee"
```

2. Modifying Fields:
```
"Make the due date field required in the task form"
```

3. Adding New Features:
```
"Add a comments section to the task details page"
```

4. Updating Layout:
```
"Move the status chart to the top of the dashboard"
```