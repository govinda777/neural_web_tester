import pytest
import sqlite3
import os
import asyncio
from pytest_bdd import scenario, given, when, then
from agent import NeuralAgent
from observability.server import init_db, save_session, save_step
import json

# Fixture para garantir que o banco está limpo antes dos testes
@pytest.fixture(scope="module", autouse=True)
def clean_db():
    if os.path.exists("telemetry.db"):
        os.remove("telemetry.db")
    init_db()
    yield

@scenario('../features/observability.feature', 'O agente inicia uma sessão e envia telemetria após uma ação')
def test_observability_flow():
    pass

@given("que o servidor de telemetria está ativo")
def server_active():
    pass

@when('o agente inicia um teste na URL "file:///app/test_site.html" com objetivo "Testar Observabilidade"', target_fixture="agent_context")
def start_agent_test():
    agent = NeuralAgent(url="file:///app/test_site.html", bdd_step="Testar Observabilidade", max_steps=1)
    # Mock do _send para salvar diretamente no SQLite
    async def mock_send(message):
        if message["type"] == "init_session":
            save_session(message["data"])
        elif message["type"] == "step_update":
            save_step(message["data"])

    agent.telemetry._send = mock_send
    return {"agent": agent, "session_id": agent.telemetry.session_id}

@when("o agente executa 1 passo")
def execute_one_step(agent_context):
    agent = agent_context["agent"]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(agent.run())

@then("a sessão deve ser registrada no banco de dados SQLite")
def verify_session_in_db(agent_context):
    conn = sqlite3.connect("telemetry.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sessions WHERE id = ?", (agent_context["session_id"],))
    result = cursor.fetchone()
    conn.close()
    assert result is not None, f"Sessão {agent_context['session_id']} não encontrada no banco."

@then("pelo menos 1 passo deve conter metadados de confiança e features")
def verify_steps_in_db(agent_context):
    conn = sqlite3.connect("telemetry.db")
    cursor = conn.cursor()
    # Pega o step_number 1 (o primeiro passo real após o reset)
    cursor.execute("SELECT action_json, observation_json FROM steps WHERE session_id = ? AND step_number = 1", (agent_context["session_id"],))
    result = cursor.fetchone()
    conn.close()

    assert result is not None, "Passo 1 não registrado no banco."
    action = json.loads(result[0])
    observation = json.loads(result[1])

    assert "confidence" in action
    assert "features_weights" in observation
    assert "top_candidates" in observation
