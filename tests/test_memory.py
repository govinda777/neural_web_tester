import unittest
import numpy as np
from memory import cosine_similarity, SemanticMemory


class TestMemory(unittest.TestCase):
    def test_cosine_similarity(self):
        v1 = np.array([1, 0, 0])
        v2 = np.array([1, 0, 0])
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)

        v3 = np.array([0, 1, 0])
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0)

        v4 = np.array([-1, 0, 0])
        self.assertAlmostEqual(cosine_similarity(v1, v4), -1.0)

    def test_semantic_memory(self):
        memory = SemanticMemory(threshold=0.98)
        v1 = np.random.rand(1280)

        # Primeiro estado é sempre novo
        self.assertTrue(memory.is_new_state(v1))

        # Mesmo estado não deve ser novo
        self.assertFalse(memory.is_new_state(v1))

        # Estado levemente modificado deve ser detectado como já visitado
        v1_noise = v1 + 0.001 * np.random.rand(1280)
        self.assertFalse(memory.is_new_state(v1_noise))

        # Estado completamente diferente deve ser novo
        v2 = np.random.rand(1280)
        while cosine_similarity(v1, v2) > 0.98:
            v2 = np.random.rand(1280)
        self.assertTrue(memory.is_new_state(v2))


if __name__ == "__main__":
    unittest.main()
