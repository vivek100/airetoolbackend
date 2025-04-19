import json
from typing import Dict, Any
from models.agent_state import AgentState
from utils.database import Database
from ws.socket_handler import socket_manager
from utils.openai_client import detect_edit_intent as detect_edit_intent_ai
from utils.openai_client import apply_edit_patch as apply_edit_patch_ai
from utils.openai_client import regenerate_mock_data as regenerate_mock_data_ai

async def detect_edit_type(state: AgentState, db: Database) -> AgentState:
    try:
        await socket_manager.send_status(
            state.project_id,
            "detect_edit_type",
            "Analyzing edit request..."
        )
        
        result = await detect_edit_intent_ai(state.user_input)
        result_dict = json.loads(result)
        
        state.edit_target = result_dict["edit_target"]
        state.modification_details = result_dict
        
        await socket_manager.send_state(
            state.project_id,
            "detect_edit_type",
            result_dict
        )
        
        await db.save_message(
            state.project_id,
            "detect_edit_type",
            "success",
            json.dumps(result_dict)
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "detect_edit_type",
            str(e)
        )
        raise
    
    return state

async def load_current_state(state: AgentState, db: Database) -> AgentState:
    try:
        await socket_manager.send_status(
            state.project_id,
            "load_current_state",
            "Loading current configuration..."
        )
        
        # Load latest config version
        version = await db.get_max_version(state.project_id)
        config = await db.get_config(state.project_id, version)
        state.current_config = config
        
        # Load all mock data
        mock_data = await db.get_all_mock_data(state.project_id)
        state.mock_data = mock_data
        
        await socket_manager.send_state(
            state.project_id,
            "load_current_state",
            {
                "config": config,
                "mockData": mock_data
            }
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "load_current_state",
            str(e)
        )
        raise
    
    return state

async def apply_patch(state: AgentState, db: Database) -> AgentState:
    await socket_manager.send_status(
        state.project_id,
        "apply_patch",
        "Applying requested changes..."
    )
    
    try:
        result = await apply_edit_patch_ai(
            state.current_config,
            state.edit_target,
            state.modification_details
        )
        result_dict = json.loads(result)
        
        state.updated_config = result_dict
        
        await socket_manager.send_state(
            state.project_id,
            "apply_patch",
            result_dict
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "apply_patch",
            str(e)
        )
        raise
    
    return state

async def regenerate_affected_data(state: AgentState, db: Database) -> AgentState:
    # Only regenerate if schema changed
    if not needs_data_regeneration(state.modification_details):
        return state
    
    await socket_manager.send_status(
        state.project_id,
        "regenerate_data",
        "Updating mock data for schema changes..."
    )
    
    try:
        result = await regenerate_mock_data_ai(
            state.updated_config,
            state.mock_data,
            state.modification_details
        )
        result_dict = json.loads(result)
        
        state.updated_data = result_dict
        
        await socket_manager.send_state(
            state.project_id,
            "regenerate_data",
            result_dict
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "regenerate_data",
            str(e)
        )
        raise
    
    return state

async def save_updates(state: AgentState, db: Database) -> AgentState:
    try:
        # Save updated config
        await db.save_config(state.project_id, state.updated_config)
        
        # Save updated mock data if any
        if state.updated_data:
            for resource, data in state.updated_data.items():
                await db.save_mock_data(state.project_id, resource, data)
        
        await socket_manager.send_complete(
            state.project_id,
            "Updates successfully applied",
            state.updated_config,
            state.updated_data or state.mock_data
        )
        
        await db.save_message(
            state.project_id,
            "save_updates",
            "success",
            "Updates saved successfully"
        )
        
    except Exception as e:
        await socket_manager.send_error(
            state.project_id,
            "save_updates",
            str(e)
        )
        raise
    
    return state

def needs_data_regeneration(modification_details: Dict[str, Any]) -> bool:
    """Check if the edit affects data schema and requires regeneration."""
    schema_changing_ops = {
        "add_field",
        "remove_field",
        "modify_field_type",
        "add_entity",
        "remove_entity"
    }
    return modification_details.get("operation") in schema_changing_ops

def create_edit_flow(db: Database):
    """Create a dictionary of node functions for the edit flow"""
    return {
        "detect_edit_type": lambda state: detect_edit_type(state, db),
        "load_current_state": lambda state: load_current_state(state, db),
        "apply_patch": lambda state: apply_patch(state, db),
        "regenerate_affected_data": lambda state: regenerate_affected_data(state, db),
        "save_updates": lambda state: save_updates(state, db)
    }

def get_next_step(current_step: str) -> str:
    """Get the next step based on the current step"""
    steps = {
        "detect_edit_type": "load_current_state",
        "load_current_state": "apply_patch",
        "apply_patch": "regenerate_affected_data",
        "regenerate_affected_data": "save_updates",
        "save_updates": None  # End of flow
    }
    return steps.get(current_step)