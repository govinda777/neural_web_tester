# 🚀 Tutorial: Seu Primeiro Teste com IA

Chegou a hora de ver o agente em ação! Vamos preparar o ambiente e rodar uma exploração autônoma.

## 1. Preparação do Laboratório

Antes de começar, certifique-se de que você tem o **Python 3.12+** instalado. O projeto usa o `Task` para facilitar sua vida.

No terminal, execute:
```bash
# 1. Instala as dependências (TensorFlow, Playwright, etc)
task install

# 2. Roda os testes para garantir que o cérebro está funcionando
task test
```

---

## 2. Rodando o Agente Neural

O agente precisa de um alvo. Vamos usar o site de teste que já vem no projeto:

```bash
# Rodando o agente por 5 passos em um site de exemplo
python agent.py --url https://www.google.com --steps 5
```

Enquanto ele roda, observe os logs no terminal:
- Ele dirá quando estiver "processando a visão".
- Ele avisará se encontrar uma página que já visitou visualmente.
- Ele gerará um relatório rico na pasta `reports/`.

---

## 3. Experimento Científico (Desafio)

A melhor forma de aprender é quebrando as coisas! 🛠️

### O Desafio do "Limiar de Memória"
Abra o arquivo `agent.py` e procure pela linha onde inicializamos a memória:
`self.memory = SemanticMemory(threshold=0.98)`

**Tente o seguinte:**
1.  Mude o `threshold` para `0.999`. Rode o agente novamente. 
    *   *O que acontece?* (Dica: O agente se tornará "perfeccionista" e achará que quase tudo é uma página nova).
2.  Mude o `threshold` para `0.50`. 
    *   *O que acontece?* (Dica: O agente achará que tudo é igual e ficará entediado rapidamente).

### O Desafio da Visão
Abra o arquivo `perception.py`. Você verá que redimensionamos a imagem para `(224, 224)`. 
*   O que aconteceria se mudássemos para `(10, 10)`? A rede neural ainda conseguiria diferenciar um botão da logo do Google?

---

## 🏆 Conclusão

Você acaba de rodar e configurar seu primeiro agente autônomo baseado em redes neurais! 

Você viu que:
1.  IA não é apenas chat; ela pode **enxergar** e **tomar decisões**.
2.  Bibliotecas como **TensorFlow** e **Keras** permitem que você use modelos poderosos com pouquíssimas linhas de código.
3.  A matemática (Similaridade de Cosseno) é a cola que une a visão à memória.

**Parabéns, Desenvolvedor de IA!** 🎓
