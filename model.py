import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

_shared_use_model = None

def get_use_model():
    global _shared_use_model
    if _shared_use_model is None:
        _shared_use_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
    return _shared_use_model

class NeuralWebModel:
    def __init__(self, state_dim, action_space_size=5, max_elements=50):
        """
        Arquitetura: MLP + LSTM
        - state_dim: Tamanho do vetor de entrada (DOM + Gherkin + Hash)
        - action_space_size: Categorias de ações (Click, Type, Scroll, Back, Finish)
        - max_elements: Número máximo de elementos para seleção (Click(id), Type(id))
        """
        self.state_dim = state_dim
        self.action_space_size = action_space_size
        self.max_elements = max_elements

        # Compartilha o Universal Sentence Encoder
        self.use_model = get_use_model()

        # Define a rede neural MLP + LSTM
        self.model = self._build_model()

    def _build_model(self):
        inputs = tf.keras.Input(shape=(None, self.state_dim)) # Sequence of steps

        x = tf.keras.layers.Dense(256, activation='relu')(inputs)
        x = tf.keras.layers.Dense(128, activation='relu')(x)

        # LSTM para manter o contexto da sequência de cliques
        x = tf.keras.layers.LSTM(64)(x)

        # Saída 1: Categoria de Ação (Softmax)
        action_cat = tf.keras.layers.Dense(self.action_space_size, activation='softmax', name='action_cat')(x)

        # Saída 2: Seleção de Elemento (Softmax para os top N elementos)
        element_idx = tf.keras.layers.Dense(self.max_elements, activation='softmax', name='element_idx')(x)

        model = tf.keras.Model(inputs=inputs, outputs=[action_cat, element_idx])
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        return model

    def get_gherkin_embedding(self, text):
        """Transforma o passo Gherkin em um embedding (512-dim)."""
        return self.use_model([text]).numpy()[0]

    def predict_action(self, state_sequence):
        """
        Retorna as probabilidades das categorias de ações e os índices dos elementos.
        """
        if len(state_sequence.shape) == 2:
            state_sequence = np.expand_dims(state_sequence, axis=0)

        action_probs, element_probs = self.model.predict(state_sequence, verbose=0)
        return action_probs[0], element_probs[0]
