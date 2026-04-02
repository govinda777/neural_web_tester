Feature: Observabilidade Espacial do Agente
  Como um desenvolvedor de IA
  Eu quero que o agente transmita sua telemetria para o servidor
  Para que eu possa visualizar seu raciocínio em tempo real

  @observability
  Scenario: O agente inicia uma sessão e envia telemetria após uma ação
    Given que o servidor de telemetria está ativo
    When o agente inicia um teste na URL "file:///app/test_site.html" com objetivo "Testar Observabilidade"
    And o agente executa 1 passo
    Then a sessão deve ser registrada no banco de dados SQLite
    And pelo menos 1 passo deve conter metadados de confiança e features
