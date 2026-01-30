Feature: Currency Dashboard
  As a user
  I want to see currency rates
  So that I can monitor exchange values

  Scenario: View Dashboard
    Given I am on the currency dashboard
    Then I should see the "Aplikacja Kursów Walut" title

  Scenario: Fetch rates for a selected date
    Given I am on the currency dashboard
    When I enter the date "2026-01-30"
    And I click the "Synchronizuj z NBP" button
    Then I should see the currency rates table
