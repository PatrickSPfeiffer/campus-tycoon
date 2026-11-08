# Feature 4: the five-day run

## Why
A run lasts five trading days and ends with a clear result, so the player can see
whether their decisions made money, and then start again. (CT01, CT05, CT R5)

## What
Implements CT01 (progress and new run), CT05 and CT R5 (scenario A6).
- [ ] The screen shows progress through the run, e.g. "Day 1 of 5".
- [ ] After the fifth trade the run is complete. Buying and trading are rejected
      and nothing changes.
- [ ] When the run is complete, the screen shows final cash, remaining stock at
      purchase cost, and the overall gain or loss (CT R4).
- [ ] The history keeps every completed day, each recorded once.
- [ ] Starting a new run asks for confirmation. Confirming restores €100, every stock
      at 0, every price at its reference, day 1 and an empty history.
      Cancelling keeps the current run unchanged.
- [ ] A completed run, and its result, survive a restart.

## Out of scope
Blocking price changes after the run (the brief only stops buying and trading),
keeping several runs or a leaderboard, random events, more products, charts,
upgrading old databases.

## Done when
1. New game: the run is at day 1 of 5 and not complete.
2. Buy 10 Café and 10 Water (cash €75). Set Water to €2.50 (above twice its €1.20
   reference, so demand 0). Trade five times. Then the run is complete: final cash €115,
   remaining stock at cost €5.00 (10 Water × €0.50), overall gain €20.
3. After the run is complete, buying and trading are rejected; cash, stock, day and
   history stay the same.
4. The history has exactly 5 days. After a restart the run is still complete with
   the same final result.
5. Starting a new run restores €100, stock 0 / 0 / 0, prices €4.00 / €3.00 / €1.20,
   day 1 and an empty history.
6. The 16 tests of features 1–3 still pass.
7. All tests green, on branch feature-4-five-day-run, pushed.
