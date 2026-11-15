# Data model

Where Campus Tycoon stores things. All tables are created by `create_tables` in `db.py`,
and `db.py` is the only file that reads or writes them.

Need a new table or column? Ask the owner of the data structure; don't change the tables yourself.

## Conventions

- **A player is their email**, stored as TEXT: non-empty, at most 254 characters, not only
  spaces. Until sign-in exists (feature 8) the app uses the fixed player `"guest"`.
  Every `player`, `organiser` and `email` column holds this value.
- **Money** (cash, price, revenue, cogs, gross_profit) is REAL, rounded to 2 decimals
  in `logic.py` before it is saved.
- **Products** are stored by catalogue name: `Café`, `Croissant` or `Water`.
  Unit costs and reference prices are not stored; they live in `PRODUCTS` in `logic.py`.
- **day** is the next day to trade: 1 at the start, 6 after the fifth day (run complete).
- Tables have no foreign keys; the link between tables is the shared `player`
  (and `tournament_id`) value.

## Practice tables

Each player has one private practice game. Every practice function in `logic.py` takes the
player and only reads or changes that player's rows.

### players

One row per player, added the first time their game is loaded.

| Column | Type | Meaning |
|---|---|---|
| email | TEXT, PRIMARY KEY | The player. |
| name | TEXT NOT NULL | Display name: the part of the email before `@` (the whole text if there is no `@`). |

### games

One row per player: their current practice run.

| Column | Type | Meaning |
|---|---|---|
| player | TEXT, PRIMARY KEY | The player (`players.email`). |
| cash | REAL NOT NULL | Cash in euros. Starts at 100.00. |
| day | INTEGER NOT NULL | Next day to trade, 1–5; 6 means the run is complete. |
| start_cash | REAL NOT NULL DEFAULT 100.0 | Cash at the start of this run: its difficulty level (Easy 150.00, Normal 100.00, Hard 70.00). The final gain subtracts it. Added for difficulty levels, approved by the owner of the data structure. |

### products

One row per player and product: their stock and selling price.

| Column | Type | Meaning |
|---|---|---|
| player | TEXT NOT NULL | The player. |
| product | TEXT NOT NULL | Catalogue name. |
| stock | INTEGER NOT NULL | Units in stock. Starts at 0. |
| price | REAL NOT NULL | Selling price in euros. Starts at the reference price. |

PRIMARY KEY (player, product).

### results

One row per player, traded day and product. Written in the same transaction as the game
after trading a day; deleted for that player only when they start a new run.

| Column | Type | Meaning |
|---|---|---|
| player | TEXT NOT NULL | The player. |
| day | INTEGER NOT NULL | The day that was traded (1–5). |
| product | TEXT NOT NULL | Catalogue name. |
| units_sold | INTEGER NOT NULL | Units sold that day. |
| revenue | REAL NOT NULL | units_sold × price. |
| cogs | REAL NOT NULL | units_sold × unit cost. |
| gross_profit | REAL NOT NULL | revenue − cogs. |

PRIMARY KEY (player, day, product), so a day can't be recorded twice.
Day totals are not stored; `logic.get_results` adds them up.

## Tournament tables

Created in every database but not used yet; the tournament features build on them.
Every column is NOT NULL.

### tournaments

One row per tournament.

| Column | Type | Meaning |
|---|---|---|
| id | INTEGER, PRIMARY KEY | Tournament number. SQLite assigns the next one if you leave it out. |
| name | TEXT NOT NULL | Name chosen by the organiser. |
| code | TEXT NOT NULL, UNIQUE | 6-character join code. The database rejects a second tournament with the same code. |
| organiser | TEXT NOT NULL | The player who created it. |
| day | INTEGER NOT NULL | Next day to close, 1–5; 6 means complete. |

There is no status column: everything follows from `day`. While `day` is 1 the first day
has not closed, so players can still join; `day` 6 means the tournament is complete.

### stands

One row per player in a tournament.

| Column | Type | Meaning |
|---|---|---|
| tournament_id | INTEGER NOT NULL | `tournaments.id`. |
| player | TEXT NOT NULL | The player who owns this stand. |
| seat | INTEGER NOT NULL | Joining order: 1 for the first player to join, then 2, 3… Used by rule M3 (whose turn it is) and the ranking. |
| cash | REAL NOT NULL | Cash in euros. Starts at 100.00. |
| ready | INTEGER NOT NULL | 1 if the player pressed Ready for the current day, otherwise 0. Only 0 or 1 is allowed. |

PRIMARY KEY (tournament_id, player): one stand per player per tournament.
UNIQUE (tournament_id, seat): the database rejects two stands with the same seat in one
tournament. The same seat number in different tournaments is fine.

### stand_products

One row per stand and product: that stand's stock and selling price.

| Column | Type | Meaning |
|---|---|---|
| tournament_id | INTEGER NOT NULL | `tournaments.id`. |
| player | TEXT NOT NULL | The stand's player. |
| product | TEXT NOT NULL | Catalogue name. |
| stock | INTEGER NOT NULL | Units in stock. Starts at 0. |
| price | REAL NOT NULL | Selling price in euros. Starts at the reference price. |

PRIMARY KEY (tournament_id, player, product).

### tournament_results

One row per closed day, player and product in a tournament.

| Column | Type | Meaning |
|---|---|---|
| tournament_id | INTEGER NOT NULL | `tournaments.id`. |
| day | INTEGER NOT NULL | The day that was closed (1–5). |
| player | TEXT NOT NULL | The stand's player. |
| product | TEXT NOT NULL | Catalogue name. |
| price | REAL NOT NULL | The price the stand had that day, in euros. |
| units_sold | INTEGER NOT NULL | Units sold that day. |
| revenue | REAL NOT NULL | units_sold × price. |
| cogs | REAL NOT NULL | units_sold × unit cost. |
| gross_profit | REAL NOT NULL | revenue − cogs. |

PRIMARY KEY (tournament_id, day, player, product), so a day can't be recorded twice.

## Old databases

The structure changed in feature 7, and old databases are not upgraded. Delete the local
`data/game.db` and the old Turso tables before running the app; the tables are then
created fresh.
