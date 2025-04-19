from fastapi import WebSocket
from typing import Dict, Set, Any, Optional
import json

class SocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.frontend_url = "http://localhost:5174/?id="  # Frontend app URL template

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, project_id: str):
        self.active_connections[project_id].remove(websocket)
        if not self.active_connections[project_id]:
            del self.active_connections[project_id]

    async def send_status(self, project_id: str, step: str, message: str):
        """Send a status update message"""
        await self.send_message(project_id, {
            "type": "status",
            "step": step,
            "message": message
        })

    async def send_state(self, project_id: str, step: str, data: Dict[str, Any]):
        """Send a state update message with formatted AI output"""
        # Format the AI output nicely for display
        formatted_data = self._format_ai_output(step, data)
        
        await self.send_message(project_id, {
            "type": "state",
            "step": step,
            "data": data,
            "formatted": formatted_data
        })

    async def send_complete(self, project_id: str, message: str, config: Dict[str, Any], mock_data: Dict[str, Any]):
        """Send a completion message with app URL"""
        # Generate the app URL for preview
        app_url = f"{self.frontend_url}{project_id}"
        preview_api_url = f"http://localhost:8000/project/preview/?id={project_id}"
        
        await self.send_message(project_id, {
            "type": "complete",
            "message": message,
            "config": config,
            "mockData": mock_data,
            "appUrl": app_url,
            "previewApiUrl": preview_api_url,
            "links": {
                "app": app_url,
                "api": preview_api_url
            }
        })

    async def send_error(self, project_id: str, step: str, error: str):
        """Send an error message"""
        await self.send_message(project_id, {
            "type": "error",
            "step": step,
            "error": error
        })

    async def send_message(self, project_id: str, message: dict):
        """Send a raw message to all connections for a project"""
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                await connection.send_json(message)
    
    def _format_ai_output(self, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format AI output based on the step for nice display in frontend"""
        formatted = {"summary": "", "details": {}}
        
        if step == "analyze_user_intent":
            formatted["summary"] = f"App: {data.get('app_name', 'Unknown')}"
            formatted["details"] = {
                "App Name": data.get('app_name', 'Unknown'),
                "Use Case": data.get('use_case_summary', 'No summary provided')
            }
            
        elif step == "generate_use_cases":
            entity_count = len(data.get('entities', []))
            page_count = len(data.get('pages', []))
            formatted["summary"] = f"Generated {entity_count} entities and {page_count} pages"
            
            # Format entities and pages for display
            entities_summary = []
            for entity in data.get('entities', []):
                field_count = len(entity.get('fields', []))
                entities_summary.append(f"{entity.get('name', 'Unknown')} ({field_count} fields)")
                
            pages_summary = []
            for page in data.get('pages', []):
                pages_summary.append(f"{page.get('title', 'Unknown')} - {page.get('purpose', 'No purpose')}")
                
            formatted["details"] = {
                "Entities": entities_summary,
                "Pages": pages_summary
            }
            
        elif step == "generate_page_configs":
            page_count = len(data.get('pages', {}))
            formatted["summary"] = f"Generated UI config with {page_count} pages"
            
        elif step == "generate_mock_data":
            entity_count = len(data.keys())
            record_count = sum(len(records) for records in data.values())
            formatted["summary"] = f"Generated {record_count} records across {entity_count} entities"
            
            # Format record counts by entity
            entity_records = {}
            for entity, records in data.items():
                entity_records[entity] = f"{len(records)} records"
                
            formatted["details"] = entity_records
            
        elif step == "detect_edit_type":
            formatted["summary"] = f"Edit: {data.get('operation', 'Unknown')} {data.get('edit_target', 'Unknown')}"
            formatted["details"] = {
                "Target": f"{data.get('edit_target', 'Unknown')} on {data.get('target_page', 'Unknown')}",
                "Operation": data.get('operation', 'Unknown'),
                "Component": data.get('target_component', 'N/A')
            }
            
        elif step == "load_current_state":
            config_size = len(json.dumps(data.get('config', {})))
            mock_data_size = len(json.dumps(data.get('mockData', {})))
            formatted["summary"] = f"Loaded current app state ({config_size + mock_data_size} bytes)"
            
        return formatted

socket_manager = SocketManager()