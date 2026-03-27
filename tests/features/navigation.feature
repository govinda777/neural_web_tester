# language: pt
Funcionalidade: Navegação e Interação com o Browser
  O agente deve ser capaz de navegar por uma URL, identificar elementos interativos
  e priorizar ações baseadas no contexto do DOM.

  Cenário: Identificação de elementos e priorização
    Dado que o agente acesse a página de dashboard "test_site.html"
    Quando ele analisar o DOM em busca de elementos interativos
    Então ele deve localizar o botão "Salvar Alterações" com prioridade 3
    E ele deve ignorar o link externo para o "Google"
    E ele deve capturar um erro de console planejado
