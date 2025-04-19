-- Project metadata
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    name TEXT,
    mode TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Latest app config
CREATE TABLE IF NOT EXISTS configs (
    project_id TEXT,
    version INTEGER,
    config_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, version)
);

-- Mock data per resource
CREATE TABLE IF NOT EXISTS mock_data (
    project_id TEXT,
    resource_name TEXT,
    data_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, resource_name)
);

-- WebSocket messages for replay/debug
CREATE TABLE IF NOT EXISTS messages (
    project_id TEXT,
    step TEXT,
    type TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);