# Neural Web Tester 🤖🌐

O **Neural Web Tester** é uma ferramenta CLI de exploração autônoma de aplicações web. Ele utiliza Redes Neurais Convolucionais (MobileNetV2) para reconhecimento visual de estados e uma memória semântica para evitar a exploração redundante de caminhos já visitados.

O objetivo é automatizar o teste de "sanidade" (smoke testing) e a descoberta de bugs visuais ou de rede, gerando relatórios ricos com evidências de cada passo.

## 🚀 Guia de Início Rápido

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
   make install
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

O projeto utiliza um `Makefile` para padronizar comandos comuns:

- `make install`: Instala dependências Python e navegadores Playwright.
- `make test`: Executa todos os testes unitários.
- `make lint`: Verifica o estilo do código usando **Ruff**.
- `make clean`: Limpa caches, logs e arquivos temporários.

## ⚠️ Troubleshooting (Resolução de Problemas)

### Timeout do Playwright
Se o site alvo for muito pesado, o agente pode sofrer timeout.
- **Dica:** Tente rodar com `HEADLESS=false` no `.env` para observar o comportamento do navegador ou aumente o tempo de espera no `navigation.py`.

### Autenticação e Sessão
- Monitore se o `AGENT_TOKEN` no `.env` não expirou, impedindo o acesso a áreas autenticadas do site.

### Erros de TensorFlow/Modelos
O carregamento inicial do modelo MobileNetV2 pode demorar alguns segundos na primeira execução pois ele baixa os pesos pré-treinados da ImageNet.
- Certifique-se de ter conexão com a internet no primeiro uso.
