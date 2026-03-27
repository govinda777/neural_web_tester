# language: pt
Funcionalidade: Percepção Visual e Embeddings
  O agente deve processar screenshots e extrair representações vetoriais (embeddings)
  usando a rede neural MobileNetV2 para tomada de decisão.

  Cenário: Processamento de imagem e extração de características
    Dado que o extrator MobileNetV2 esteja carregado
    Quando uma captura de tela de 300x300 pixels é processada
    Então o vetor de embedding resultante deve ter dimensão 1280
    E os valores do tensor de entrada devem estar normalizados entre -1 e 1
