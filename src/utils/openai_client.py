import os
import json
from dotenv import load_dotenv
import openai
from typing import Dict, Any, List

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key for older version
openai.api_key = os.getenv("OPENAI_API_KEY")

async def analyze_intent(user_input: str) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",  # Using gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert system analyst. Extract the app name and use case summary from the user's request.
                    Format your response as JSON with 'app_name' and 'use_case_summary' keys.
                    The app name should be short, clean, and title-cased.
                    Only return a valid JSON object without any additional text or explanation."""
                },
                {"role": "user", "content": user_input}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # If not valid JSON, create a simple valid response
            default_response = {
                "app_name": "Task App",
                "use_case_summary": user_input
            }
            return json.dumps(default_response)
            
    except Exception as e:
        # Handle API errors
        print(f"OpenAI API error: {str(e)}")
        default_response = {
            "app_name": "Task App",
            "use_case_summary": user_input
        }
        return json.dumps(default_response)

async def generate_use_cases(use_case_summary: str) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",  # Using gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": """Generate entities and pages for the application based on the use case summary.
                    Each entity should have fields with types (string, number, boolean, select, date).
                    Each page should have a title, path, icon, and purpose.
                    Format as JSON with 'entities' and 'pages' arrays.
                    Only return a valid JSON object without any additional text or explanation."""
                },
                {"role": "user", "content": use_case_summary}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # If not valid JSON, create a simple valid response
            default_response = {
                "entities": [
                    {
                        "name": "Task",
                        "fields": [
                            {"name": "title", "type": "string"},
                            {"name": "description", "type": "string"},
                            {"name": "status", "type": "select", "options": ["Todo", "In Progress", "Done"]}
                        ]
                    }
                ],
                "pages": [
                    {
                        "title": "Dashboard",
                        "path": "/",
                        "icon": "home",
                        "purpose": "Main dashboard"
                    },
                    {
                        "title": "Tasks",
                        "path": "/tasks",
                        "icon": "list",
                        "purpose": "Task management"
                    }
                ]
            }
            return json.dumps(default_response)
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        default_response = {
            "entities": [
                {
                    "name": "Task",
                    "fields": [
                        {"name": "title", "type": "string"},
                        {"name": "description", "type": "string"},
                        {"name": "status", "type": "select", "options": ["Todo", "In Progress", "Done"]}
                    ]
                }
            ],
            "pages": [
                {
                    "title": "Dashboard",
                    "path": "/",
                    "icon": "home",
                    "purpose": "Main dashboard"
                },
                {
                    "title": "Tasks",
                    "path": "/tasks",
                    "icon": "list",
                    "purpose": "Task management"
                }
            ]
        }
        return json.dumps(default_response)

async def generate_page_configs(entities: List[Dict[str, Any]], pages: List[Dict[str, Any]]) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",  # Using gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": """Create a detailed UI configuration with pages, zones, and components based on the provided entities and pages.
                    
                    For each page, create at least two zones (e.g., header, main, sidebar, footer).
                    
                    Use these components appropriately:
                    - DataTable: For displaying lists of data with sortable columns
                    - Form: For creating or editing entity records
                    - MetricCard: For displaying summary statistics 
                    - Chart: For visualizing data trends or distributions
                    
                    Each zone should have:
                    - title: A string title for the zone
                    - components: An array of components
                    
                    Each component should have:
                    - type: The component type (DataTable, Form, MetricCard, Chart)
                    - title: A string title for the component
                    - props: An object containing all necessary properties for that component
                    
                    Format as JSON with a 'pages' object, with each page ID as a key containing the full page configuration.
                    
                    Only return a valid JSON object without any additional text or explanation."""
                },
                {
                    "role": "user", 
                    "content": f"Entities: {entities}\nPages: {pages}"
                }
            ]
        )
        
        content = response.choices[0].message.content.strip()
        # Validate JSON
        try:
            json_data = json.loads(content)
            
            # Check if the result has a proper pages structure
            if not json_data.get("pages") or len(json_data.get("pages", {})) == 0:
                # If empty or missing pages, use a default based on entities
                return create_default_page_config(entities, pages)
            
            return content
        except json.JSONDecodeError:
            # Default config based on entities
            return create_default_page_config(entities, pages)
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return create_default_page_config(entities, pages)

def create_default_page_config(entities: List[Dict[str, Any]], pages: List[Dict[str, Any]]) -> str:
    """Create a default page configuration based on the entities and pages"""
    default_config = {"pages": {}}
    
    # If no pages provided, create at least a dashboard and an entity page
    if not pages:
        pages = [
            {"title": "Dashboard", "path": "/", "icon": "home", "purpose": "Main dashboard"},
            {"title": "Tasks", "path": "/tasks", "icon": "list", "purpose": "Task management"}
        ]
    
    # For each page, create a basic configuration
    for page in pages:
        page_id = page.get("path", "").strip("/") or page.get("title", "").lower().replace(" ", "-")
        if not page_id:
            continue
            
        # Create basic page structure
        default_config["pages"][page_id] = {
            "title": page.get("title", "Page"),
            "zones": {
                "header": {
                    "title": "Header",
                    "components": [
                        {
                            "type": "MetricCard",
                            "title": f"{page.get('title', 'Page')} Overview",
                            "props": {
                                "metrics": [
                                    {"label": "Total Items", "value": "0"},
                                    {"label": "Active Items", "value": "0"}
                                ]
                            }
                        }
                    ]
                },
                "main": {
                    "title": "Main Content",
                    "components": []
                }
            }
        }
        
        # Add appropriate components based on page purpose
        main_components = default_config["pages"][page_id]["zones"]["main"]["components"]
        
        # Dashboard-specific components
        if "dashboard" in page.get("title", "").lower() or page.get("path", "") == "/":
            main_components.append({
                "type": "Chart",
                "title": "Activity Overview",
                "props": {
                    "chartType": "bar",
                    "data": {
                        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                        "datasets": [
                            {
                                "label": "Activity",
                                "data": [12, 19, 3, 5, 2]
                            }
                        ]
                    }
                }
            })
        
        # For each entity, add a data table if the page seems to be related to that entity
        for entity in entities:
            entity_name = entity.get("name", "")
            if entity_name.lower() in page.get("title", "").lower() or entity_name.lower() in page.get("purpose", "").lower():
                # Add DataTable for this entity
                columns = []
                fields = entity.get("fields", [])
                if fields and isinstance(fields, list):
                    # Get up to first 4 fields safely
                    field_slice = fields[:min(4, len(fields))]
                    columns = [
                        {"title": field.get("name", "Field"), "dataIndex": field.get("name", "field"), "key": field.get("name", "field")}
                        for field in field_slice
                    ]
                else:
                    # Default column if no fields available
                    columns = [{"title": "ID", "dataIndex": "id", "key": "id"}]
                
                main_components.append({
                    "type": "DataTable",
                    "title": f"{entity_name} List",
                    "props": {
                        "dataSource": entity_name,
                        "columns": columns,
                        "pagination": {"pageSize": 10}
                    }
                })
                
                # Add Form for this entity
                form_items = []
                if fields and isinstance(fields, list):
                    form_items = [
                        {
                            "name": field.get("name", "field"),
                            "label": field.get("name", "Field").title(),
                            "type": field.get("type", "string")
                        }
                        for field in fields
                    ]
                else:
                    # Default form item if no fields available
                    form_items = [{"name": "name", "label": "Name", "type": "string"}]
                
                main_components.append({
                    "type": "Form",
                    "title": f"Add {entity_name}",
                    "props": {
                        "formItems": form_items,
                        "submitText": f"Add {entity_name}"
                    }
                })
    
    return json.dumps(default_config)

async def generate_mock_data(entities: List[Dict[str, Any]]) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",  # Using gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": """Generate realistic mock data for each entity.
                    Create 5-10 records per entity.
                    Ensure foreign keys match between related entities.
                    Use realistic values for dates and enums.
                    Format as JSON with entity names as keys and record arrays as values.
                    Only return a valid JSON object without any additional text or explanation."""
                },
                {"role": "user", "content": str(entities)}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # Default mock data
            return json.dumps({"Task": []})
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return json.dumps({"Task": []})

async def detect_edit_intent(user_input: str) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",  # Using gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": """Analyze the edit request and extract:
                    - edit_target: page, component, data, field, or style
                    - target_page: which page to modify
                    - target_component: which component to modify
                    - operation: add, remove, or update
                    - modification_details: structured description of changes
                    Format as JSON with these fields.
                    Only return a valid JSON object without any additional text or explanation."""
                },
                {"role": "user", "content": user_input}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # Default edit intent
            return json.dumps({
                "edit_target": "component",
                "target_page": "Dashboard",
                "target_component": "main",
                "operation": "update",
                "modification_details": {"description": user_input}
            })
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return json.dumps({
            "edit_target": "component",
            "target_page": "Dashboard",
            "target_component": "main",
            "operation": "update",
            "modification_details": {"description": user_input}
        })

async def apply_edit_patch(
    current_config: Dict[str, Any],
    edit_target: str,
    modification_details: Dict[str, Any]
) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",  # Using gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": """Apply the requested changes to the configuration.
                    Preserve existing structure and only modify what's needed.
                    Return the complete updated configuration as JSON.
                    Only return a valid JSON object without any additional text or explanation."""
                },
                {
                    "role": "user",
                    "content": f"""
                    Current config: {current_config}
                    Edit target: {edit_target}
                    Modifications: {modification_details}
                    """
                }
            ]
        )
        
        content = response.choices[0].message.content.strip()
        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # Default: return existing config
            return json.dumps(current_config)
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return json.dumps(current_config)

async def regenerate_mock_data(
    updated_config: Dict[str, Any],
    current_mock_data: Dict[str, List[Dict[str, Any]]],
    modification_details: Dict[str, Any]
) -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",  # Using gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": """Update mock data to match schema changes.
                    Preserve existing records where possible.
                    Add new fields or records as needed.
                    Return complete updated mock data as JSON.
                    Only return a valid JSON object without any additional text or explanation."""
                },
                {
                    "role": "user",
                    "content": f"""
                    Updated config: {updated_config}
                    Current mock data: {current_mock_data}
                    Modifications: {modification_details}
                    """
                }
            ]
        )
        
        content = response.choices[0].message.content.strip()
        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # Default: return existing mock data
            return json.dumps(current_mock_data)
            
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return json.dumps(current_mock_data)