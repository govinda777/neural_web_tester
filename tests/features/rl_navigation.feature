Feature: Shadow DOM RL Navigation
  Scenario: Piercing deep Shadow DOM
    Given the agent is on the test page with 5-level Shadow DOM
    When the agent receives the command "Click hidden button"
    Then the agent must locate and interact with the element at the deepest level
    And the agent must reach the goal in less than 20 steps

  Scenario: Cycle and Loop Detection
    Given the agent enters a page with circular redirection
    When the agent identifies the repeated state hash
    Then the reward must be penalized by -5
    And the agent must change its action policy to escape the loop
