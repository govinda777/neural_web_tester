import gymnasium as gym
from gymnasium import spaces
import numpy as np
import asyncio
import hashlib
from navigation import BrowserManager
from encoder import DOMEncoder
from perception import load_mobilenet_extractor, get_embedding
from model import get_use_model

class WebAgentEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, start_url, gherkin_goal, max_steps=15):
        super(WebAgentEnv, self).__init__()
        self.start_url = start_url
        self.gherkin_goal = gherkin_goal
        self.max_steps = max_steps
        self.step_count = 0

        # Managers & AI
        self.browser = BrowserManager()
        self.encoder = DOMEncoder()
        self.vision_model = load_mobilenet_extractor()

        # Gherkin Goal Embedding (usando modelo compartilhado)
        use_model = get_use_model()
        self.goal_embedding = use_model([gherkin_goal]).numpy()[0]

        # Observation Space (State dimension):
        # (50 elements * 2 coords) + (50 elements * 2 flags) + (50*50 adj matrix) + 1 hash + 512 embedding
        self.state_dim = (50 * 2) + (50 * 2) + (50 * 50) + 1 + 512
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.state_dim,), dtype=np.float32)

        # Action Space: (Action Category (5), Element Index (50))
        # 0: Click, 1: Type, 2: Scroll, 3: Back, 4: Finish
        self.action_space = spaces.MultiDiscrete([5, 50])

        self.state_history = []
        self.last_state_hash = None

    async def async_reset(self, seed=None, options=None):
        await self.browser.start(self.start_url)
        self.step_count = 0
        self.state_history = []
        self.last_state_hash = None
        obs = await self._get_obs()
        return obs, {}

    def reset(self, seed=None, options=None):
        """Método de interface para Gymnasium (síncrono)."""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(self.async_reset(seed, options))
        return loop.run_until_complete(self.async_reset(seed, options))

    async def _get_obs(self):
        screenshot = await self.browser.capture_state()
        elements = await self.browser.get_interactive_elements()

        # Vision embedding para cálculo do hash
        embedding = await asyncio.to_thread(get_embedding, self.vision_model, screenshot)
        current_hash = hashlib.md5(embedding.tobytes()).hexdigest()[:8]

        obs = self.encoder.get_full_state_tensor(
            elements, screenshot, self.last_state_hash, self.goal_embedding
        )
        self.last_state_hash = current_hash
        return obs

    async def async_step(self, action):
        action_cat, element_idx = action
        self.step_count += 1
        reward = -1.0 # Penalidade por passo
        done = False
        truncated = False

        elements = await self.browser.get_interactive_elements()

        try:
            if action_cat == 0: # Click
                if elements and element_idx < len(elements):
                    await elements[element_idx]['element'].click()
                else:
                    reward -= 1.0 # Ação inválida
            elif action_cat == 1: # Type
                if elements and element_idx < len(elements) and elements[element_idx]['tag'] == 'input':
                    await elements[element_idx]['element'].fill("Test data")
                else:
                    reward -= 1.0
            elif action_cat == 2: # Scroll
                await self.browser.page.evaluate("window.scrollBy(0, 500)")
            elif action_cat == 3: # Back
                await self.browser.page.go_back()
            elif action_cat == 4: # Finish
                done = True
                reward += 10.0

            await self.browser.page.wait_for_load_state("networkidle", timeout=2000)
        except Exception:
            reward -= 5.0
            done = True

        if self.last_state_hash in self.state_history:
            reward -= 5.0
        self.state_history.append(self.last_state_hash)

        if self.step_count >= self.max_steps:
            truncated = True

        obs = await self._get_obs()
        return obs, reward, done, truncated, {}

    def step(self, action):
        """Interface síncrona para Gymnasium."""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(self.async_step(action))
        return loop.run_until_complete(self.async_step(action))

    async def async_close(self):
        await self.browser.close()

    def close(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(self.async_close())
        else:
            loop.run_until_complete(self.async_close())
