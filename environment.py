import gymnasium as gym
from gymnasium import spaces
import numpy as np
import asyncio
import hashlib
from navigation import BrowserManager
from encoder import DOMEncoder
from perception import load_mobilenet_extractor, get_embedding

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

        # Gherkin Goal Embedding (pre-computed once)
        import tensorflow_hub as hub
        use_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        self.goal_embedding = use_model([gherkin_goal]).numpy()[0]

        # Observation Space (State dimension):
        # (50 elements * 2 coords) + (50 elements * 2 flags) + (50*50 adj matrix) + 1 hash + 512 embedding
        self.state_dim = (50 * 2) + (50 * 2) + (50 * 50) + 1 + 512
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.state_dim,), dtype=np.float32)

        # Action Space: 0: Click(best), 1: Type, 2: Scroll, 3: Back, 4: Finish
        self.action_space = spaces.Discrete(5)

        self.state_history = []
        self.last_state_hash = None

    async def _async_reset(self):
        await self.browser.start(self.start_url)
        self.step_count = 0
        self.state_history = []
        self.last_state_hash = None
        return await self._get_obs(), {}

    def reset(self, seed=None, options=None):
        return asyncio.run(self._async_reset())

    async def _get_obs(self):
        screenshot = await self.browser.capture_state()
        elements = await self.browser.get_interactive_elements()

        # Vision embedding to calculate hash
        embedding = await asyncio.to_thread(get_embedding, self.vision_model, screenshot)
        current_hash = hashlib.md5(embedding.tobytes()).hexdigest()[:8]

        obs = self.encoder.get_full_state_tensor(
            elements, screenshot, self.last_state_hash, self.goal_embedding
        )
        self.last_state_hash = current_hash
        return obs

    async def _async_step(self, action):
        self.step_count += 1
        reward = -1.0 # Penalidade por cada passo
        done = False
        truncated = False

        elements = await self.browser.get_interactive_elements()

        try:
            if action == 0: # Click
                if elements:
                    best_el = elements[0]['element']
                    await best_el.click()
                else:
                    reward -= 1.0 # Penalidade por ação inválida
            elif action == 1: # Type (simplificado)
                if elements and elements[0]['tag'] == 'input':
                    await elements[0]['element'].fill("Test data")
                else:
                    reward -= 1.0
            elif action == 2: # Scroll
                await self.browser.page.evaluate("window.scrollBy(0, 500)")
            elif action == 3: # Back
                await self.browser.page.go_back()
            elif action == 4: # Finish
                done = True
                # No mundo real, validaríamos se o objetivo foi atingido
                reward += 10.0

            await self.browser.page.wait_for_load_state("networkidle", timeout=2000)
        except Exception:
            reward -= 5.0 # Penalidade por erro/timeout
            done = True

        # Detecção de Ciclo
        if self.last_state_hash in self.state_history:
            reward -= 5.0
            # done = True # Opcional: encerrar o episódio ao detectar ciclo
        self.state_history.append(self.last_state_hash)

        if self.step_count >= self.max_steps:
            truncated = True

        obs = await self._get_obs()
        return obs, reward, done, truncated, {}

    def step(self, action):
        return asyncio.run(self._async_step(action))

    def close(self):
        asyncio.run(self.browser.close())
