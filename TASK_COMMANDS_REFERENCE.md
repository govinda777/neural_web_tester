# 📖 Referência de Comandos (Taskfile.yml)

Este arquivo documenta tecnicamente o fluxo de execução implementado no [Taskfile.yml](./Taskfile.yml). 
O `Taskfile.yml` atua como nosso orquestrador universal, isolando a complexidade do sistema operacional e invocando a versão correta do ecossistema do Python 3.12 internamente.

---

## 1. Instalação e Setup (`task install`)

**Resumo:**
Prepara a máquina de desenvolvimento instalando as dependências do `requirements.txt` (incluindo pacotes nativos pesados como o TensorFlow) e faz o download isolado do motor do navegador Chromium para as automações visuais via Playwright.

**Fluxo de Execução:**

```mermaid
flowchart TD
    A([Utilizador digita: "task install"]) --> B{Decisão da Variável OS}
    B -->|Windows| C[Usa comando: py -3.12]
    B -->|Linux/macOS| D[Usa comando: python3]
    C --> E
    D --> E
    
    E[Inicia gerenciador Pip] --> F[python -m pip install -r requirements.txt]
    F --> G[Inicia instalador Playwright]
    G --> H[python -m playwright install chromium]
    
    H --> I(([Ambiente Pronto ✅]))
```

---

## 2. Validação e Testes (`task test`)

**Resumo:**
Mapeia automaticamente o caminho do projeto para o `PYTHONPATH` global do script e engatilha o módulo `pytest` rodando toda a suíte de testes existente na pasta `tests/`. Agora também exporta nativamente um relatório visual com a execução e, se o parâmetro `REPORT=true` for fornecido, abre automaticamente no navegador!

**Uso Opcional:** `task test REPORT=true`

**Fluxo de Execução:**

```mermaid
flowchart LR
    A([Utilizador digita: "task test REPORT=true"]) --> B[Seta Env: PYTHONPATH=.]
    B --> C[Roda interpretador Python Mapeado]
    C --> D[python -m pytest tests/ --html=reports/test_report.html]
    D --> E{Há falhas?}
    
    E -->|Sim/Não| F{REPORT=true?}
    F -->|Sim| G([Abre relatorio_testes.html no Navegador Nativo])
    F -->|Não| H([Finaliza processo silencioso])
```

---

## 3. Checagem de Estilo (`task lint`)

**Resumo:**
Comando que invoca o `ruff` (Auditor de código) sob o interpretador em duas etapas: ele primeiro tenta encontrar falhas críticas de codigorm (como tipagem torta, imports falsos) e posteriormente checa a formatação dura do código (quebra de linha excessiva, padrões de aspas).

**Fluxo de Execução:**

```mermaid
flowchart TD
    A([Utilizador digita: "task lint"]) --> B[python -m ruff check .]
    B -->|Limpa imports lixos e valida regras de design| C[python -m ruff format --check .]
    C -->|Garante que todos os espaços estão em formato PEP-8| D(([Aprovado nos Padrões de Qualidade 🛡️]))
```

---

## 4. Limpeza Avançada (`task clean`)

**Resumo:**
Responsável por esvaziar a geração de resíduos do Python e limpezas operacionais do tester (limpar pastas de screenshots, vídeos que o Playwright gerou e todos os logs). O fluxo é completamente ramificado pelas plataformas para não ter vulnerabilidades ou falhas de Sintaxe no Unix/CMD.

**Fluxo de Execução:**

```mermaid
flowchart TD
    A([Utilizador digita: "task clean"]) --> B{Qual Plataforma base?}
    
    B -->|Linux / Darwin (Mac)| C[Executa rm -rf bash\nExecuta sh: find -exec e -delete]
    B -->|Windows (PowerShell)| D[Invoca powershell nativo\nRemove-Item e Get-ChildItem Recursivamente]
    
    C --> E[Exclui Pastas de Artefatos:\n/screenshots\n/videos\n.pytest_cache\n.ruff_cache]
    D --> E
    
    E --> F[Busca Oculta profunda:\nExclui todas as __pycache__ filhas\nExclui todos os arquivos .log]
    
    F --> G(([Diretório Completamente Limpo ♻️]))
```
