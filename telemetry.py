import json
import asyncio
import websockets
import base64
import time
from typing import Optional

class TelemetryManager:
    def __init__(self, ws_url="ws://localhost:8000/ws"):
        self.ws_url = ws_url
        self.ws = None
        self.session_id = f"session_{int(time.time())}"

    async def connect(self):
        try:
            self.ws = await websockets.connect(self.ws_url)
            print(f"Conectado ao servidor de telemetria em {self.ws_url}")
        except Exception as e:
            print(f"Não foi possível conectar ao servidor de telemetria: {e}")
            self.ws = None

    async def init_session(self, url: str, bdd_goal: str):
        if not self.ws:
            await self.connect()

        message = {
            "type": "init_session",
            "data": {
                "session_id": self.session_id,
                "url": url,
                "bdd_goal": bdd_goal
            }
        }
        await self._send(message)

    async def send_step(self, step_number: int, state_hash: str, screenshot_bytes: Optional[bytes], action: Optional[dict], observation: Optional[dict]):
        screenshot_base64 = None
        if screenshot_bytes:
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        message = {
            "type": "step_update",
            "data": {
                "session_id": self.session_id,
                "step_number": step_number,
                "state_hash": state_hash,
                "screenshot_base64": screenshot_base64,
                "action": action,
                "observation": observation
            }
        }
        await self._send(message)

    async def send_episode_summary(self, episode: int, total_reward: float, avg_loss: float, steps_taken: int):
        message = {
            "type": "episode_summary",
            "data": {
                "session_id": self.session_id,
                "episode": episode,
                "total_reward": total_reward,
                "avg_loss": avg_loss,
                "steps_taken": steps_taken
            }
        }
        await self._send(message)

    async def _send(self, message: dict):
        if self.ws:
            try:
                await self.ws.send(json.dumps(message))
            except Exception as e:
                print(f"Erro ao enviar telemetria: {e}")
                self.ws = None # Tenta reconectar no próximo passo

    async def close(self):
        if self.ws:
            await self.ws.close()
