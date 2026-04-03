import sqlite3
import json
import asyncio
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Neural Web Tester - Observability Server")

# Configuração de CORS para o frontend React (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Banco de Dados SQLite ---
DB_NAME = "telemetry.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            url TEXT,
            bdd_goal TEXT
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            episode_number INTEGER,
            total_reward REAL,
            avg_loss REAL,
            steps_taken INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Gerenciador de Conexões WebSocket ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Remove conexões quebradas silenciosamente
                pass

manager = ConnectionManager()

# --- Endpoints ---

@app.get("/sessions")
async def get_sessions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC")
    sessions = [{"id": r[0], "start_time": r[1], "url": r[2], "bdd_goal": r[3]} for r in cursor.fetchall()]
    conn.close()
    return sessions

@app.get("/sessions/{session_id}/steps")
async def get_steps(session_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT step_number, state_hash, screenshot_base64, action_json, observation_json, timestamp FROM steps WHERE session_id = ? ORDER BY step_number ASC", (session_id,))
    steps = []
    for r in cursor.fetchall():
        steps.append({
            "step_number": r[0],
            "state_hash": r[1],
            "screenshot_base64": r[2],
            "action": json.loads(r[3]) if r[3] else None,
            "observation": json.loads(r[4]) if r[4] else None,
            "timestamp": r[5]
        })
    conn.close()
    return steps

@app.get("/sessions/{session_id}/episodes")
async def get_episodes(session_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT episode_number, total_reward, avg_loss, steps_taken, timestamp FROM episodes WHERE session_id = ? ORDER BY episode_number ASC", (session_id,))
    episodes = []
    for r in cursor.fetchall():
        episodes.append({
            "episode": r[0],
            "total_reward": r[1],
            "avg_loss": r[2],
            "steps_taken": r[3],
            "timestamp": r[4]
        })
    conn.close()
    return episodes

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # O agente envia dados via WS, e nós retransmitimos para o Dashboard e salvamos no banco
            message = json.loads(data)

            if message.get("type") == "init_session":
                save_session(message["data"])
            elif message.get("type") == "step_update":
                save_step(message["data"])
            elif message.get("type") == "episode_summary":
                save_episode(message["data"])

            # Retransmite para todos os clientes (Dashboard)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def save_session(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO sessions (id, url, bdd_goal) VALUES (?, ?, ?)",
                   (data["session_id"], data["url"], data["bdd_goal"]))
    conn.commit()
    conn.close()

def save_step(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO steps (session_id, step_number, state_hash, screenshot_base64, action_json, observation_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["session_id"],
        data["step_number"],
        data["state_hash"],
        data.get("screenshot_base64"),
        json.dumps(data.get("action")),
        json.dumps(data.get("observation"))
    ))
    conn.commit()
    conn.close()

def save_episode(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO episodes (session_id, episode_number, total_reward, avg_loss, steps_taken)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["session_id"],
        data["episode"],
        data["total_reward"],
        data["avg_loss"],
        data["steps_taken"]
    ))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
