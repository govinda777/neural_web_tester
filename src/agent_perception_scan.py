import asyncio
import os
import datetime
from src.navigation import BrowserManager


async def perform_perception_scan():
    url = f"file://{os.path.abspath('test_site.html')}"
    browser = BrowserManager()
    await browser.start(url)
    page = browser.page

    # 1. Extrair inputs de formulário
    inputs = await page.query_selector_all("input")
    found_inputs = []
    for el in inputs:
        input_id = await el.get_attribute("id")
        name = await el.get_attribute("name")
        input_type = await el.get_attribute("type")
        found_inputs.append({"id": input_id, "name": name, "type": input_type})

    # 2. Dados da tabela de serviços
    rows = await page.query_selector_all("#services-table tbody tr")
    found_services = []
    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) >= 2:
            service = await cells[0].inner_text()
            price = await cells[1].inner_text()
            found_services.append({"service": service, "price": price})

    # 3. Estado dos botões
    buttons = await page.query_selector_all("button")
    found_buttons = []
    for btn in buttons:
        btn_id = await btn.get_attribute("id")
        is_enabled = await btn.is_enabled()
        found_buttons.append({"id": btn_id, "enabled": is_enabled})

    await browser.close()

    # Validação (Benchmark)
    expected_inputs = ["name", "email"]
    expected_buttons = ["submit-btn", "disabled-btn", "save-btn"]

    found_input_ids = [i["id"] for i in found_inputs]
    found_button_ids = [b["id"] for b in found_buttons]

    missing_inputs = [i for i in expected_inputs if i not in found_input_ids]
    missing_buttons = [b for b in expected_buttons if b not in found_button_ids]

    total_expected = len(expected_inputs) + len(expected_buttons)
    total_found = (len(expected_inputs) - len(missing_inputs)) + (
        len(expected_buttons) - len(missing_buttons)
    )

    success_rate = (total_found / total_expected) * 100 if total_expected > 0 else 100

    # Geração do Relatório
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_sha = os.environ.get("GITHUB_SHA", "Local-dev")

    report_content = f"""# Perception Scan Report
**Timestamp:** {timestamp}
**Commit SHA:** {commit_sha}

## Tabela de Elementos Encontrados

### Inputs
| ID | Name | Type |
|----|------|------|
"""
    for i in found_inputs:
        report_content += f"| {i['id']} | {i['name']} | {i['type']} |\n"

    report_content += """
### Buttons
| ID | Enabled |
|----|---------|
"""
    for b in found_buttons:
        report_content += f"| {b['id']} | {b['enabled']} |\n"

    report_content += """
### Services Table
| Service | Price |
|---------|-------|
"""
    for s in found_services:
        report_content += f"| {s['service']} | {s['price']} |\n"

    report_content += f"""
## Status de Sucesso
O agente identificou {success_rate:.0f}% dos elementos esperados.

## Divergências
"""
    if not missing_inputs and not missing_buttons:
        report_content += "Nenhuma divergência encontrada.\n"
    else:
        if missing_inputs:
            report_content += f"- Inputs ausentes: {', '.join(missing_inputs)}\n"
        if missing_buttons:
            report_content += f"- Botões ausentes: {', '.join(missing_buttons)}\n"

    with open("latest_scan_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print("Relatório 'latest_scan_report.md' gerado com sucesso.")


if __name__ == "__main__":
    asyncio.run(perform_perception_scan())
