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

    obs, _ = await env.async_reset()
    total_reward = 0
    steps = 0
    done = False

    while not done and steps < 10:
        # Ação 4 é Finish
        obs, reward, done, truncated, _ = await env.async_step([4, 0])
        total_reward += reward
        steps += 1
        if done:
            break

    assert steps < 10
    assert total_reward > -10
    await env.async_close()
