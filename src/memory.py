import numpy as np


def cosine_similarity(v1, v2):
    """Calcula a similaridade de cosseno entre dois vetores."""
    # Garante que os vetores sejam numpy arrays
    v1 = np.asarray(v1)
    v2 = np.asarray(v2)

    # Produto escalar dividido pela multiplicação das normas
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    # Evita divisão por zero
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


class SemanticMemory:
    def __init__(self, threshold=0.98):
        """Inicializa a memória semântica com um limiar de similaridade."""
        self.embeddings = []
        self.threshold = threshold

    def is_new_state(self, new_embedding):
        """Verifica se o novo estado é diferente dos estados já visitados."""
        if not self.embeddings:
            self.embeddings.append(new_embedding)
            return True

        for existing_embedding in self.embeddings:
            similarity = cosine_similarity(new_embedding, existing_embedding)
            if similarity > self.threshold:
                # O estado já foi visitado (muito similar)
                return False

        # O estado é novo, adiciona à memória
        self.embeddings.append(new_embedding)
        return True
