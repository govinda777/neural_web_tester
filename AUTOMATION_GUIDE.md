# Guia de Automação: Windows & Linux 🚀

Para garantir que desenvolvedores utilizando Windows, Linux ou macOS tenham a mesma experiência ao rodar tarefas do projeto de forma nativa e sem misturar o gerenciador de tarefas com código de aplicação, este projeto utiliza o **Task** (`Taskfile.yml`).

Abaixo você encontra como utilizá-lo passo a passo em qualquer sistema operacional e quais os pré-requisitos fundamentais para esse projeto funcionar corretamente.

## ⚠️ Pré-requisitos (TensorFlow)

Este projeto usa pacotes como o `tensorflow` que **não suportam versões experimentais/futuras do Python** (ex: Python 3.13 ou 3.14). 
Se você usar uma versão muito nova, erros de pacotes não encontrados ou C-extension quebrado irão ocorrer. 

- **Versão exigida:** Python **3.12** (ou 3.11).
- **Como instalador (Windows):** `winget install Python.Python.3.12`
- O nosso arquivo automador já invoca nativamente a versão correta 3.12, então você não precisa desinstalar outras distribuições que tiver na máquina!

---

## 🛠️ Como Instalar a ferramenta de tarefas (Task)

Para poder rodar os comandos no seu terminal, primeiro instale o runner global:

**Com Node/NPM (Universal):**
```bash
npm install -g @go-task/cli
```

**(Ou) Com Winget (Windows):**
```powershell
winget install Task.Task
```

**(Ou) Com Homebrew (macOS/Linux):**
```bash
brew install go-task/tap/go-task
```

---

## 🚀 Como Executar

A partir da raiz do projeto, no seu terminal:

1. **Instalar dependências (Python + Playwright):**
   ```bash
   task install
   ```
2. **Rodar testes:**
   ```bash
   task test
   ```
3. **Checar linting e estilo do código (ruff):**
   ```bash
   task lint
   ```
4. **Limpar arquivos temporários (caches, logs, media):**
   ```bash
   task clean
   ```

A configuração e lógicas de cada comando encontram-se documentadas e organizadas dentro do arquivo `Taskfile.yml`.
