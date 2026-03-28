# Neural Web Tester 🤖🌐

O **Neural Web Tester** é um projeto educacional focado em ensinar desenvolvedores a implementarem redes neurais simples na prática. Ele utiliza o pretexto de uma ferramenta CLI de exploração autônoma de aplicações web para demonstrar conceitos de Visão Computacional e Memória Semântica.

> **Objetivo:** Desmistificar o uso de IA (MobileNetV2) e Geometria Vetorial em aplicações reais de engenharia de software.

---

## 🎓 Aprenda com este projeto

Este repositório foi desenhado para ser um guia de estudo. Comece por aqui:

- [🧠 **Introdução à IA Prática:** Como o Agente "Pensa"?](docs/education/introducao_ia_pratica.md)
- [🏗️ **Arquitetura do Código:** Da Teoria à Prática](docs/technical/arquitetura_do_codigo.md)
- [🚀 **Tutorial:** Seu Primeiro Teste com IA](docs/tutorial_seu_primeiro_teste_ia.md)

---

## 🚀 Guia de Início Rápido (Hands-on)

### Requisitos
- **Python:** 3.8 ou superior
- **Node.js:** Necessário para o Playwright gerenciar os navegadores.

### Setup Rápido

1. Clone o repositório:
   ```bash
   git clone <repo-url>
   cd neural-web-tester
   ```

2. Instale as dependências:
   ```bash
   task install
   ```

3. Configure o ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves e tokens
   ```

## 🛠️ Guia de Uso

Para iniciar uma exploração autônoma em um site:

```bash
python agent.py --url https://exemplo.com --steps 10
```

### Argumentos da CLI
- `--url`: (Obrigatório) URL inicial para a exploração.
- `--token`: Token JWT para injeção de autenticação (Pode ser configurado no `.env` como `AGENT_TOKEN`).
- `--steps`: Número máximo de passos que o agente deve realizar (Padrão: 10).

## 🏗️ Estrutura do Projeto

- `agent.py`: Ponto de entrada da CLI e orquestrador do loop de exploração.
- `navigation.py`: Gerenciamento do navegador via Playwright e extração de elementos interativos.
- `perception.py`: Camada de visão computacional (MobileNetV2) para extração de embeddings de imagens.
- `memory.py`: Lógica de memória semântica baseada em similaridade de cosseno.
- `report.py`: Gerador de relatórios HTML com as evidências coletadas (fotos, logs e erros).
- `templates/`: Templates Jinja2 para a geração do relatório.
- `tests/`: Suíte de testes unitários.

## 🧪 Desenvolvimento e Automação

O projeto utiliza o **Task** (`Taskfile.yml`) de forma multiplataforma (Windows, Linux, macOS) para padronizar comandos comuns:

- `task install`: Instala dependências Python e navegadores Playwright.
- `task test`: Executa todos os testes unitários via pytest. Use `task test REPORT=true` para abrir o relatório após a execução.
- `task lint`: Verifica o estilo do código usando **Ruff**.
- `task clean`: Limpa caches recursivos, logs e arquivos temporários.

## ⚠️ Troubleshooting (Resolução de Problemas)

### Timeout do Playwright
Se o site alvo for muito pesado, o agente pode sofrer timeout.
- **Dica:** Tente rodar com `HEADLESS=false` no `.env` para observar o comportamento do navegador ou aumente o tempo de espera no `navigation.py`.

### Autenticação e Sessão
- Monitore se o `AGENT_TOKEN` no `.env` não expirou, impedindo o acesso a áreas autenticadas do site.

### Erros de TensorFlow/Modelos
O carregamento inicial do modelo MobileNetV2 pode demorar alguns segundos na primeira execução pois ele baixa os pesos pré-treinados da ImageNet.
- Certifique-se de ter conexão com a internet no primeiro uso.
