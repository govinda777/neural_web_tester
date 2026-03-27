import argparse
import asyncio
import random
from perception import load_mobilenet_extractor, get_embedding
from memory import SemanticMemory
from navigation import BrowserManager
from report import ReportGenerator, Evidence

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
        self.state_map = {} # embedding_hash -> step_id

    def _get_embedding_hash(self, embedding):
        return hash(tuple(embedding.round(4)))

    async def explore(self):
        """Loop de exploração do agente."""
        print(f"Iniciando exploração em: {self.url}")
        await self.browser.start(self.url)

        previous_step_id = None

        try:
            while self.step_count < self.max_steps:
                self.step_count += 1
                current_step_id = self.step_count
                print(f"--- Passo {current_step_id} ---")

                # Captura o estado atual
                screenshot_bytes = await self.browser.capture_state()
                current_url = self.browser.page.url

                # Percepção: Gera o embedding
                embedding = await asyncio.to_thread(get_embedding, self.model, screenshot_bytes)
                emb_hash = self._get_embedding_hash(embedding)

                # Memória Semântica: Verifica se é um estado novo
                is_new = self.memory.is_new_state(embedding)

                # Coleta evidências
                state_type = "SUCCESS"
                if self.browser.network_errors or any("error" in log.lower() for log in self.browser.console_logs):
                    state_type = "BUG"
                elif not is_new:
                    state_type = "REVISITED"
                    print("Estado já visitado.")

                evidence = Evidence(
                    url=current_url,
                    screenshot_bytes=screenshot_bytes,
                    console_logs=list(self.browser.console_logs),
                    network_errors=list(self.browser.network_errors),
                    state_type=state_type,
                    step=current_step_id
                )
                self.reporter.add_evidence(evidence)

                # Limpa logs para o próximo passo
                self.browser.console_logs.clear()
                self.browser.network_errors.clear()

                # Mapeamento para o grafo
                if emb_hash not in self.state_map:
                    self.state_map[emb_hash] = current_step_id

                # Se revisitado, tenta voltar ou resetar para evitar loop infinito
                if not is_new and self.step_count < self.max_steps:
                    print("Redirecionando para evitar loop...")
                    await self.browser.page.goto(self.url)
                    previous_step_id = None
                    continue

                # Navegação: Extrai e prioriza ações
                actions = await self.browser.get_interactive_elements()

                if not actions:
                    print("Nenhum elemento interativo encontrado. Voltando ao início.")
                    await self.browser.page.goto(self.url)
                    previous_step_id = None
                    continue

                # Escolha estocástica entre as top 3 ações para evitar determinismo excessivo
                top_actions = actions[:3]
                best_action = random.choice(top_actions)

                print(f"Executando: {best_action['text']} ({best_action['tag']})")

                # Grava a aresta no grafo
                if previous_step_id is not None:
                    self.reporter.add_edge(previous_step_id, current_step_id, best_action['text'])

                try:
                    # Tenta clicar no elemento
                    await best_action['element'].click()
                    # Espera um pouco para a rede estabilizar
                    await self.browser.page.wait_for_load_state("networkidle", timeout=5000)
                    previous_step_id = current_step_id
                except Exception as e:
                    print(f"Erro ao clicar: {e}")
                    await self.browser.page.goto(self.url)
                    previous_step_id = None

        finally:
            self.reporter.generate()
            await self.browser.close()
            print("Exploração finalizada.")

def main():
    parser = argparse.ArgumentParser(description="Autônomo de Bolso - CLI do Agente Neural")
    parser.add_argument("--url", required=True, help="URL inicial para exploração")
    parser.add_argument("--token", help="Bearer JWT Token para injeção")
    parser.add_argument("--steps", type=int, default=10, help="Número máximo de passos de exploração")

    args = parser.parse_args()

    agent = NeuralAgent(url=args.url, token=args.token, max_steps=args.steps)
    asyncio.run(agent.explore())

if __name__ == "__main__":
    main()
