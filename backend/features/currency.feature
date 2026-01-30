Feature: Currency API
  As a user
  I want to retrieve currency exchange rates
  So that I can see current values

  Scenario: Retrieve list of currencies
    Given the database contains a currency "USD" with name "US Dollar"
    When I request the list of currencies
    Then I should receive a list containing "USD"

  Scenario: Retrieve specific rate
    Given the database contains a currency "EUR" with rate 4.50 for date "2026-01-30"
    When I request the rate for "EUR" on "2026-01-30"
    Then I should receive the rate 4.50
