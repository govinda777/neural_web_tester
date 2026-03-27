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

    await env.async_reset()

    # Passo 1: Scroll
    obs1, reward1, done1, truncated1, _ = await env.async_step([2, 0])

    # Passo 2: Scroll novamente (após volta manual ao topo no environment)
    await env.browser.page.evaluate("window.scrollTo(0, 0)")
    obs2, reward2, done2, truncated2, _ = await env.async_step([2, 0])

    assert any(reward <= -6.0 for reward in [reward1, reward2])

    await env.async_close()
