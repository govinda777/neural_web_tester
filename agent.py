import argparse
import asyncio
import random
import hashlib
import os
import logging
from dotenv import load_dotenv
from perception import load_mobilenet_extractor, get_embedding
from memory import SemanticMemory
from navigation import BrowserManager
from report import ReportGenerator, Evidence


logger = logging.getLogger(__name__)


class NeuralAgent:
    def __init__(self, url, token=None, max_steps=10):
        self.url = url
        self.token = token
        self.max_steps = max_steps
        self.memory = SemanticMemory(threshold=0.98)
        self.model = load_mobilenet_extractor()
        self.browser = BrowserManager(token=token)
        self.reporter = ReportGenerator()
        self.step_count = 0
        self.state_history = []  # Lista de IDs de estados visitados
        self.tried_actions = {}  # state_id -> set of action_identifiers

    def _get_state_id(self, embedding):
        """Gera um ID único (curto) para o estado baseado no embedding."""
        return hashlib.md5(embedding.tobytes()).hexdigest()[:8]

    async def explore(self):
        """Loop de exploração do agente."""
        logger.info(f"Iniciando exploração autônoma em: {self.url}")
        await self.browser.start(self.url)

        previous_step_count = None

        try:
            while self.step_count < self.max_steps:
                self.step_count += 1
                logger.info(f"Iniciando Passo {self.step_count}/{self.max_steps}")

                # Captura o estado atual
                screenshot_bytes = await self.browser.capture_state()
                current_url = self.browser.page.url

                # Percepção: Gera o embedding
                logger.info("Extraindo embeddings na camada MobileNetV2...")
                embedding = await asyncio.to_thread(
                    get_embedding, self.model, screenshot_bytes
                )

                # Memória Semântica: Verifica se é um estado novo
                # Aqui usamos a nossa memória semântica para ver se o estado visual é conhecido
                is_new = self.memory.is_new_state(embedding)

                # Coleta evidências
                state_type = "SUCCESS"
                if self.browser.network_errors or any(
                    "error" in log.lower() for log in self.browser.console_logs
                ):
                    state_type = "BUG"
                    logger.warning(f"Passo {self.step_count}: BUG detectado (Erro de console ou rede)!")
                elif not is_new:
                    state_type = "REVISITED"
                    logger.info(f"Passo {self.step_count}: Estado visual já conhecido.")

                evidence = Evidence(
                    url=current_url,
                    screenshot_bytes=screenshot_bytes,
                    console_logs=list(self.browser.console_logs),
                    network_errors=list(self.browser.network_errors),
                    state_type=state_type,
                    step=self.step_count,
                )
                self.reporter.add_evidence(evidence)

                # Limpa logs para o próximo passo
                self.browser.console_logs.clear()
                self.browser.network_errors.clear()

                # Navegação: Extrai e prioriza ações
                actions = await self.browser.get_interactive_elements()

                if not actions:
                    logger.warning("Nenhum elemento interativo encontrado. Retornando à URL inicial.")
                    await self.browser.page.goto(self.url)
                    previous_step_count = None
                    continue

                # Tenta encontrar uma ação que ainda não foi tentada neste estado (aproximadamente)
                # Como o estado é visual, usamos o embedding para identificar o estado
                state_id = self._get_state_id(embedding)
                if state_id not in self.tried_actions:
                    self.tried_actions[state_id] = set()

                # Filtra ações já tentadas
                untried_actions = [
                    a for a in actions if a["text"] not in self.tried_actions[state_id]
                ]

                if not untried_actions:
                    logger.info("Todas as ações conhecidas neste estado já foram tentadas. Resetando para a home.")
                    await self.browser.page.goto(self.url)
                    previous_step_count = None
                    continue

                # Escolha entre as melhores ações não tentadas
                top_untried = untried_actions[:3]
                best_action = random.choice(top_untried)

                self.tried_actions[state_id].add(best_action["text"])

                logger.info(f"Decidindo ação: Executando '{best_action['text']}' em elemento <{best_action['tag']}>.")

                # Grava a aresta no grafo
                if previous_step_count is not None:
                    self.reporter.add_edge(
                        previous_step_count, self.step_count, best_action["text"]
                    )

                try:
                    # Tenta clicar no elemento
                    await best_action["element"].click()
                    # Espera um pouco para a rede estabilizar
                    await self.browser.page.wait_for_load_state(
                        "networkidle", timeout=5000
                    )
                    previous_step_count = self.step_count
                except Exception as e:
                    logger.error(f"Erro ao interagir com o elemento: {e}")
                    await self.browser.page.goto(self.url)
                    previous_step_count = None

        finally:
            self.reporter.generate()
            await self.browser.close()
            logger.info("Exploração finalizada com sucesso.")


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Neural Web Tester - CLI do Agente Neural"
    )
    parser.add_argument("--url", required=True, help="URL inicial para exploração")
    parser.add_argument(
        "--token",
        default=os.getenv("AGENT_TOKEN"),
        help="Bearer JWT Token para injeção",
    )
    parser.add_argument(
        "--steps", type=int, default=10, help="Número máximo de passos de exploração"
    )

    args = parser.parse_args()

    agent = NeuralAgent(url=args.url, token=args.token, max_steps=args.steps)
    asyncio.run(agent.explore())


if __name__ == "__main__":
    main()
