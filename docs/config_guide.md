# Configuration Guide for Internal App Builder

## Overview
The configuration file (`appConfig.json`) is the heart of your internal app. It defines:
- Page structure and navigation
- UI components and their properties
- Data resources and relationships
- Layout and organization

## Core Structure
```json
{
  "navigation": {
    "title": "App Name",
    "items": []
  },
  "pages": {
    "pageKey": {
      "title": "Page Title",
      "path": "/route-path",
      "zones": []
    }
  }
}
```

## Page Configuration
Each page requires:
- `title`: Display name in navigation and header
- `path`: URL route path
- `subtitle` (optional): Additional context
- `parentPage` (optional): Key of parent page for nesting
- `isGroup` (optional): Boolean for navigation grouping
- `zones`: Array of component zones

Example:
```json
{
  "dashboard": {
    "title": "Dashboard",
    "subtitle": "Overview of key metrics",
    "path": "/",
    "zones": [
      {
        "title": "Key Metrics",
        "components": []
      }
    ]
  }
}
```

## Available Components

### 1. MetricCard
Purpose: Display key statistics or numbers
```json
{
  "type": "MetricCard",
  "props": {
    "label": "Total Users",
    "value": "1,234",
    "trend": "+12%",
    "color": "blue"
  }
}
```

### 2. DataTable
Purpose: CRUD operations on data resources
```json
{
  "type": "DataTable",
  "props": {
    "resource": "users",
    "columns": [
      {
        "field": "name",
        "header": "Name"
      }
    ],
    "actions": ["view", "edit", "create", "delete"]
  }
}
```

### 3. SimpleForm
Purpose: Create/edit forms for resources
```json
{
  "type": "SimpleForm",
  "props": {
    "resource": "users",
    "fields": [
      {
        "name": "email",
        "type": "string",
        "required": true
      }
    ]
  }
}
```

### 4. ExpandableForm
Purpose: Multi-section forms
```json
{
  "type": "ExpandableForm",
  "props": {
    "sections": [
      {
        "title": "Basic Info",
        "fields": []
      }
    ]
  }
}
```

### 5. Chart
Purpose: Data visualization
```json
{
  "type": "Chart",
  "props": {
    "type": "bar",
    "data": {
      "labels": [],
      "datasets": []
    }
  }
}
```

### 6. StatusFlow
Purpose: Progress/stage indicators
```json
{
  "type": "StatusFlow",
  "props": {
    "stages": ["Draft", "Review", "Approved"],
    "currentStage": "Review"
  }
}
```

### 7. TabsComponent
Purpose: Tabbed content sections
```json
{
  "type": "TabsComponent",
  "props": {
    "tabs": [
      {
        "label": "Overview",
        "content": []
      }
    ]
  }
}
```

### 8. Modal
Purpose: Pop-up dialogs
```json
{
  "type": "Modal",
  "props": {
    "title": "Confirm Action",
    "content": []
  }
}
```

## Navigation Configuration
```json
{
  "navigation": {
    "title": "App Name",
    "items": [
      {
        "label": "Dashboard",
        "path": "/"
      },
      {
        "label": "Users",
        "path": "/users",
        "subItems": [
          {
            "label": "List",
            "path": "/users/list"
          }
        ]
      }
    ]
  }
}
```

## Field Types
Available field types for forms:
- `string`: Text input
- `number`: Numeric input
- `boolean`: Checkbox/toggle
- `select`: Dropdown with options
- `date`: Date picker
- `datetime`: Date and time picker
- `text`: Multi-line text area
- `email`: Email input
- `password`: Password input
- `file`: File upload

## Best Practices

1. **Page Organization**
   - Use descriptive page keys
   - Group related pages using parentPage
   - Keep paths consistent with structure

2. **Component Usage**
   - Place MetricCards at the top of dashboards
   - Use DataTable for list views
   - Combine DataTable with SimpleForm for CRUD
   - Use Charts sparingly and meaningfully

3. **Navigation**
   - Limit nesting to 2 levels
   - Use clear, concise labels
   - Group related functionality

4. **Forms**
   - Group related fields
   - Use appropriate field types
   - Mark required fields
   - Provide helpful labels

## Common Issues & Solutions

1. **Navigation Not Showing**
   - Verify page keys match parentPage references
   - Check path format starts with "/"
   - Ensure isGroup is set for parent pages

2. **Components Not Rendering**
   - Verify component type is correct
   - Check required props are provided
   - Validate JSON structure

3. **Forms Not Working**
   - Verify resource name matches backend
   - Check field names match API
   - Ensure required fields are marked

4. **Charts Not Displaying**
   - Validate data structure
   - Check for empty datasets
   - Verify chart type is supported

## Full Example

```json
{
  "navigation": {
    "title": "Task Manager",
    "items": [
      {
        "label": "Dashboard",
        "path": "/"
      },
      {
        "label": "Tasks",
        "path": "/tasks"
      }
    ]
  },
  "pages": {
    "dashboard": {
      "title": "Dashboard",
      "path": "/",
      "zones": [
        {
          "title": "Overview",
          "components": [
            {
              "type": "MetricCard",
              "props": {
                "label": "Total Tasks",
                "value": "156",
                "trend": "+23%",
                "color": "blue"
              }
            }
          ]
        },
        {
          "title": "Task Status",
          "components": [
            {
              "type": "Chart",
              "props": {
                "type": "pie",
                "data": {
                  "labels": ["Todo", "In Progress", "Done"],
                  "datasets": []
                }
              }
            }
          ]
        }
      ]
    },
    "tasks": {
      "title": "Tasks",
      "path": "/tasks",
      "zones": [
        {
          "components": [
            {
              "type": "DataTable",
              "props": {
                "resource": "tasks",
                "columns": [
                  {
                    "field": "title",
                    "header": "Title"
                  },
                  {
                    "field": "status",
                    "header": "Status"
                  },
                  {
                    "field": "dueDate",
                    "header": "Due Date"
                  }
                ],
                "actions": ["view", "edit", "create", "delete"]
              }
            }
          ]
        }
      ]
    }
  }
}
```

## Validation Rules

1. **Required Top-level Keys**
   - navigation
   - pages

2. **Page Requirements**
   - Unique page keys
   - Valid path format
   - Title and path required
   - Valid parentPage references

3. **Component Requirements**
   - Valid component type
   - Required props per component type
   - Valid resource references
   - Valid field references

4. **Navigation Requirements**
   - Unique paths
   - Valid page references
   - Maximum nesting depth