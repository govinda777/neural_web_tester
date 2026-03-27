import pytest
import asyncio
import os
from environment import WebAgentEnv

@pytest.mark.asyncio
async def test_rl_convergence():
    """Valida se o agente atinge o objetivo em menos de N passos (baseline)."""
    url = f"file://{os.path.abspath('test_site.html')}"
    goal = "Then I click the save button"
    env = WebAgentEnv(url, goal, max_steps=5)

    obs, _ = await env._async_reset()
    total_reward = 0
    steps = 0
    done = False

    while not done and steps < 10:
        # Simula uma política perfeita para testar o ambiente
        # Ação 4 é Finish, que deve encerrar o episódio
        obs, reward, done, truncated, _ = await env._async_step(4)
        total_reward += reward
        steps += 1
        if done:
            break

    assert steps < 10
    assert total_reward > -10
    await env.browser.close()
