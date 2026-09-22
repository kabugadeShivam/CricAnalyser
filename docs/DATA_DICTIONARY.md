# Data Dictionary

## matches.csv

| Field | Meaning |
|---|---|
| match_id | Unique match identifier |
| season | IPL season |
| date | Match date |
| venue | Match venue |
| city | Venue city |
| team1/team2 | Participating teams |
| toss_winner | Team winning toss |
| toss_decision | Bat/field decision |
| winner | Match winner |
| result | Result type |
| win_by_runs | Margin when won by runs |
| win_by_wickets | Margin when won by wickets |
| player_of_match | Player of the match |

## deliveries.csv

| Field | Meaning |
|---|---|
| match_id | Parent match identifier |
| season | Season |
| inning | Innings number |
| over | Over number |
| ball | Ball sequence |
| batting_team | Batting team |
| bowling_team | Bowling team |
| batter | Batter |
| bowler | Bowler |
| batsman_runs | Runs scored off the bat |
| extra_runs | Extras on delivery |
| total_runs | Total delivery runs |
| extra_type | Type of extra |
| is_wicket | 1 if wicket, else 0 |
| player_dismissed | Dismissed player |
| dismissal_type | Dismissal type |
