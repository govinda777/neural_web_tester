import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

class NeuralWebModel:
    def __init__(self, state_dim, action_space_size=5):
        """
        Arquitetura: MLP + LSTM
        - state_dim: Tamanho do vetor de entrada (DOM + Gherkin + Hash)
        - action_space_size: Número de ações (Click, Type, Scroll, Back, Finish)
        """
        self.state_dim = state_dim
        self.action_space_size = action_space_size

        # Carrega o Universal Sentence Encoder (Gherkin embedding)
        self.use_model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

        # Define a rede neural MLP + LSTM
        self.model = self._build_model()

    def _build_model(self):
        inputs = tf.keras.Input(shape=(None, self.state_dim)) # Sequence of steps

        x = tf.keras.layers.Dense(256, activation='relu')(inputs)
        x = tf.keras.layers.Dense(128, activation='relu')(x)

        # LSTM para manter o contexto da sequência de cliques
        x = tf.keras.layers.LSTM(64)(x)

        x = tf.keras.layers.Dense(32, activation='relu')(x)

        # Saída (Action Space) - Softmax para escolher a ação
        outputs = tf.keras.layers.Dense(self.action_space_size, activation='softmax')(x)

        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        return model

    def get_gherkin_embedding(self, text):
        """Transforma o passo Gherkin em um embedding (512-dim)."""
        return self.use_model([text]).numpy()[0]

    def predict_action(self, state_sequence):
        """
        Recebe uma sequência de estados [batch, seq_len, state_dim]
        e retorna as probabilidades das ações.
        """
        # Garante que state_sequence seja [1, seq_len, state_dim] para o modelo
        if len(state_sequence.shape) == 2:
            state_sequence = np.expand_dims(state_sequence, axis=0)

        return self.model.predict(state_sequence, verbose=0)[0]
