import pytest
import asyncio
import os
import hashlib
from environment import WebAgentEnv

@pytest.mark.asyncio
async def test_cycle_detection():
    """Valida se o ambiente penaliza ao entrar em loop visual."""
    url = f"file://{os.path.abspath('test_site.html')}"
    goal = "I want to test cycle detection"
    env = WebAgentEnv(url, goal, max_steps=10)

    await env._async_reset()

    # Passo 1: Captura o estado inicial (hash)
    obs1, reward1, done1, truncated1, _ = await env._async_step(2) # Scroll
    hash1 = env.last_state_hash

    # Passo 2: Volta para o topo (mesmo estado visual)
    await env.browser.page.evaluate("window.scrollTo(0, 0)")
    obs2, reward2, done2, truncated2, _ = await env._async_step(2) # Scroll novamente (para capturar o novo hash e verificar o ciclo)

    # Se o hash capturado no passo 2 for igual ao hash capturado no passo 1,
    # a recompensa deve ser penalizada em -5.0
    # Como enviamos 2 passos de scroll, a recompensa base de cada passo é -1.0

    # Na verdade, a detecção de ciclo no environment.py acontece assim:
    # if self.last_state_hash in self.state_history: reward -= 5.0

    assert any(reward == -6.0 for reward in [-1.0, reward1, reward2]) # reward = -1 (base) - 5 (ciclo)

    await env.browser.close()
