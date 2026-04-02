Feature: Dashboard UI E2E
  Como um engenheiro de QA
  Eu quero que o dashboard reflita o estado real do agente
  Para validar visualmente o comportamento da rede neural

  @e2e @dashboard
  Scenario: Validar que o Dashboard exibe dados após a execução do agente
    Given que o servidor de telemetria e o frontend estão rodando
    When o agente completa uma navegação de 2 passos
    Then eu acesso o dashboard em "http://localhost:3000"
    And eu devo ver o screenshot da página no componente LivePreview
    And eu devo ver as barras de importância de features
    And o mapa mental de estados deve conter pelo menos 2 nós
