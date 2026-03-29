import argparse
import asyncio
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from model import load_reasoning_engine, get_use_model
from web_agent_env import WebAgentEnv
from report import ReportGenerator, Evidence
from telemetry import TelemetryManager


class NeuralAgent:
    def __init__(self, url, bdd_step="Navegar no site", token=None, max_steps=10):
        self.url = url
        self.bdd_step = bdd_step
        self.token = token
        self.max_steps = max_steps

        # Inicializa Ambiente Gymnasium
        self.env = WebAgentEnv(url, bdd_step, token=token, max_steps=max_steps)

        # Inicializa Modelos de IA
        self.state_dim = self.env.observation_space.shape[0]
        self.action_dim = self.env.action_space.nvec[1]  # Numero de elementos alvo (50)
        self.model = load_reasoning_engine(self.state_dim, self.action_dim)
        self.use_model = get_use_model()

        self.reporter = ReportGenerator()
        self.telemetry = TelemetryManager()

    async def run(self, train=False):
        """Loop principal do agente usando a política da rede neural."""
        print(f"Iniciando Agente RL em: {self.url}")
        print(f"Objetivo Gherkin: {self.bdd_step}")

        # 0. Inicializa Telemetria
        await self.telemetry.connect()
        await self.telemetry.init_session(self.url, self.bdd_step)

        # 1. Gera embedding do objetivo (When Gherkin)
        bdd_embedding = self.use_model([self.bdd_step]).numpy()

        # 2. Reset do Ambiente
        obs, info = await self.env.async_reset()

        # Envia estado inicial para telemetria
        screenshot = await self.env.browser.capture_state()
        await self.telemetry.send_step(
            step_number=0,
            state_hash=self.env.previous_hash,
            screenshot_bytes=screenshot,
            action=None,
            observation={
                "top_candidates": self._get_top_candidates(tf.zeros((1, self.action_dim)), self.env._last_elements),
                "features_weights": {} # Reset não tem pesos de decisão ainda
            }
        )

        terminated = False
        truncated = False
        step = 0

        optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)

        try:
            while not (terminated or truncated):
                step += 1
                print(f"--- Passo {step} ---")

                # Prepara entrada para a rede
                obs_tensor = tf.convert_to_tensor(
                    obs[np.newaxis, ...], dtype=tf.float32
                )
                bdd_tensor = tf.convert_to_tensor(bdd_embedding, dtype=tf.float32)

                # 3. Inferência: Escolha da Ação
                cat_probs, target_probs = self.model(
                    {"state": obs_tensor, "bdd_embedding": bdd_tensor}
                )

                # Epsilon-greedy para exploração básica durante o teste
                if np.random.rand() < 0.2:
                    category = np.random.randint(5)
                    target_idx = np.random.randint(self.action_dim)
                else:
                    category = np.argmax(cat_probs.numpy()[0])
                    target_idx = np.argmax(target_probs.numpy()[0])

                action = [category, target_idx]

                print(f"Ação Escolhida: Cat={category}, ElementID={target_idx}")

                # 4. Execução no Ambiente
                obs, reward, terminated, truncated, info = await self.env.async_step(
                    action
                )

                # 5. Coleta de Metadados para Telemetria
                # Calculamos a importância das features de forma simplificada:
                # Pegamos o vetor de estado do elemento escolhido e multiplicamos pelos pesos da camada densa
                # (Simplificação: apenas os valores brutos para esta fase)
                feature_importance = self._get_feature_importance(obs, target_idx)

                # Envia para o Dashboard
                screenshot = await self.env.browser.capture_state()
                await self.telemetry.send_step(
                    step_number=step,
                    state_hash=self.env.previous_hash,
                    screenshot_bytes=screenshot,
                    action={
                        "element_id": int(target_idx),
                        "type": ["CLICK", "TYPE", "SCROLL", "BACK", "FINISH"][category],
                        "confidence": float(cat_probs.numpy()[0][category] * target_probs.numpy()[0][target_idx])
                    },
                    observation={
                        "top_candidates": self._get_top_candidates(target_probs, self.env._last_elements),
                        "features_weights": feature_importance
                    }
                )

                # 4.1 Update básico (online learning simulado)
                if train:
                    with tf.GradientTape() as tape:
                        p_cat, p_target = self.model(
                            {"state": obs_tensor, "bdd_embedding": bdd_tensor}
                        )
                        loss = -tf.math.log(p_cat[0, category]) - tf.math.log(
                            p_target[0, target_idx]
                        )

                    grads = tape.gradient(loss * reward, self.model.trainable_variables)
                    optimizer.apply_gradients(
                        zip(grads, self.model.trainable_variables)
                    )

                # 6. Coleta de Evidências (Relatório Estático)
                evidence = Evidence(
                    url=self.env.browser.page.url,
                    screenshot_bytes=screenshot,
                    console_logs=list(self.env.browser.console_logs),
                    network_errors=list(self.env.browser.network_errors),
                    state_type="SUCCESS"
                    if reward > 0
                    else "LOOP"
                    if reward < -1
                    else "REVISITED",
                    step=step,
                )
                self.reporter.add_evidence(evidence)

                print(f"Recompensa: {reward}")

        finally:
            self.reporter.generate()
            await self.telemetry.close()
            await self.env.close()
            print("Execução finalizada.")

    def _get_top_candidates(self, target_probs, elements):
        probs = target_probs.numpy()[0]
        top_indices = np.argsort(probs)[-5:][::-1]
        candidates = []
        for idx in top_indices:
            if idx < len(elements):
                el = elements[idx]
                candidates.append({
                    "id": int(idx),
                    "prob": float(probs[idx]),
                    "coords": [el["x"], el["y"], el.get("w", 0.05), el.get("h", 0.02)],
                    "label": f"{el['tag']} {el['text'][:10]}"
                })
        return candidates

    def _get_feature_importance(self, obs, element_idx):
        # O encoder coloca features em: adj_matrix(2500) + features(200) + memory(32)
        # No encoder.py, as features são concatenadas APÓS a adj_matrix.
        # features: x, y, is_shadow, is_iframe para cada um dos 50 elementos.
        if element_idx < 50:
            start = 2500 + element_idx * 4
            # Garantir que não passamos do tamanho do vetor (2500 + 200 = 2700)
            feat_values = obs[start : start + 4]
            return {
                "pos_x": float(feat_values[0]),
                "pos_y": float(feat_values[1]),
                "is_shadow": float(feat_values[2]),
                "is_iframe": float(feat_values[3]),
            }
        return {}


async def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Neural Web Tester CLI")
    parser.add_argument("--url", required=True, help="URL inicial")
    parser.add_argument(
        "--bdd", default="Ao clicar em Salvar", help="Texto do passo 'When' Gherkin"
    )
    parser.add_argument("--steps", type=int, default=10, help="Passos máximos")

    args = parser.parse_args()

    agent = NeuralAgent(url=args.url, bdd_step=args.bdd, max_steps=args.steps)
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
