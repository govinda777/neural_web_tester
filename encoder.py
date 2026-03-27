import numpy as np
import tensorflow as tf
from perception import preprocess_image

class DOMEncoder:
    def __init__(self, max_elements=50):
        self.max_elements = max_elements

    def encode_elements(self, elements):
        """
        Transforma a lista de elementos interativos em tensores:
        - Coordenadas (x, y) normalizadas (2D vector)
        - Flags: isShadow, isIFrame (2D binary vector)
        - Adjacência: baseada no parentTag e siblingIndex (Matrix)
        """
        num_els = min(len(elements), self.max_elements)

        coords = np.zeros((self.max_elements, 2), dtype=np.float32)
        flags = np.zeros((self.max_elements, 2), dtype=np.float32)
        adj_matrix = np.zeros((self.max_elements, self.max_elements), dtype=np.float32)

        # Usamos um mapeamento simples para adjacência: se compartilham o mesmo pai, estão conectados
        parents = {}

        for i in range(num_els):
            el = elements[i]
            # Normalização simples (considerando 1280x720 fixo do BrowserManager)
            coords[i, 0] = el.get('x', 0) / 1280.0
            coords[i, 1] = el.get('y', 0) / 720.0

            flags[i, 0] = 1.0 if el.get('isShadow') else 0.0
            flags[i, 1] = 1.0 if el.get('isIFrame') else 0.0

            parent_key = (el['hierarchy']['parentTag'], el['isIFrame'])
            if parent_key not in parents:
                parents[parent_key] = []
            parents[parent_key].append(i)

        for members in parents.values():
            for i in members:
                for j in members:
                    if i != j:
                        adj_matrix[i, j] = 1.0

        return coords, flags, adj_matrix

    def get_full_state_tensor(self, elements, screenshot_bytes, prev_state_hash, gherkin_embedding):
        """
        Combina todas as percepções em um único tensor de estado.
        """
        coords, flags, adj = self.encode_elements(elements)

        # Flatten para simplificar a MLP inicial
        dom_vector = np.concatenate([coords.flatten(), flags.flatten(), adj.flatten()])

        # Hash do estado anterior como flag binária (simplificado: hash convertido em float normalizado)
        # Em um sistema real, poderíamos usar o hash para buscar na memória
        hash_val = int(prev_state_hash, 16) % 1000 / 1000.0 if prev_state_hash else 0.0

        # Combina com o embedding do Gherkin
        state_tensor = np.concatenate([
            dom_vector,
            [hash_val],
            gherkin_embedding
        ])

        return state_tensor.astype(np.float32)
