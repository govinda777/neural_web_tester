import unittest
import asyncio
import os
import logging
from navigation import BrowserManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestNavigation(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.browser_manager = BrowserManager()
        self.test_file_path = f"file://{os.path.abspath('test_site.html')}"

    def tearDown(self):
        self.loop.run_until_complete(self.browser_manager.close())
        self.loop.close()

    def test_navigation_and_capture(self):
        async def run_test():
            logger.info(f"Iniciando navegação para: {self.test_file_path}")
            await self.browser_manager.start(self.test_file_path)

            # Captura de logs de console
            logger.info("Verificando captura de logs de console na página...")
            self.assertTrue(
                any(
                    "Este é um erro de console planejado!" in log
                    for log in self.browser_manager.console_logs
                )
            )
            logger.info(
                f"Logs de console interceptados com sucesso: {self.browser_manager.console_logs}"
            )

            # Screenshot não vazio
            logger.info("Capturando screenshot da página ativa...")
            screenshot = await self.browser_manager.capture_state()
            self.assertGreater(len(screenshot), 100)
            logger.info(f"Screenshot capturado com sucesso: {len(screenshot)} bytes.")

            # Elementos interativos
            logger.info("Extraindo elementos interativos da página...")
            actions = await self.browser_manager.get_interactive_elements()
            actions = await self.browser_manager.get_interactive_elements()
            self.assertGreater(len(actions), 0)
            logger.info(
                f"Foram encontrados {len(actions)} elementos interativos válidos."
            )

            # Verificação de prioridades
            # "Salvar" deve ter prioridade 3
            save_btn = next((a for a in actions if "salvar" in a["text"]), None)
            self.assertIsNotNone(save_btn)
            self.assertEqual(save_btn["priority"], 3)
            logger.info("Prioridade do botão 'salvar' validada corretamente (3).")

            # Link para o Google deve ser ignorado (externo)
            google_link = next((a for a in actions if "google" in a["text"]), None)
            self.assertIsNone(google_link)
            logger.info("Link externo para o Google foi ignorado com sucesso!")

        self.loop.run_until_complete(run_test())


if __name__ == "__main__":
    unittest.main()
