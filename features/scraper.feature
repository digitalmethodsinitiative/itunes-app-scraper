Feature: scraper initial

  Scenario: run a simple search
     Given we have itunes scraper installed
      When we search for "mindful"
      Then the scraper will return "50" results

  Scenario: run a similarity search
     Given we have itunes scraper installed
      When we search for result from mindful
      Then the scraper will return "50" results

  Scenario: run a collections search
     Given we have itunes scraper installed
      When we search for the topic topfreeapplications
      Then the scraper will return "50" results

  Scenario: run a developer search
     Given we have itunes scraper installed
      When we search for the developer 384434796
      Then the scraper will return "1" results

  Scenario: run an app search
     Given we have itunes scraper installed
      When we search for the app with id "493145008"
      Then the results length is "44"

  Scenario: run a multiple app search
     Given we have itunes scraper installed
      When we search for "10" apps
      Then the results length is "10"

  Scenario: run a multiple app search with incorrect app id
     Given we have itunes scraper installed
      When we define an incorrect app id "872"
       And we search for another "10" apps
      Then the results length is "10"

  Scenario: read app details for pokemon
     Given we have itunes scraper installed
      When we search for the app with id "1094591345"
      Then the title is "Pokémon GO"