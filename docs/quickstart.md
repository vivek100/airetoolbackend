# Quick Start Guide

## Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

## Setup Instructions

1. **Create a virtual environment:**
```bash
python -m venv venv
```

2. **Activate the virtual environment:**

Windows:
```bash
.\venv\Scripts\activate
```

Unix/MacOS:
```bash
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Start the server:**
```bash
cd src
uvicorn app:app --reload --port 8000
```

The server will start at `http://localhost:8000`

## Testing the API

1. **Using curl:**

Create a new app:
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "create",
    "user_input": "Create a task management app with projects and tasks"
  }'
```

2. **Using the FastAPI Swagger UI:**
- Open `http://localhost:8000/docs` in your browser
- Test the endpoints using the interactive documentation

3. **Testing WebSocket:**

Using wscat (install with `npm install -g wscat`):
```bash
wscat -c ws://localhost:8000/ws/your_project_id
```

## Common Test Cases

1. **Create a simple app:**
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "create",
    "user_input": "Create a simple todo list app with tasks and categories"
  }'
```

2. **Edit an existing app:**
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "your_project_id",
    "mode": "edit",
    "user_input": "Add a chart showing task completion by day"
  }'
```

3. **Get project details:**
```bash
curl http://localhost:8000/project/your_project_id
```

## Troubleshooting

1. **Database Issues:**
- Ensure the `src/db` directory exists
- Check file permissions
- Delete and recreate the database if schema issues occur

2. **WebSocket Connection Issues:**
- Verify the project_id is correct
- Check if the server is running
- Ensure no firewall is blocking WebSocket connections

3. **OpenAI API Issues:**
- Verify your API key in the .env file
- Check your OpenAI API quota and limits
- Ensure your requests are properly formatted