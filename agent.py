import argparse
import asyncio
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from model import load_reasoning_engine, get_use_model
from web_agent_env import WebAgentEnv
from report import ReportGenerator, Evidence


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

    async def run(self, train=False):
        """Loop principal do agente usando a política da rede neural."""
        print(f"Iniciando Agente RL em: {self.url}")
        print(f"Objetivo Gherkin: {self.bdd_step}")

        # 1. Gera embedding do objetivo (When Gherkin)
        bdd_embedding = self.use_model([self.bdd_step]).numpy()

        # 2. Reset do Ambiente
        obs, info = await self.env.async_reset()

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

                # 5. Coleta de Evidências (Dashboard do Agente)
                screenshot = await self.env.browser.capture_state()
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
            await self.env.close()
            print("Execução finalizada.")


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
