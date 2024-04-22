# Unit tests

## Verified Runs

The following behaviors are required for the Verified Runs portion of the bot to work:
- Parse a verified run from the speedrun.com API
    - Query latest verified run (tests API call) [done]
    - Pass into Pydantic model (tests validation) [done]
    - Assert no exceptions were raised while parsing [done]

- Poll a specified leaderboard for new runs
    - Query runs verified in the last week [done]
    - Pass into Pydantic model (tests validation) [done]
    - Assert no runs are outside the specified range [done]

- Repeat the polling every x seconds

-
