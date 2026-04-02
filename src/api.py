import sqlite3
import json
import asyncio
import uuid
from typing import List, Optional, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agent import NeuralAgent

app = FastAPI(title="Neural Web Tester - Bridge API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
DB_NAME = "telemetry.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            url TEXT,
            bdd_goal TEXT,
            status TEXT DEFAULT 'RUNNING'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            step_number INTEGER,
            state_hash TEXT,
            screenshot_base64 TEXT,
            action_json TEXT,
            observation_json TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- State Management ---
class AgentState:
    def __init__(self):
        self.running_agents: Dict[str, NeuralAgent] = {}
        self.stop_events: Dict[str, asyncio.Event] = {}
        self.current_session_id: Optional[str] = None

state = AgentState()

# --- Request Models ---
class StartRequest(BaseModel):
    url: str
    bdd_goal: str = "Navegar no site"
    steps: int = 10

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        message_str = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception:
                pass

manager = ConnectionManager()

# --- Helper Functions ---
def save_session(session_id, url, bdd_goal):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO sessions (id, url, bdd_goal, status) VALUES (?, ?, ?, ?)",
                   (session_id, url, bdd_goal, 'RUNNING'))
    conn.commit()
    conn.close()

def update_session_status(session_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET status = ? WHERE id = ?", (status, session_id))
    conn.commit()
    conn.close()

async def run_agent_task(session_id: str, url: str, bdd_goal: str, steps: int):
    stop_event = asyncio.Event()
    state.stop_events[session_id] = stop_event

    agent = NeuralAgent(url=url, bdd_step=bdd_goal, max_steps=steps)
    state.running_agents[session_id] = agent

    # Broadcast session initialization
    await manager.broadcast({
        "type": "init_session",
        "data": {
            "session_id": session_id,
            "url": url,
            "bdd_goal": bdd_goal
        }
    })

    try:
        # Pass the stop event to the agent (we need to modify agent.py to support this)
        # For now, we will wrap the agent.run() and check the event if possible,
        # but the best way is to inject it.
        await agent.run(stop_event=stop_event)
        update_session_status(session_id, "FINISHED")
    except Exception as e:
        print(f"Error running agent: {e}")
        update_session_status(session_id, "ERROR")
    finally:
        if session_id in state.running_agents:
            del state.running_agents[session_id]
        if session_id in state.stop_events:
            del state.stop_events[session_id]
        if state.current_session_id == session_id:
            state.current_session_id = None

        await manager.broadcast({
            "type": "status_update",
            "data": {
                "session_id": session_id,
                "status": "FINISHED"
            }
        })

# --- Endpoints ---
@app.post("/start")
async def start_agent(request: StartRequest, background_tasks: BackgroundTasks):
    if state.current_session_id and state.current_session_id in state.running_agents:
        return {"status": "error", "message": "An agent is already running"}

    session_id = str(uuid.uuid4())
    state.current_session_id = session_id

    save_session(session_id, request.url, request.bdd_goal)
    background_tasks.add_task(run_agent_task, session_id, request.url, request.bdd_goal, request.steps)

    return {"status": "success", "session_id": session_id}

@app.post("/stop")
async def stop_agent():
    if not state.current_session_id or state.current_session_id not in state.stop_events:
        return {"status": "error", "message": "No agent is currently running"}

    session_id = state.current_session_id
    state.stop_events[session_id].set()
    update_session_status(session_id, "STOPPED")

    return {"status": "success", "session_id": session_id}

@app.get("/status")
async def get_status():
    if not state.current_session_id:
        return {"status": "IDLE"}

    session_id = state.current_session_id
    if session_id in state.running_agents:
        return {"status": "RUNNING", "session_id": session_id}

    return {"status": "FINISHED", "session_id": session_id}

@app.get("/sessions")
async def get_sessions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC")
    sessions = [{"id": r[0], "start_time": r[1], "url": r[2], "bdd_goal": r[3], "status": r[4]} for r in cursor.fetchall()]
    conn.close()
    return sessions

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We mostly broadcast from the server to the frontend
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
