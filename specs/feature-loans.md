# Loans (practice game)

## Why
In the practice game the player can only spend the cash they have. A loan adds a real
business decision: borrow now to buy more stock, and pay it back with interest. It only
pays off if the extra sales bring more than the interest. (Project list: "Loans", Hard.)

## What
- [ ] Constants in logic.py: LOAN_MAX = 50 and LOAN_INTEREST = 0.10.
- [ ] Every practice game has a "debt" (euros owed). A new game and a new run start
      with debt 0.00.
- [ ] `take_loan(db_path, player, amount)` in logic.py: the amount is a whole number of
      euros from 1 to LOAN_MAX. Cash goes up by the amount and debt becomes
      round(amount * (1 + LOAN_INTEREST), 2). Both are saved together.
- [ ] Refusals, with a clear message and nothing changed: amount not a whole number,
      below 1 or above 50 (True/False are not numbers); the player already has a loan
      in this run ("You already have a loan in this run."); the run is complete (same
      message as buying after the run is complete).
- [ ] Final result (CT R4 plus the loan): final_result also returns "debt", and
      gain = final cash + stock at cost - starting cash - debt. Cash is never reduced
      by the debt, so it never goes negative (CT R3). Tournament stands have no debt.
- [ ] Screen (practice only): a "Loan" section with an amount from 1 to 50, the text
      "You will owe €X" before confirming, and a "Take loan" button, disabled when the
      run is complete or a loan was already taken. The current debt is shown next to
      the cash, and the final result shows "Loan to repay".
- [ ] Storage: a new column games.debt REAL NOT NULL DEFAULT 0, added to create_tables
      and described in docs/data-model.md. Approved by the owner of the data structure
      (Patrick).

## Out of scope
Tournaments, more than one loan per run, repaying early, interest per day, upgrading
old databases (we reset the data, as AGENTS.md says).

## Done when
1. A new game has debt 0.00 and the usual final gain.
2. Normal game (€100), take_loan 50 → cash 150.00, debt 55.00. After reloading the
   game: same cash and debt.
3. take_loan 1 → debt 1.10. take_loan 50 is accepted, 51 is refused.
4. A second loan in the same run is refused; cash and debt do not change.
5. Amounts 0, -5, 51, 2.5 and True are refused; nothing changes.
6. After the run is complete, take_loan is refused; nothing changes.
7. Final gain: Normal game, take_loan 50, then trade five days with no stock →
   final cash 150.00, debt 55.00, gain -5.00.
8. new_run after a loan → debt 0.00 and the level's starting cash.
9. All existing tests pass unchanged.
10. On branch feature-loans, pushed, pull request approved by a teammate before merging.
