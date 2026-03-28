import numpy as np
import hashlib


class DOMEncoder:
    def __init__(self, max_elements=50):
        self.max_elements = max_elements

    def encode(self, elements_metadata, previous_state_hash=None):
        """
        Transforma os metadados dos elementos e o estado anterior em um tensor.

        elements_metadata: Lista de dicionários com:
            - x, y (coordenadas relativas 0-1)
            - is_shadow (bool)
            - is_iframe (bool)
            - parent_index (int ou None)
        """
        num_elements = min(len(elements_metadata), self.max_elements)

        # 1. Matriz de Adjacência (Baseada em Relacionamento Pai-Filho)
        adj_matrix = np.zeros((self.max_elements, self.max_elements), dtype=np.float32)

        # 2. Vetor de Coordenadas e Flags (x, y, is_shadow, is_iframe)
        features = np.zeros((self.max_elements, 4), dtype=np.float32)

        for i in range(num_elements):
            el = elements_metadata[i]
            features[i] = [
                el.get("x", 0),
                el.get("y", 0),
                float(el.get("is_shadow", False)),
                float(el.get("is_iframe", False)),
            ]

            parent_idx = el.get("parent_index")
            if parent_idx is not None and parent_idx < self.max_elements:
                adj_matrix[parent_idx, i] = 1.0
                adj_matrix[i, parent_idx] = (
                    1.0  # Grafo não direcionado para facilitar propagação
                )

        # 3. Hash do estado anterior (Memory Component)
        # Transformamos o hash (hex) em um vetor numérico simples
        memory_vector = np.zeros((32,), dtype=np.float32)
        if previous_state_hash:
            # Converte partes do SHA-256 (32 bytes) em floats
            hash_bytes = bytes.fromhex(previous_state_hash)
            memory_vector = (
                np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32) / 255.0
            )

        # Flatten e concatenação para formar o vetor de estado 's'
        state_tensor = np.concatenate(
            [adj_matrix.flatten(), features.flatten(), memory_vector]
        )

        return state_tensor

    @staticmethod
    def get_hash(screenshot_bytes):
        """Gera um hash SHA-256 do estado visual."""
        return hashlib.sha256(screenshot_bytes).hexdigest()
