import numpy as np
import logging

logger = logging.getLogger(__name__)


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
        logger.info("Analisando novo estado visual na Memória Semântica.")
        if not self.embeddings:
            logger.info("Memória vazia. Primeiro estado registrado.")
            self.embeddings.append(new_embedding)
            return True

        for idx, existing_embedding in enumerate(self.embeddings):
            similarity = cosine_similarity(new_embedding, existing_embedding)
            if similarity > self.threshold:
                logger.info(f"Estado visual já visitado. Similaridade {similarity:.4f} com estado #{idx}.")
                # O estado já foi visitado (muito similar)
                return False

        # O estado é novo, adiciona à memória
        logger.info(f"Novo estado visual detectado. Adicionando à memória (Total: {len(self.embeddings) + 1}).")
        self.embeddings.append(new_embedding)
        return True
