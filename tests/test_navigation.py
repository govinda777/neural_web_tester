import unittest
import asyncio
import os
from navigation import BrowserManager

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
            await self.browser_manager.start(self.test_file_path)

            # Captura de logs de console
            self.assertTrue(any("Este é um erro de console planejado!" in log for log in self.browser_manager.console_logs))

            # Screenshot não vazio
            screenshot = await self.browser_manager.capture_state()
            self.assertGreater(len(screenshot), 100)

            # Elementos interativos
            actions = await self.browser_manager.get_interactive_elements()
            self.assertGreater(len(actions), 0)

            # Verificação de prioridades
            # "Salvar" deve ter prioridade 3
            save_btn = next((a for a in actions if "salvar" in a['text']), None)
            self.assertIsNotNone(save_btn)
            self.assertEqual(save_btn['priority'], 3)

            # Link para o Google deve ser ignorado (externo)
            google_link = next((a for a in actions if "google" in a['text']), None)
            self.assertIsNone(google_link)

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
