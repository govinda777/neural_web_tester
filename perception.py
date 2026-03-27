import tensorflow as tf
import numpy as np
from PIL import Image
import io


def load_mobilenet_extractor():
    """Carrega o MobileNetV2 (Feature Extractor)."""
    # include_top=False e pooling='avg' garantem que teremos o vetor de características (embedding)
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights="imagenet", pooling="avg"
    )
    return base_model


def preprocess_image(screenshot_bytes):
    """Redimensiona e normaliza a imagem para 224x224."""
    img = Image.open(io.BytesIO(screenshot_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    # MobileNetV2 espera que os pixels estejam em [-1, 1]
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    # Adiciona a dimensão do batch
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def get_embedding(model, screenshot_bytes):
    """Gera um Vetor de Características (Embedding) da imagem."""
    processed_img = preprocess_image(screenshot_bytes)
    embedding = model.predict(processed_img)
    # Retorna o vetor normalizado (flatten)
    return embedding.flatten()
