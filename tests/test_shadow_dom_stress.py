import pytest
import asyncio
import os
from navigation import BrowserManager

@pytest.mark.asyncio
async def test_shadow_dom_penetration():
    """Valida se o agente consegue penetrar 5 níveis de Shadow DOM."""
    # Cria arquivo HTML com Shadow DOM aninhado
    html_content = """
    <html><body>
    <div id="host1"></div>
    <script>
        let currentHost = document.getElementById('host1');
        for (let i = 1; i <= 5; i++) {
            let shadow = currentHost.attachShadow({mode: 'open'});
            let nextHost = document.createElement('div');
            nextHost.id = 'host' + (i + 1);
            if (i === 5) {
                let btn = document.createElement('button');
                btn.id = 'deep-btn';
                btn.innerText = 'Deep Button';
                nextHost.appendChild(btn);
            }
            shadow.appendChild(nextHost);
            currentHost = nextHost;
        }
    </script>
    </body></html>
    """
    with open("shadow_test.html", "w") as f:
        f.write(html_content)

    url = f"file://{os.path.abspath('shadow_test.html')}"
    browser = BrowserManager()
    await browser.start(url)

    elements = await browser.get_interactive_elements()

    # Verifica se o botão dentro de 5 níveis de Shadow DOM foi encontrado
    found_deep_btn = any(e['id'] == 'deep-btn' for e in elements)

    await browser.close()
    os.remove("shadow_test.html")

    assert found_deep_btn
