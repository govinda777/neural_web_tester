import asyncio
import os
import pytest
import allure
from pytest_bdd import scenario, given, when, then, parsers
from navigation import BrowserManager

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def browser_manager():
    return BrowserManager()

@pytest.fixture
def context(event_loop, browser_manager):
    ctx = {"browser": browser_manager, "loop": event_loop}
    yield ctx
    event_loop.run_until_complete(browser_manager.close())

@given(parsers.parse('que o agente acesse a página de dashboard "{file_name}"'))
def step_open_page(context, file_name):
    test_file_path = f"file://{os.path.abspath(file_name)}"
    context["loop"].run_until_complete(context["browser"].start(test_file_path))

@when('ele analisar o DOM em busca de elementos interativos')
def step_analyze_dom(context):
    actions = context["loop"].run_until_complete(context["browser"].get_interactive_elements())
    context["actions"] = actions

@then(parsers.parse('ele deve localizar o botão "{button_text}" com prioridade {priority:d}'))
def step_check_button_priority(context, button_text, priority):
    actions = context["actions"]
    btn = next((a for a in actions if button_text.lower() in a["text"].lower()), None)
    assert btn is not None, f"Botão '{button_text}' não encontrado"
    assert btn["priority"] == priority, f"Prioridade esperada {priority}, mas obteve {btn['priority']}"

@then(parsers.parse('ele deve ignorar o link externo para o "{link_name}"'))
def step_check_ignored_link(context, link_name):
    actions = context["actions"]
    link = next((a for a in actions if link_name.lower() in a["text"].lower()), None)
    assert link is None, f"Link '{link_name}' não deveria ter sido capturado"

@then('ele deve capturar um erro de console planejado')
def step_check_console_error(context):
    logs = context["browser"].console_logs
    assert any("Este é um erro de console planejado!" in log for log in logs), "Erro de console não capturado"

@scenario('../features/navigation.feature', 'Identificação de elementos e priorização')
def test_navigation_and_prioritization():
    pass
