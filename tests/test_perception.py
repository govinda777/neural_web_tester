import unittest
import numpy as np
from perception import load_mobilenet_extractor, preprocess_image, get_embedding
from perception import load_mobilenet_extractor, preprocess_image, get_embedding
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestPerception(unittest.TestCase):
    def setUp(self):
        logger.info("Carregando MobileNet Extractor e preparando dados fictícios...")
        self.model = load_mobilenet_extractor()
        # Cria uma imagem fictícia de 300x300
        img = Image.new("RGB", (300, 300), color="red")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        self.screenshot_bytes = img_byte_arr.getvalue()
        logger.info("Setup concluído para TestPerception.")

    def test_preprocess_image(self):
        logger.info("Executando teste no preprocessamento de imagem...")
        processed = preprocess_image(self.screenshot_bytes)
        self.assertEqual(processed.shape, (1, 224, 224, 3))
        self.assertTrue(np.max(processed) <= 1.0)
        self.assertTrue(np.min(processed) >= -1.0)
        logger.info(f"Pré-processamento retornou os dados no formato esperado {processed.shape}.")

    def test_get_embedding(self):
        logger.info("Testando extração do Embedding com a MobileNetV2...")
        embedding = get_embedding(self.model, self.screenshot_bytes)
        # O MobileNetV2 com pooling='avg' e sem top deve retornar 1280 features
        self.assertEqual(embedding.shape, (1280,))
        logger.info(f"Embeddings extraídos com sucesso na dimensão {embedding.shape}!")


if __name__ == "__main__":
    unittest.main()
