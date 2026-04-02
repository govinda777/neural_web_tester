from playwright.sync_api import sync_playwright
import time
import os

def capture_dashboard_evidence():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Abre o Dashboard
        try:
            page.goto("http://localhost:3000", timeout=5000)
            time.sleep(3) # Espera carregar

            # Screenshot do dashboard (mesmo que aguardando telemetria, mostra o layout)
            page.screenshot(path="docs/images/dashboard_layout.png")
            print("Layout do Dashboard capturado.")
        except Exception as e:
            print(f"Erro ao capturar dashboard: {e}")

        browser.close()

if __name__ == "__main__":
    capture_dashboard_evidence()
