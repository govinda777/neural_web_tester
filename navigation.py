import os
from playwright.async_api import async_playwright
import re


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
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)

        # Injeção de JWT nos headers globais
        extra_headers = {}
        if self.token:
            extra_headers["Authorization"] = f"Bearer {self.token}"

        self.context = await self.browser.new_context(
            extra_http_headers=extra_headers, viewport={"width": 1280, "height": 720}
        )

        self.page = await self.context.new_page()

        # Captura logs do console
        self.page.on(
            "console", lambda msg: self.console_logs.append(f"[{msg.type}] {msg.text}")
        )

        # Captura erros de rede (4xx, 5xx)
        self.page.on("response", self._handle_response)

        await self.page.goto(url, wait_until="networkidle")

    async def _handle_response(self, response):
        if response.status >= 400:
            self.network_errors.append(f"Error {response.status} at {response.url}")

    async def capture_state(self):
        """Tira screenshot e retorna os bytes."""
        return await self.page.screenshot(type="png")

    async def get_interactive_elements(self):
        """Extrai todos os elementos clicáveis e relevantes, incluindo Shadow DOM e iFrames."""
        selector = "button, a, input, select, textarea, [role='button'], [role='link']"
        interactive_actions = []

        url = self.page.url
        if url.startswith("file://"):
            current_domain = "localhost"
        else:
            domain_match = re.search(r"https?://([^/]+)", url)
            current_domain = domain_match.group(1) if domain_match else ""

        for frame in self.page.frames:
            try:
                elements = await frame.locator(selector).all()
            except Exception:
                continue

            is_main_frame = frame == self.page.main_frame

            for el in elements:
                try:
                    if not await el.is_visible() or not await el.is_enabled():
                        continue

                    # Filtro de links externos
                    tag = await el.evaluate("el => el.tagName.toLowerCase()")
                    if tag == "a":
                        href = await el.get_attribute("href")
                        if href:
                            if (
                                href.startswith("http")
                                and current_domain
                                and current_domain not in href
                            ):
                                continue
                            if href.startswith("#") or href.startswith("javascript:"):
                                continue

                    box = await el.bounding_box()
                    if not box or box["width"] == 0 or box["height"] == 0:
                        continue

                    # Extração de dados adicionais via JS para performance
                    info = await el.evaluate("""el => {
                        const rect = el.getBoundingClientRect();
                        const isShadow = !!el.getRootNode().host;
                        const parent = el.parentElement;
                        return {
                            text: (el.innerText || el.value || el.placeholder || "").trim().toLowerCase(),
                            isShadow: isShadow,
                            parentTag: parent ? parent.tagName.toLowerCase() : null,
                            siblingIndex: parent ? Array.from(parent.children).indexOf(el) : 0,
                            id: el.id || ""
                        }
                    }""")

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
                    if any(kw in info["text"] for kw in high_priority_keywords):
                        priority = 3
                    elif tag in ["button", "a"]:
                        priority = 2

                    interactive_actions.append(
                        {
                            "element": el,
                            "text": info["text"],
                            "priority": priority,
                            "tag": tag,
                            "x": box["x"] + box["width"] / 2,
                            "y": box["y"] + box["height"] / 2,
                            "isShadow": info["isShadow"],
                            "isIFrame": not is_main_frame,
                            "id": info["id"],
                            "hierarchy": {
                                "parentTag": info["parentTag"],
                                "siblingIndex": info["siblingIndex"],
                            },
                        }
                    )
                except Exception:
                    continue

        interactive_actions.sort(key=lambda x: x["priority"], reverse=True)
        return interactive_actions

    async def close(self):
        """Fecha o navegador e o Playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
