# 🧠 Introdução à IA Prática: Como o Agente "Pensa"?

Seja bem-vindo ao coração do **Neural Web Tester**. Se você é um desenvolvedor que sempre achou Inteligência Artificial algo "mágico" ou acessível apenas para especialistas em dados, este guia é para você.

Neste projeto, usamos IA para resolver um problema comum: **Como um robô pode saber que "o site mudou" ou que "ele já esteve aqui" sem depender apenas de URLs ou do código HTML?**

---

## 🤖 O Agente Autônomo: Corpo e Cérebro

Imagine que nosso testador é um pequeno robô. Para ele funcionar, precisamos de duas partes:

1.  **O Corpo (Playwright):** É a mão do robô. Ele consegue abrir o navegador, clicar em botões, digitar em campos e tirar fotos da tela.
2.  **O Cérebro (Rede Neural):** É o que processa o que o robô está "vendo". Ele toma as decisões baseadas na imagem da tela, não na URL.

Quando o agente navega, ele segue um ciclo simples:
**Ver (Screenshot) -> Processar (IA) -> Decidir (Ação) -> Repetir.**

---

## 👁️ Visão Computacional: Resumindo Imagens em Números

Computadores não "veem" imagens como nós. Eles veem uma grade de pixels (cores). Para um robô entender se uma página de "Login" é diferente de uma página de "Dashboard", ele usa uma técnica chamada **Extração de Características** (Feature Extraction).

### O Modelo MobileNetV2
Neste projeto, usamos uma rede neural chamada **MobileNetV2**. Ela é famosa por ser leve e rápida, ideal para rodar até em celulares. 

**A analogia do Resumo:**
Imagine que eu te mostro uma foto de uma praia e peço para você resumi-la em exatamente 1000 números que a descrevam perfeitamente (ex: 0.1 para 'tem areia', 0.8 para 'tem mar'). 
A MobileNetV2 faz exatamente isso! Ela recebe a imagem da tela do site e cospe um vetor (uma lista) de números chamada de **Embedding**.

> **Conceito Chave:** O *Embedding* é o "DNA digital" daquela tela no momento exato em que a foto foi tirada.

---

## 🧠 Memória Semântica: "Eu já estive aqui?"

Se o robô apenas olhasse a URL, ele poderia se perder. Muitos sites modernos (SPAs) mudam todo o conteúdo da tela sem nunca mudar a URL. É aqui que entra a **Memória Semântica**.

### Similaridade de Cosseno
Como saber se dois *Embeddings* (listas de números) representam a mesma página? Usamos um cálculo matemático chamado **Similaridade de Cosseno**.

**A analogia das Setas:**
Imagine cada Embedding como uma seta (vetor) apontando para uma direção em um espaço gigante:
*   Se as duas setas apontam quase para o mesmo lugar, as páginas são visualmente idênticas (Similaridade ~ 1.0).
*   Se elas apontam para direções diferentes, o robô entende que está vendo algo novo (Similaridade baixa).

No nosso código, definimos um limite (ex: 0.98). Se a similaridade for maior que isso, o "cérebro" do robô diz: *"Ah, eu já conheço essa tela, não preciso explorar esse caminho de novo!"*

---

## 🎯 Por que isso é incrível?
Diferente de testes tradicionais que quebram se você mudar o ID de um botão no HTML, um agente guiado por IA "enxerga" o layout. Se você mudar a cor do fundo ou mover um elemento de lugar, o Embedding mudará levemente, permitindo que o robô se adapte como um ser humano faria.

---
**Próximo Passo:** [Entendendo o Código (Módulos Técnicos)](../technical/arquitetura_do_codigo.md)
