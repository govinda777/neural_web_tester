import numpy as np
import pytest
from pytest_bdd import scenario, given, when, then
from memory import SemanticMemory

@pytest.fixture
def memory_context():
    return {}

@scenario('../features/memory.feature', 'Identificação de novos estados visuais')
def test_semantic_memory_states():
    pass

@given('que a memória semântica esteja inicializada com limiar de 0.98', target_fixture="memory_context")
def step_init_memory():
    return {"memory": SemanticMemory(threshold=0.98)}

@when('um novo embedding de 1280 dimensões é processada')
def step_process_embedding(memory_context):
    v1 = np.random.rand(1280)
    memory_context["v1"] = v1
    memory_context["is_new_v1"] = memory_context["memory"].is_new_state(v1)

@then('ele deve ser identificado como um novo estado')
def step_check_new_state(memory_context):
    assert memory_context["is_new_v1"] is True

@then('se o mesmo embedding for processado novamente, ele deve ser identificado como um estado revisitado')
def step_check_revisited_state(memory_context):
    assert memory_context["memory"].is_new_state(memory_context["v1"]) is False

@then('um embedding levemente modificado deve ser identificado como um estado revisitado')
def step_check_noisy_state(memory_context):
    v1_noise = memory_context["v1"] + 0.0001 * np.random.rand(1280)
    assert memory_context["memory"].is_new_state(v1_noise) is False

@then('um embedding completamente diferente deve ser identificado como um novo estado')
def step_check_different_state(memory_context):
    v2 = np.random.rand(1280)
    # Ensure it is actually different
    from memory import cosine_similarity
    while cosine_similarity(memory_context["v1"], v2) > 0.98:
        v2 = np.random.rand(1280)
    assert memory_context["memory"].is_new_state(v2) is True
