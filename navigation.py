import os
import logging
from playwright.async_api import async_playwright
import re

logger = logging.getLogger(__name__)


class BrowserManager:
    def __init__(self, token=None):
        self.token = token
        self.headless = os.getenv("HEADLESS", "true").lower() == "true"
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.console_logs = []
        self.network_errors = []

    async def start(self, url):
        """Inicia o Playwright e abre a página com injeção de JWT."""
        logger.info(f"Iniciando BrowserManager para a URL: {url}")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)

        # Injeção de JWT nos headers globais
        extra_headers = {}
        if self.token:
            logger.info("Token JWT detectado. Injetando no header de Autorização.")
            extra_headers["Authorization"] = f"Bearer {self.token}"

        self.context = await self.browser.new_context(
            extra_http_headers=extra_headers, viewport={"width": 1280, "height": 720}
        )

        self.page = await self.context.new_page()

        # Captura logs do console
        self.page.on(
            "console",
            lambda msg: (
                self.console_logs.append(f"[{msg.type}] {msg.text}"),
                logger.debug(f"Console Log: [{msg.type}] {msg.text}"),
            ),
        )

        # Captura erros de rede (4xx, 5xx)
        self.page.on("response", self._handle_response)

        logger.info("Navegando para a URL e aguardando estabilidade da rede.")
        await self.page.goto(url, wait_until="networkidle")

    async def _handle_response(self, response):
        if response.status >= 400:
            self.network_errors.append(f"Error {response.status} at {response.url}")

    async def capture_state(self):
        """Tira screenshot e retorna os bytes."""
        return await self.page.screenshot(type="png")

    async def get_interactive_elements(self):
        """Extrai todos os elementos clicáveis e relevantes."""
        logger.info("Iniciando extração de elementos interativos do DOM.")
        # Seleciona botões, links, inputs e elementos com role de botão ou link
        elements = await self.page.query_selector_all(
            "button, a, input[type='button'], input[type='submit'], [role='button'], [role='link']"
        )
        logger.info(f"Localizados {len(elements)} nós potenciais no DOM.")

        interactive_actions = []
        url = self.page.url
        if url.startswith("file://"):
            current_domain = (
                "localhost"  # Trata arquivos locais como localhost para teste
            )
        else:
            domain_match = re.search(r"https?://([^/]+)", url)
            current_domain = domain_match.group(1) if domain_match else ""

        for el in elements:
            # Filtra elementos invisíveis ou desabilitados
            if not await el.is_visible() or not await el.is_enabled():
                continue

            # Para links, verifica se leva ao mesmo domínio
            href = await el.get_attribute("href")
            if href:
                if (
                    href.startswith("http")
                    and current_domain
                    and current_domain not in href
                ):
                    continue  # Ignora links externos
                if href.startswith("#") or href.startswith("javascript:"):
                    continue  # Ignora âncoras internas e scripts diretos

            # Priorização básica baseada em texto
            text = (await el.inner_text()).lower()
            tag = await el.evaluate("el => el.tagName.toLowerCase()")

            priority = 1
            high_priority_keywords = [
                "save",
                "submit",
                "menu",
                "enviar",
                "salvar",
                "entrar",
                "login",
            ]
            if any(kw in text for kw in high_priority_keywords):
                priority = 3
            elif tag == "button" or tag == "a":
                priority = 2

            interactive_actions.append(
                {"element": el, "text": text, "priority": priority, "tag": tag}
            )
            logger.debug(f"Elemento interceptado: '{text}' ({tag}) - Prioridade {priority}")

        # Ordena por prioridade (maior primeiro)
        interactive_actions.sort(key=lambda x: x["priority"], reverse=True)
        logger.info(f"Extração finalizada: {len(interactive_actions)} elementos válidos identificados.")
        return interactive_actions

    async def close(self):
        """Fecha o navegador e o Playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
