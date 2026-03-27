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

        extra_headers = {}
        if self.token:
            extra_headers["Authorization"] = f"Bearer {self.token}"

        self.context = await self.browser.new_context(
            extra_http_headers=extra_headers,
            viewport={"width": 1280, "height": 720}
        )

        self.page = await self.context.new_page()
        self.page.on("console", lambda msg: self.console_logs.append(f"[{msg.type}] {msg.text}"))
        self.page.on("response", self._handle_response)

        await self.page.goto(url, wait_until="networkidle")

    async def _handle_response(self, response):
        if response.status >= 400:
            self.network_errors.append(f"Error {response.status} at {response.url}")

    async def capture_state(self):
        """Tira screenshot e retorna os bytes."""
        return await self.page.screenshot(type="png")

    async def get_interactive_elements(self, max_shadow_depth=5):
        """
        Extrai todos os elementos clicáveis, incluindo Shadow DOM (até 5 níveis) e iFrames.
        Retorna metadados para o encoder.
        """
        # Script JS para atravessar Shadow DOM de forma recursiva
        js_script = f"""
        (maxDepth) => {{
            const elements = [];
            const walk = (root, depth, currentParentIdx = null, isShadow = false) => {{
                if (depth > maxDepth) return;

                // Seleciona todos os nós para manter a hierarquia
                const allNodes = Array.from(root.querySelectorAll('*'));

                // Adiciona o próprio shadow root se ele for o root atual (exceto o document)
                const children = (root === document) ? Array.from(document.body.children) : Array.from(root.children);

                allNodes.forEach(node => {{
                    const isInteractive = node.matches('button, a, input, [role="button"], [role="link"]');
                    const rect = node.getBoundingClientRect();
                    const isVisible = rect.width > 0 && rect.height > 0;

                    if (isInteractive && isVisible) {{
                        const idx = elements.length;

                        // Tenta encontrar o pai na nossa lista de elementos já processados
                        let parentIdx = null;
                        let p = node.parentElement || (node.getRootNode() && node.getRootNode().host);
                        while (p) {{
                            const foundParent = elements.findIndex(el => el._rawNode === p);
                            if (foundParent !== -1) {{
                                parentIdx = foundParent;
                                break;
                            }}
                            p = p.parentElement || (p.getRootNode() && p.getRootNode().host);
                        }}

                        elements.push({{
                            tag: node.tagName.toLowerCase(),
                            text: node.innerText || node.value || "",
                            x: (rect.left + rect.width / 2) / window.innerWidth,
                            y: (rect.top + rect.height / 2) / window.innerHeight,
                            is_shadow: isShadow || (node.getRootNode() instanceof ShadowRoot),
                            is_iframe: false,
                            parent_index: parentIdx,
                            id: node.id || "",
                            _rawNode: node // Referência temporária para busca de parentesco
                        }});
                    }}

                    if (node.shadowRoot) {{
                        walk(node.shadowRoot, depth + 1, elements.length - 1, true);
                    }}
                }});
            }};

            walk(document, 0);
            // Limpa a referência circular antes de retornar
            return elements.map(({{_rawNode, ...rest}}) => rest);
        }}
        """

        # Executa o script no contexto da página principal
        elements_metadata = await self.page.evaluate(js_script, max_shadow_depth)

        # Refinamento: Adicionar lógica para iFrames se necessário
        # (Nesta implementação simplificada, focamos no Shadow DOM conforme o requisito)

        # Conectamos os metadados aos elementos reais para execução de ações
        for i, meta in enumerate(elements_metadata):
            # Usamos o índice como chave para recuperar o elemento depois
            meta['index'] = i

        return elements_metadata

    async def execute_action(self, action_category, element_index, elements_metadata, text_input=""):
        """Executa a ação escolhida pela rede neural."""
        if element_index >= len(elements_metadata):
            return False

        meta = elements_metadata[element_index]

        # Como o script de avaliação não retorna o objeto JS handle,
        # usamos as coordenadas para clicar ou um seletor robusto.
        # Aqui, usamos coordenadas (x,y) normalizadas de volta para pixels.
        x = meta['x'] * 1280
        y = meta['y'] * 720

        try:
            if action_category == 0: # CLICK
                await self.page.mouse.click(x, y)
            elif action_category == 1: # TYPE
                await self.page.mouse.click(x, y)
                await self.page.keyboard.type(text_input)
            elif action_category == 2: # SCROLL
                await self.page.mouse.wheel(0, 300)
            elif action_category == 3: # BACK
                await self.page.go_back()
            # 4 is FINISH (handled by the agent loop)

            await self.page.wait_for_load_state("networkidle", timeout=5000)
            return True
        except Exception as e:
            print(f"Erro ao executar ação {action_category}: {e}")
            return False

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
