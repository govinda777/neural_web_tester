import pytest
import asyncio
import os
from pytest_bdd import scenario, given, when, then
from agent import NeuralAgent
from playwright.async_api import async_playwright

@scenario('../features/dashboard_ui.feature', 'Validar que o Dashboard exibe dados após a execução do agente')
def test_dashboard_ui_e2e():
    pass

@given("que o servidor de telemetria e o frontend estão rodando")
def services_up():
    pass

@when("o agente completa uma navegação de 2 passos", target_fixture="session_id")
def run_agent_cuj():
    url = f"file://{os.getcwd()}/test_site.html"
    agent = NeuralAgent(url=url, bdd_step="Navegar no Dashboard", max_steps=2)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(agent.run())
    return agent.telemetry.session_id

@then('eu acesso o dashboard em "http://localhost:3000"', target_fixture="dashboard_page")
def access_dashboard():
    loop = asyncio.get_event_loop()

    async def _access():
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("http://localhost:3000")
        await page.wait_for_timeout(3000)
        return {"page": page, "browser": browser, "pw": pw}

    return loop.run_until_complete(_access())

@then("eu devo ver o screenshot da página no componente LivePreview")
def verify_screenshot(dashboard_page):
    page = dashboard_page["page"]
    loop = asyncio.get_event_loop()

    async def _verify():
        img = page.locator('img[alt="Agent View"]')
        if not await img.is_visible():
            pytest.fail("Screenshot do agente não encontrado no LivePreview")
        src = await img.get_attribute("src")
        assert src.startswith("data:image/png;base64,"), "Screenshot não contém dados válidos"

    loop.run_until_complete(_verify())

@then("eu devo ver as barras de importância de features")
def verify_features(dashboard_page):
    page = dashboard_page["page"]
    loop = asyncio.get_event_loop()

    async def _verify():
        bars = page.locator('div.bg-blue-500, div.bg-red-400')
        count = await bars.count()
        assert count > 0, "Nenhuma barra de importância de features encontrada"

    loop.run_until_complete(_verify())

@then("o mapa mental de estados deve conter pelo menos 2 nós")
def verify_state_graph(dashboard_page):
    page = dashboard_page["page"]
    loop = asyncio.get_event_loop()

    async def _verify():
        nodes = page.locator('.react-flow__node')
        count = await nodes.count()

        browser = dashboard_page["browser"]
        pw = dashboard_page["pw"]
        await browser.close()
        await pw.stop()

        assert count >= 2, f"Mapa mental contém apenas {count} nós, esperado pelo menos 2"

    loop.run_until_complete(_verify())
