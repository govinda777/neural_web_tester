import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

# Compartilhamento do singleton para otimizar memória e tempo de carregamento do modelo
_use_model = None

def get_use_model():
    """Retorna o Universal Sentence Encoder (USE) como um singleton."""
    global _use_model
    if _use_model is None:
        # Carrega o modelo v4 do TensorFlow Hub
        # Este modelo gera embeddings de 512 dimensões para frases
        _use_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
    return _use_model

class ReasoningModel(tf.keras.Model):
    def __init__(self, state_dim, action_dim=10, lstm_units=64):
        super(ReasoningModel, self).__init__()

        # 1. Entrada de Estado (Percepção + Memória)
        self.state_fc = tf.keras.layers.Dense(128, activation='relu')

        # 2. Entrada de Condicionamento (Embedding BDD Gherkin)
        self.bdd_fc = tf.keras.layers.Dense(128, activation='relu')

        # 3. Memória Recorrente (LSTM)
        # s_t + bdd_v
        self.lstm = tf.keras.layers.LSTM(lstm_units, return_sequences=False)
        self.dropout = tf.keras.layers.Dropout(0.2)

        # 4. Saída de Ações (Multi-head Softmax)
        # Cabeçalho 1: Escolher Categoria da Ação (Click, Type, Scroll, Back, Finish)
        self.action_category = tf.keras.layers.Dense(5, activation='softmax', name='category')

        # Cabeçalho 2: Escolher Elemento Alvo (ID do elemento retornado pelo Playwright/Encoder)
        self.target_element = tf.keras.layers.Dense(action_dim, activation='softmax', name='element')

    def call(self, inputs):
        """
        inputs: Dicionário com 'state' (tensor 1D) e 'bdd_embedding' (vetor USE 512)
        """
        state = inputs['state']
        bdd = inputs['bdd_embedding']

        # Processamento paralelo de features
        s_feat = self.state_fc(state)
        b_feat = self.bdd_fc(bdd)

        # Fusão de contexto
        # Expandimos dimensões para o LSTM esperar (batch, timesteps, features)
        combined = tf.concat([s_feat, b_feat], axis=-1)
        combined = tf.expand_dims(combined, axis=1) # Timesteps = 1 para este step

        x = self.lstm(combined)
        x = self.dropout(x)

        # Predição multi-objetivo
        cat_out = self.action_category(x)
        target_out = self.target_element(x)

        return cat_out, target_out

def load_reasoning_engine(state_dim, action_dim):
    """Factory para instanciar o modelo com as dimensões dinâmicas do encoder."""
    model = ReasoningModel(int(state_dim), int(action_dim))
    # Build inicial com tensores dummy
    dummy_state = tf.zeros((1, state_dim))
    dummy_bdd = tf.zeros((1, 512))
    model({'state': dummy_state, 'bdd_embedding': dummy_bdd})
    return model
