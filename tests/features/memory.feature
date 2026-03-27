# language: pt
Funcionalidade: Memória Semântica e Deduplicação de Estados
  O agente deve ser capaz de distinguir estados visuais novos de estados já visitados
  usando similaridade de cosseno em seus embeddings.

  Cenário: Identificação de novos estados visuais
    Dado que a memória semântica esteja inicializada com limiar de 0.98
    Quando um novo embedding de 1280 dimensões é processada
    Então ele deve ser identificado como um novo estado
    E se o mesmo embedding for processado novamente, ele deve ser identificado como um estado revisitado
    E um embedding levemente modificado deve ser identificado como um estado revisitado
    Mas um embedding completamente diferente deve ser identificado como um novo estado
