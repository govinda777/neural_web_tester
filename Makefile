# Makefile para Automação do Neural Web Tester

# Variáveis
PYTHON = python3
PIP = pip3
PYTEST = pytest
RUFF = ruff

.PHONY: help install test lint clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala dependências do Python e do Playwright"
	@echo "  make test     - Executa a suíte de testes"
	@echo "  make lint     - Executa checagem de estilo com Ruff"
	@echo "  make clean    - Remove arquivos temporários e caches"

install:
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install chromium

test:
	PYTHONPATH=. $(PYTEST) tests/

lint:
	$(RUFF) check .
	$(RUFF) format --check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	rm -rf screenshots/
	rm -rf videos/
	@echo "Limpeza concluída."
