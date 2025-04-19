import json
from typing import Dict, Any
from models.agent_state import AgentState
from utils.database import Database
from ws.socket_handler import socket_manager
from utils.openai_client import (
    analyze_intent,
    generate_use_cases,
    generate_page_configs,
    generate_mock_data as generate_mock_data_ai
)

async def analyze_user_intent(state: AgentState, db: Database) -> AgentState:
    try:
        await socket_manager.send_status(
            state.project_id,
            "analyze_user_intent",
            "Analyzing user intent..."
        )
        
        result = await analyze_intent(state.user_input)
        result_dict = json.loads(result)
        
        state.app_name = result_dict["app_name"]
        state.use_case_summary = result_dict["use_case_summary"]
        
        await socket_manager.send_state(
            state.project_id,
            "analyze_user_intent",
            result_dict
        )
        
        await db.save_message(
            state.project_id,
            "analyze_user_intent",
            "success",
            json.dumps(result_dict)
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "analyze_user_intent",
            str(e)
        )
        raise
    
    return state

async def generate_use_cases_step(state: AgentState, db: Database) -> AgentState:
    try:
        await socket_manager.send_status(
            state.project_id,
            "generate_use_cases",
            "Generating use cases..."
        )
        
        result = await generate_use_cases(state.use_case_summary)
        result_dict = json.loads(result)
        
        state.entities = result_dict["entities"]
        state.pages = result_dict["pages"]
        
        await socket_manager.send_state(
            state.project_id,
            "generate_use_cases",
            result_dict
        )
        
        await db.save_message(
            state.project_id,
            "generate_use_cases",
            "success",
            json.dumps(result_dict)
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "generate_use_cases",
            str(e)
        )
        raise
    
    return state

async def generate_page_configs_step(state: AgentState, db: Database) -> AgentState:
    await socket_manager.send_status(
        state.project_id,
        "generate_page_configs",
        "Generating page configurations..."
    )
    
    try:
        result = await generate_page_configs(state.entities, state.pages)
        result_dict = json.loads(result)
        
        state.page_configs = result_dict
        
        await socket_manager.send_state(
            state.project_id,
            "generate_page_configs",
            result_dict
        )
        
        await db.save_message(
            state.project_id,
            "generate_page_configs",
            "success",
            json.dumps(result_dict)
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "generate_page_configs",
            str(e)
        )
        raise
    
    return state

async def generate_mock_data_step(state: AgentState, db: Database) -> AgentState:
    await socket_manager.send_status(
        state.project_id,
        "generate_mock_data",
        "Generating mock data..."
    )
    
    try:
        result = await generate_mock_data_ai(state.entities)
        result_dict = json.loads(result)
        
        state.mock_data = result_dict
        
        await socket_manager.send_state(
            state.project_id,
            "generate_mock_data",
            result_dict
        )
        
        await db.save_message(
            state.project_id,
            "generate_mock_data",
            "success",
            json.dumps(result_dict)
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "generate_mock_data",
            str(e)
        )
        raise
    
    return state

async def write_files(state: AgentState, db: Database) -> AgentState:
    try:
        # Save config
        await db.save_config(state.project_id, state.page_configs)
        
        # Save mock data
        for resource, data in state.mock_data.items():
            await db.save_mock_data(state.project_id, resource, data)
        
        await socket_manager.send_complete(
            state.project_id,
            "App successfully generated",
            state.page_configs,
            state.mock_data
        )
        
        await db.save_message(
            state.project_id,
            "write_files",
            "success",
            "Files written successfully"
        )
        
    except Exception as e:
        await socket_manager.send_message(
            state.project_id,
            {
                "type": "error",
                "step": "write_files",
                "error": str(e)
            }
        )
        raise
    
    return state

def create_flow(db: Database):
    """Create a dictionary of node functions for the creation flow"""
    return {
        "analyze_intent": lambda state: analyze_user_intent(state, db),
        "generate_use_cases": lambda state: generate_use_cases_step(state, db),
        "generate_page_configs": lambda state: generate_page_configs_step(state, db),
        "generate_mock_data": lambda state: generate_mock_data_step(state, db),
        "write_files": lambda state: write_files(state, db)
    }

def get_next_step(current_step: str) -> str:
    """Get the next step based on the current step"""
    steps = {
        "analyze_intent": "generate_use_cases",
        "generate_use_cases": "generate_page_configs",
        "generate_page_configs": "generate_mock_data",
        "generate_mock_data": "write_files",
        "write_files": None  # End of flow
    }
    return steps.get(current_step)