import unittest
import numpy as np
import logging
from memory import cosine_similarity, SemanticMemory

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestMemory(unittest.TestCase):
    def test_cosine_similarity(self):
        logger.info(
            "Testando similaridade do cosseno com vetores idênticos e diferentes."
        )
        v1 = np.array([1, 0, 0])
        v2 = np.array([1, 0, 0])
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)

        v3 = np.array([0, 1, 0])
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0)

        v4 = np.array([-1, 0, 0])
        self.assertAlmostEqual(cosine_similarity(v1, v4), -1.0)

    def test_semantic_memory(self):
        logger.info("Inicializando SemanticMemory com limiar de 0.98 para os testes...")
        memory = SemanticMemory(threshold=0.98)
        v1 = np.random.rand(1280)

        # Primeiro estado é sempre novo
        self.assertTrue(memory.is_new_state(v1))
        logger.info("Novo estado visual registrado com sucesso.")

        # Mesmo estado não deve ser novo
        logger.info("Testando novamente o mesmo estado, não deve ser considerado novo.")
        self.assertFalse(memory.is_new_state(v1))

        # Estado levemente modificado deve ser detectado como já visitado
        v1_noise = v1 + 0.001 * np.random.rand(1280)
        self.assertFalse(memory.is_new_state(v1_noise))
        logger.info(
            "Estado com ruído leve ignorado com sucesso (considerado revisitado)."
        )

        # Estado completamente diferente deve ser novo
        logger.info("Testando estado visual completamente diferente.")
        v2 = np.random.rand(1280)
        while cosine_similarity(v1, v2) > 0.98:
            v2 = np.random.rand(1280)
        self.assertTrue(memory.is_new_state(v2))
        logger.info("Novo estado perfeitamente identificado!")


if __name__ == "__main__":
    unittest.main()
