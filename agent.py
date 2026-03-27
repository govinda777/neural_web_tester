import argparse
import asyncio
import numpy as np
import os
from dotenv import load_dotenv
from environment import WebAgentEnv
from model import NeuralWebModel
from report import ReportGenerator, Evidence


class NeuralAgent:
    def __init__(self, url, gherkin_goal, token=None, max_steps=10):
        self.url = url
        self.goal = gherkin_goal
        self.token = token
        self.max_steps = max_steps

        # RL Environment
        self.env = WebAgentEnv(url, gherkin_goal, max_steps=max_steps)

        # Neural Model
        self.model = NeuralWebModel(state_dim=self.env.state_dim)

        self.reporter = ReportGenerator()
        self.step_count = 0
        self.state_sequence = []

    async def explore(self):
        """Loop de exploração do agente usando RL."""
        print(f"Iniciando exploração RL em: {self.url}")
        print(f"Objetivo Gherkin: {self.goal}")

        obs, _ = await self.env.async_reset()
        self.state_sequence.append(obs)

        previous_step_count = None

        try:
            while self.step_count < self.max_steps:
                self.step_count += 1
                print(f"--- Passo {self.step_count} ---")

                # Predição do modelo (Policy)
                seq_tensor = np.array(self.state_sequence)
                action_probs, element_probs = self.model.predict_action(seq_tensor)

                action_cat = np.argmax(action_probs)
                element_idx = np.argmax(element_probs)

                action_names = ["Click", "Type", "Scroll", "Back", "Finish"]
                print(f"Ação: {action_names[action_cat]} | Elemento: {element_idx}")

                # Executa ação no ambiente
                obs, reward, done, truncated, _ = await self.env.async_step([action_cat, element_idx])
                self.state_sequence.append(obs)

                # Coleta evidências
                screenshot_bytes = await self.env.browser.capture_state()
                current_url = self.env.browser.page.url

                state_type = "SUCCESS"
                if reward < -2:
                    state_type = "BUG"
                elif reward < 0 and reward > -2:
                    state_type = "REVISITED"

                evidence = Evidence(
                    url=current_url,
                    screenshot_bytes=screenshot_bytes,
                    console_logs=list(self.env.browser.console_logs),
                    network_errors=list(self.env.browser.network_errors),
                    state_type=state_type,
                    step=self.step_count,
                )
                self.reporter.add_evidence(evidence)

                if previous_step_count is not None:
                    self.reporter.add_edge(
                        previous_step_count, self.step_count, f"{action_names[action_cat]} (idx: {element_idx})"
                    )

                previous_step_count = self.step_count

                if done or truncated:
                    print("Exploração concluída.")
                    break

        finally:
            self.reporter.generate()
            await self.env.async_close()
            print("Exploração finalizada.")


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Neural Web Tester - CLI do Agente Neural (RL Engine)"
    )
    parser.add_argument("--url", required=True, help="URL inicial para exploração")
    parser.add_argument(
        "--goal",
        default="When I explore the website, Then I should find relevant information",
        help="Objetivo BDD (Gherkin)"
    )
    parser.add_argument(
        "--token",
        default=os.getenv("AGENT_TOKEN"),
        help="Bearer JWT Token para injeção",
    )
    parser.add_argument(
        "--steps", type=int, default=10, help="Número máximo de passos de exploração"
    )

    args = parser.parse_args()

    agent = NeuralAgent(
        url=args.url,
        gherkin_goal=args.goal,
        token=args.token,
        max_steps=args.steps
    )
    asyncio.run(agent.explore())


if __name__ == "__main__":
    main()
