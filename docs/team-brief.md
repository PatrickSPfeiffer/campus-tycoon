# Campus Tycoon · Team project brief

Campus Tycoon becomes a game that Nova students play against each other. Each player
runs a campus stand selling Café, Croissant and Water. In a tournament, all players
share the same customers: the cheapest stand sells first, so prices and stock become
a real competition. The solo game stays as a practice mode.

The original product brief (docs/) still applies wherever this brief does not change it.

## Players and roles

- **Player:** signs in with Google (`st.login`). Plays practice runs and joins tournaments.
- **Organiser:** the player who created a tournament. Shares its join code, sees every
  player's results, and can close a day early. An organiser may also play in it.
- Nobody plays without signing in.

## Modes

**Practice.** Today's game, one per player: €100, five days, three products, the
current rules. Each player's practice run is private to them.

**Tournament.**
1. An organiser creates a tournament with a name. The app gives it a 6-character join code.
2. Players join with the code until the first day is closed. Each player starts with
   €100, no stock and reference prices, and the tournament lasts five days.
3. Each day, every player buys stock and sets prices, then presses **Ready**.
   Until then, they can still change their decisions.
4. The day closes when every player is ready, or when the organiser presses
   **Close day now**. A player who is not ready trades with their current prices and stock.
5. After the fifth day, the tournament is complete and shows the final ranking.

## The shared market (tournament rule)

For each product and each day:

- **M1.** There are 10 customers per player in the tournament: half are *budget*
  customers, who pay at most the reference price, and half are *premium* customers,
  who pay at most twice the reference price.
- **M2.** Budget customers buy first, then premium customers. Each customer buys one
  unit from the cheapest stand they can afford that still has stock.
- **M3.** Stands with the same price share those customers equally. If the customers
  cannot be split equally, the customers left over go one each to the tied players,
  starting with the player whose turn it is and following the joining order. The turn
  rotates each day in joining order: on day 1 it is the player who joined first, on day 2
  the second, and so on, starting again after the last player. If the player whose turn it
  is is not in the tie, the next tied player in joining order starts. A tied player who runs
  out of stock passes their remaining customers to the other tied players.
  (Known limit: in a five-day tournament some players get the turn once more than others.)
- **M4.** Revenue, COGS, gross profit, cash and rounding follow the existing rules
  (CT R2–R4).

With one player, M1–M3 give exactly the current demand rule (10 / 5 / 0), so the solo
game is a market of one and its tests stay valid.

**Example (Café, reference €4, two players):** 10 budget and 10 premium customers.
Ana sells at €3.50 with 15 units; Bruno at €6.00 with 10 units.
The 10 budget customers buy from Ana. The premium customers buy 5 more from Ana
(her stock runs out), and the last 5 buy from Bruno. Result: Ana sells 15, Bruno 5.

## What players see

- During a tournament: their own cash, stock, prices and day; who is ready.
- After each day: every stand's price and units sold per product (not their stock or cash).
- At the end: the ranking by overall gain (CT R4).

## Access rules (each becomes a test, including the rejected case)

- A player can only see and change their own practice run.
- A player can only act in tournaments they joined, and only on their own stand.
- Only the organiser can close a day early.
- Joining with a wrong code, or after the first day closed, is rejected.
- Actions after the tournament is complete are rejected; nothing changes.

## What the product must remember

Players (from their Google account); practice runs; tournaments (name, code, organiser,
current day, status); each player's stand in a tournament (cash, stock, prices, ready);
every closed day's results per player and product. All of it must survive restarts and
be shared by all users of the deployed app.

## Delivery in layers (each layer is a complete, working product)

1. **Foundation:** deployed app, hosted database, Google sign-in, one practice run per player.
2. **Tournaments:** create, join with a code, ready / close day, ranking. Each player still
   has their own customers.
3. **Shared market:** rules M1–M3 decide each day's sales across the tournament.

## Suggested split for four members

- **Member 1 (owner of the data structure):** layer 1 storage and sign-in. Designs all
  the tables, including those for tournaments, before the others build on them.
- **Member 2:** deploy now, tests on every pull request (GitHub Actions), README.
- **Member 3:** tournaments (create, join, ready, close day, ranking).
- **Member 4:** the shared market rule as a pure function in `logic.py`: given the stands,
  return each stand's sales. It needs no database, so it can start on day one.
- **Everyone, at the end:** UI/UX polish, security pass, demo and walkthrough rehearsal.

## Out of scope

Live updates without a refresh (a Refresh button is enough for a turn-based game),
chat between players, private messages, products other than the three in the catalogue.

## Open technical decisions

- Hosting: Streamlit Community Cloud (decided when deploying).
- Hosted database provider: chosen by member 1 in layer 1.
- Google sign-in configuration and where its secrets live (never in the repository).
