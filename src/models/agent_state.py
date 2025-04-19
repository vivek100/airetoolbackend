from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel

class AgentState(BaseModel):
    user_input: str
    project_id: str
    app_name: Optional[str] = None
    use_case_summary: Optional[str] = None
    entities: List[Dict[str, Any]] = []
    pages: List[Dict[str, Any]] = []
    page_configs: Dict[str, Any] = {}
    mock_data: Dict[str, List[Dict[str, Any]]] = {}
    current_config: Optional[Dict[str, Any]] = None
    mode: Literal["create", "edit"] = "create"
    edit_target: Optional[str] = None
    modification_details: Optional[Dict[str, Any]] = None
    updated_config: Optional[Dict[str, Any]] = None
    updated_data: Optional[Dict[str, Any]] = None