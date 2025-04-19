from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import aiosqlite
import uuid
import asyncio
import threading

from utils.database import get_db, Database, init_db
import utils.database  # Import for DB_PATH
from ws.socket_handler import socket_manager
from flows.create_agent import create_flow, get_next_step as create_get_next
from flows.edit_agent import create_edit_flow, get_next_step as edit_get_next
from models.agent_state import AgentState

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AgentRequest(BaseModel):
    project_id: Optional[str] = None
    mode: str
    user_input: str
    chat_history: Optional[List[dict]] = None
    user_id: Optional[str] = None

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/agent/run")
async def run_agent(
    request: AgentRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    # Use provided project_id or generate a new one
    # Always have a fallback project ID for safety
    DEFAULT_PROJECT_ID = "default-project-123456"
    project_id = request.project_id or str(uuid.uuid4())
    
    # Initialize state
    state = AgentState(
        user_input=request.user_input,
        mode=request.mode,
        project_id=project_id
    )
    
    # Create database wrapper - but don't pass this to the background thread
    # as the connection will be closed after this function returns
    database = Database(db)
    
    # Select flow and next step function based on mode
    if request.mode == "create":
        flow_type = "create"
        get_next_step = create_get_next
        current_step = "analyze_intent"
    elif request.mode == "edit":
        # For edit mode, use provided project_id or fall back to default
        if not request.project_id:
            project_id = DEFAULT_PROJECT_ID
            state.project_id = DEFAULT_PROJECT_ID
            print(f"No project_id provided for edit mode, using default: {DEFAULT_PROJECT_ID}")
        
        flow_type = "edit"
        get_next_step = edit_get_next
        current_step = "detect_edit_type"
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Must be 'create' or 'edit'"
        )
    
    # Run the flow asynchronously using threading
    def run_flow_thread():
        asyncio.run(execute_flow_with_new_db(flow_type, state, current_step, get_next_step))
    
    thread = threading.Thread(target=run_flow_thread)
    thread.daemon = True
    thread.start()
    
    return {
        "status": "started",
        "project_id": project_id,
        "ws_channel": f"agent-updates-{project_id}"
    }

async def execute_flow_with_new_db(flow_type, state, current_step, get_next_step_func):
    """Execute the flow step by step with a new database connection"""
    # Create a new database connection for this thread
    async with aiosqlite.connect(utils.database.DB_PATH) as db:
        # Create a fresh database wrapper
        database = Database(db)
        
        # Create the flow with the new database connection
        flow = create_flow(database) if flow_type == "create" else create_edit_flow(database)
        
        try:
            while current_step:
                # Execute current step
                await flow[current_step](state)
                
                # Get next step
                current_step = get_next_step_func(current_step)
        except Exception as e:
            # Handle any errors
            print(f"Flow execution error: {str(e)}")
            await socket_manager.send_error(
                state.project_id,
                "execute_flow",
                f"Error executing flow: {str(e)}"
            )
            raise

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await socket_manager.connect(websocket, project_id)
    try:
        while True:
            await websocket.receive_text()
    except:
        await socket_manager.disconnect(websocket, project_id)

@app.get("/project/{project_id}")
async def get_project(
    project_id: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    database = Database(db)
    
    try:
        # Get latest config version
        version = await database.get_max_version(project_id)
        config = await database.get_config(project_id, version)
        
        # Get all mock data
        mock_data = await database.get_all_mock_data(project_id)
        
        return {
            "project_id": project_id,
            "appConfig": config,
            "mockData": mock_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve project: {str(e)}"
        )

@app.get("/project/preview/")
async def get_project_preview(
    id: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Preview endpoint specifically for frontend apps to load configurations"""
    database = Database(db)
    
    try:
        # Get latest config version
        version = await database.get_max_version(id)
        config = await database.get_config(id, version)
        
        # Get all mock data
        mock_data = await database.get_all_mock_data(id)
        
        return {
            "project_id": id,
            "appConfig": config,
            "mockData": mock_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve project preview: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)