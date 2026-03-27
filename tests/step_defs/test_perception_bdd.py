import numpy as np
import pytest
import allure
from pytest_bdd import scenario, given, when, then
from perception import load_mobilenet_extractor, preprocess_image, get_embedding
from PIL import Image
import io

@pytest.fixture
def perception_context():
    return {}

@scenario('../features/perception.feature', 'Processamento de imagem e extração de características')
def test_perception_processing():
    pass

@given('que o extrator MobileNetV2 esteja carregado', target_fixture="perception_context")
def step_load_model():
    model = load_mobilenet_extractor()
    return {"model": model}

@when('uma captura de tela de 300x300 pixels é processada')
def step_process_image(perception_context):
    img = Image.new("RGB", (300, 300), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    screenshot_bytes = img_byte_arr.getvalue()
    allure.attach(screenshot_bytes, name="Imagem de Teste (Mock)", attachment_type=allure.attachment_type.PNG)

    processed = preprocess_image(screenshot_bytes)
    embedding = get_embedding(perception_context["model"], screenshot_bytes)

    perception_context["processed"] = processed
    perception_context["embedding"] = embedding

@then('o vetor de embedding resultante deve ter dimensão 1280')
def step_check_embedding_dim(perception_context):
    assert perception_context["embedding"].shape == (1280,)

@then('os valores do tensor de entrada devem estar normalizados entre -1 e 1')
def step_check_normalization(perception_context):
    processed = perception_context["processed"]
    assert np.max(processed) <= 1.0
    assert np.min(processed) >= -1.0
    assert processed.shape == (1, 224, 224, 3)
