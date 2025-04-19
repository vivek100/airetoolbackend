import aiosqlite
import json
import os
from pathlib import Path

# Use /tmp directory on Render or other cloud platforms
# This is a common writable location on cloud platforms
if os.environ.get('RENDER') == 'true':
    DB_PATH = Path('/tmp/database.db')
else:
    # Original path for local development
    DB_PATH = Path(__file__).parent.parent / "db" / "database.db"

# Ensure the parent directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

async def init_db():
    print(f"Initializing database at: {DB_PATH}")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            schema_path = Path(__file__).parent.parent / "models" / "schema.sql"
            print(f"Loading schema from: {schema_path}")
            with open(schema_path) as f:
                await db.executescript(f.read())
            await db.commit()
            print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    try:
        yield db
    finally:
        await db.close()

class Database:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def get_max_version(self, project_id: str) -> int:
        async with self.db.execute(
            "SELECT MAX(version) FROM configs WHERE project_id = ?",
            (project_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] or 0

    async def get_config(self, project_id: str, version: int) -> dict:
        async with self.db.execute(
            "SELECT config_json FROM configs WHERE project_id = ? AND version = ?",
            (project_id, version)
        ) as cursor:
            result = await cursor.fetchone()
            return json.loads(result[0]) if result else {}

    async def get_all_mock_data(self, project_id: str) -> dict:
        async with self.db.execute(
            "SELECT resource_name, data_json FROM mock_data WHERE project_id = ?",
            (project_id,)
        ) as cursor:
            results = await cursor.fetchall()
            return {
                row[0]: json.loads(row[1])
                for row in results
            }

    async def save_config(self, project_id: str, config_json: dict):
        version = await self.get_max_version(project_id) + 1
        await self.db.execute(
            "INSERT INTO configs (project_id, version, config_json) VALUES (?, ?, ?)",
            (project_id, version, json.dumps(config_json))
        )
        await self.db.commit()

    async def save_mock_data(self, project_id: str, resource: str, data: list):
        await self.db.execute(
            """
            INSERT OR REPLACE INTO mock_data (project_id, resource_name, data_json)
            VALUES (?, ?, ?)
            """,
            (project_id, resource, json.dumps(data))
        )
        await self.db.commit()

    async def save_message(self, project_id: str, step: str, msg_type: str, content: str):
        await self.db.execute(
            "INSERT INTO messages (project_id, step, type, content) VALUES (?, ?, ?, ?)",
            (project_id, step, msg_type, content)
        )
        await self.db.commit()