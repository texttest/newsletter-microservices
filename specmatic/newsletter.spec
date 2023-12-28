Feature: Newsletter API

Background:
    Given openapi ../newsletter/src/openapi.yaml

Scenario Outline: AddUser
    When GET /sayHello/Geoff
    Then status 200
    Examples:
    | name  |
    | xxxxx |

Scenario Outline: BadUser
    When GET /sayHello/Insecticide
    Then status 400
    Examples:
    | name  |
    | xxxxx |

Scenario Outline: KnownUser
    When GET /sayHello/Charles%20Darwin
    Then status 200
    Examples:
    | name  |
    | xxxxx |
