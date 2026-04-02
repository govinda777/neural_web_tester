import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.navigation import BrowserManager
from src.encoder import DOMEncoder


class WebAgentEnv(gym.Env):
    def __init__(self, url, bdd_step_text, token=None, max_steps=15):
        super(WebAgentEnv, self).__init__()
        self.url = url
        self.bdd_step_text = bdd_step_text
        self.max_steps = max_steps
        self.browser = BrowserManager(token=token)
        self.encoder = DOMEncoder(max_elements=50)

        # Action Space: Category (0-4) and Element Index (0-49)
        self.action_space = spaces.MultiDiscrete([5, 50])

        # Observation Space: Tensor do Encoder (Adjacency + Features + Memory)
        # 50*50 + 50*4 + 32 = 2500 + 200 + 32 = 2732
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(2732,), dtype=np.float32
        )

        self.current_step = 0
        self.previous_hash = None
        self.state_history = []

    async def async_reset(self):
        self.current_step = 0
        self.state_history = []
        self.previous_hash = None
        await self.browser.start(self.url)

        self._last_elements = await self.browser.get_interactive_elements()
        screenshot = await self.browser.capture_state()
        self.previous_hash = self.encoder.get_hash(screenshot)

        obs = self.encoder.encode(self._last_elements, self.previous_hash)
        return obs, {}

    def reset(self, seed=None, options=None):
        # Gymnasium espera um reset síncrono, mas o Playwright é assíncrono.
        # Em um cenário real, usaríamos um loop de evento ou wrapper.
        # Para este projeto, o agente chamará async_reset explicitamente.
        return np.zeros(self.observation_space.shape), {}

    async def async_step(self, action):
        category, element_idx = action
        self.current_step += 1

        # 1. Usa os elementos capturados no passo anterior para executar a ação
        if not hasattr(self, "_last_elements"):
            self._last_elements = await self.browser.get_interactive_elements()

        success = await self.browser.execute_action(
            category, element_idx, self._last_elements
        )

        # 2. Captura novo estado (Screenshot + Hash)
        screenshot = await self.browser.capture_state()
        current_hash = self.encoder.get_hash(screenshot)

        # 3. Percepção (Novos elementos e Encoding)
        # Reutilizamos a chamada para evitar latência excessiva
        self._last_elements = await self.browser.get_interactive_elements()
        obs = self.encoder.encode(self._last_elements, self.previous_hash)

        # Reward Function Logic
        reward = 0
        terminated = False
        truncated = False

        # 1. +10 por atingir o objetivo (Simulado: se a URL mudou ou ação Finish escolhida)
        if category == 4:  # FINISH
            reward = 10
            terminated = True

        # 2. -1 por cada passo desnecessário
        reward -= 1

        # 3. -5 por entrar em um loop ou erro
        if current_hash in self.state_history:
            reward -= 5
            # Opcionalmente terminar se o loop persistir

        if not success:
            reward -= 5

        if self.current_step >= self.max_steps:
            truncated = True
            reward -= 5

        self.state_history.append(current_hash)
        self.previous_hash = current_hash

        return obs, reward, terminated, truncated, {}

    async def close(self):
        await self.browser.close()
