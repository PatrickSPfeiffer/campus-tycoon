import streamlit as st

import db
import logic

DB_PATH = db.DEFAULT_PATH

st.title("Campus Tycoon")

# Before signing in: only a short welcome and the sign-in button, no game data.
if not st.user.is_logged_in:
    st.write("Welcome! Run a small campus shop for five days. Sign in to play.")
    if st.button("Sign in with Google"):
        st.login()
    st.stop()

# The player is always the signed-in Google email, never typed in.
try:
    PLAYER = logic.player_from_user(st.user)
except ValueError as error:
    st.error(str(error))
    if st.button("Sign out"):
        st.logout()
    st.stop()

col1, col2 = st.columns([3, 1])
col1.caption(f"Signed in as {PLAYER}")
if col2.button("Sign out"):
    st.logout()

try:
    game = logic.load_game(DB_PATH, PLAYER)
except db.DatabaseUnavailable as error:
    st.error(str(error))
    st.stop()
run_complete = logic.is_run_complete(game)

col1, col2 = st.columns(2)
col1.metric("Cash", f"€{game['cash']:.2f}")
if run_complete:
    col2.metric("Progress", "Run complete")
else:
    col2.metric("Progress", f"Day {game['day']} of {logic.RUN_DAYS}")

if run_complete:
    final = logic.final_result(game)
    st.subheader("Final result")
    col1, col2, col3 = st.columns(3)
    col1.metric("Final cash", f"€{final['final_cash']:.2f}")
    col2.metric("Remaining stock at cost", f"€{final['stock_at_cost']:.2f}")
    col3.metric("Overall gain or loss", f"€{final['gain']:.2f}")

st.subheader("New run")
if not st.session_state.get("confirm_new_run"):
    if st.button("Start a new run"):
        st.session_state["confirm_new_run"] = True
        st.rerun()
else:
    st.warning("Start a new run? The current run and its history will be lost.")
    col1, col2 = st.columns(2)
    if col1.button("Yes, start a new run"):
        try:
            logic.new_run(DB_PATH, PLAYER)
            st.session_state["confirm_new_run"] = False
            st.rerun()
        except db.DatabaseUnavailable as error:
            st.error(str(error))
    if col2.button("Cancel"):
        st.session_state["confirm_new_run"] = False
        st.rerun()

st.subheader("Products")
st.table(
    [
        {
            "Product": name,
            "Stock": game["stock"][name],
            "Price": f"€{game['price'][name]:.2f}",
            "Unit cost": f"€{logic.PRODUCTS[name]['unit_cost']:.2f}",
            "Reference price": f"€{logic.PRODUCTS[name]['reference_price']:.2f}",
        }
        for name in logic.PRODUCTS
    ]
)
st.caption(
    "Demand per product per day: 10 units at or below its reference price, "
    "5 units up to twice the reference price, 0 units above that."
)

st.subheader("Selling price")
price_product = st.selectbox("Product", list(logic.PRODUCTS), key="price_product")
new_price = st.number_input(
    "Price (€)", step=0.01, value=game["price"][price_product], format="%.2f",
    key=f"price_{price_product}",
)
if st.button("Set price"):
    try:
        logic.set_price(DB_PATH, PLAYER, price_product, round(float(new_price), 2))
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

st.subheader("Buy")
buy_product = st.selectbox("Product", list(logic.PRODUCTS), key="buy_product")
quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
st.write(f"Total cost €{logic.buy_cost(buy_product, int(quantity)):.2f}")
if st.button("Buy", disabled=run_complete):
    try:
        logic.buy(DB_PATH, PLAYER, buy_product, int(quantity))
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

st.subheader("Trade")
if st.button("Trade one day", disabled=run_complete):
    try:
        logic.trade_day(DB_PATH, PLAYER)
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

st.subheader("Results")
try:
    results = logic.get_results(DB_PATH, PLAYER)
except db.DatabaseUnavailable as error:
    st.error(str(error))
    results = []

# History charts: built only from this player's own saved results.
chart_data = logic.profit_chart_data(results)
if chart_data["Day"]:
    st.write("Gross profit per day by product")
    st.bar_chart(
        chart_data, x="Day", y=list(logic.PRODUCTS), stack=False,
        x_label="Day", y_label="Gross profit (€)",
    )
    st.write("Total gross profit per day")
    st.line_chart(
        chart_data, x="Day", y="Total", x_label="Day", y_label="Gross profit (€)",
    )
else:
    st.info("Trade a day to see your charts.")

for result in results:
    st.write(f"Day {result['day']}")
    rows = []
    for name, line in list(result["by_product"].items()) + [("Total", result["total"])]:
        rows.append(
            {
                "Product": name,
                "Units sold": line["units_sold"],
                "Revenue": f"€{line['revenue']:.2f}",
                "COGS": f"€{line['cogs']:.2f}",
                "Gross profit": f"€{line['gross_profit']:.2f}",
            }
        )
    st.table(rows)

if run_complete:
    st.download_button(
        "Download run report (CSV)",
        data=logic.build_run_report_csv(results).encode("utf-8-sig"),
        file_name="run_report.csv",
        mime="text/csv",
    )

st.subheader("Tournaments")


def show_closed_day(closed_day, player):
    st.success(f"Day {closed_day['day']} closed.")
    own_sales = closed_day.get("by_player", {}).get(player)
    if own_sales is not None:
        st.table(
            [
                {
                    "Product": product,
                    "Units sold": line["units_sold"],
                    "Revenue": f"€{line['revenue']:.2f}",
                }
                for product, line in own_sales.items()
            ]
        )


def show_tournament(stand, player):
    st.subheader(f"{stand['name']} — join code {stand['code']}")
    tournament_id = stand["id"]
    try:
        status = logic.tournament_status(DB_PATH, player, tournament_id)
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))
        return

    action_error = None
    action_message = None
    closed_day = None
    products = list(logic.PRODUCTS)
    own_player = next((row for row in status["players"] if row["player"] == player), None)
    is_ready = bool(own_player and own_player["ready"])

    if status["day"] <= logic.RUN_DAYS:
        if not is_ready:
            with st.form(f"tournament_buy_form_{tournament_id}"):
                buy_product = st.selectbox(
                    "Product", products, key=f"tournament_buy_product_{tournament_id}"
                )
                quantity = st.number_input(
                    "Quantity", min_value=1, step=1, value=1,
                    key=f"tournament_quantity_{tournament_id}",
                )
                buy_submitted = st.form_submit_button("Buy")
            if buy_submitted:
                try:
                    logic.buy_tournament_stock(
                        DB_PATH, player, tournament_id, buy_product, int(quantity)
                    )
                    action_message = "Stock purchased."
                except (ValueError, db.DatabaseUnavailable) as error:
                    action_error = str(error)

            with st.form(f"tournament_price_form_{tournament_id}"):
                price_product = st.selectbox(
                    "Product", products, key=f"tournament_price_product_{tournament_id}"
                )
                price = st.number_input(
                    "Price (€)", min_value=0.01, step=0.01, value=1.0, format="%.2f",
                    key=f"tournament_price_{tournament_id}",
                )
                price_submitted = st.form_submit_button("Set price")
            if price_submitted:
                try:
                    logic.set_tournament_price(
                        DB_PATH, player, tournament_id, price_product, round(float(price), 2)
                    )
                    action_message = "Price updated."
                except (ValueError, db.DatabaseUnavailable) as error:
                    action_error = str(error)

            if st.button("Ready", key=f"tournament_ready_{tournament_id}"):
                try:
                    result = logic.ready_tournament(DB_PATH, player, tournament_id)
                    action_message = "You are Ready."
                    closed_day = result.get("closed_day")
                except (ValueError, db.DatabaseUnavailable) as error:
                    action_error = str(error)

        if player == status["organiser"] and st.button(
            "Close day now", key=f"tournament_close_{tournament_id}"
        ):
            try:
                closed_day = logic.close_tournament_day(DB_PATH, player, tournament_id)
            except (ValueError, db.DatabaseUnavailable) as error:
                action_error = str(error)

    if action_error:
        st.error(action_error)
    if action_message:
        st.success(action_message)
    if closed_day:
        show_closed_day(closed_day, player)

    # Reload after actions so the displayed state reflects this run's changes.
    try:
        status = logic.tournament_status(DB_PATH, player, tournament_id)
        stands = logic.get_my_stands(DB_PATH, player)
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))
        return
    own_player = next((row for row in status["players"] if row["player"] == player), None)
    current_stand = next((item for item in stands if item["id"] == tournament_id), None)
    if current_stand is None:
        return

    if status["day"] == logic.RUN_DAYS + 1:
        st.write("Tournament complete")
        try:
            ranking = logic.tournament_ranking(DB_PATH, tournament_id)
            st.table(
                [
                    {
                        "Position": position,
                        "Player": logic.player_name(row["player"]),
                        "Gain": f"€{row['gain']:.2f}",
                        "Final cash": f"€{row['final_cash']:.2f}",
                        "Stock at cost": f"€{row['stock_at_cost']:.2f}",
                    }
                    for position, row in enumerate(ranking, start=1)
                ]
            )
        except (ValueError, db.DatabaseUnavailable) as error:
            st.error(str(error))
        st.write("Players")
        st.table(
            [
                {"Player": logic.player_name(row["player"]), "Ready": "Ready" if row["ready"] else "not ready"}
                for row in status["players"]
            ]
        )
        return

    st.write(f"Day {status['day']} of {logic.RUN_DAYS}")
    st.write(f"Cash: €{current_stand['cash']:.2f}")
    st.table(
        [
            {
                "Product": product["product"],
                "Stock": product["stock"],
                "Price": f"€{product['price']:.2f}",
            }
            for product in current_stand["products"]
        ]
    )
    st.write("Players")
    st.table(
        [
            {"Player": logic.player_name(row["player"]), "Ready": "Ready" if row["ready"] else "not ready"}
            for row in status["players"]
        ]
    )
    if own_player and own_player["ready"]:
        st.info("You are Ready. Waiting for the other players.")

st.write("Create a tournament")
tournament_name = st.text_input("Tournament name", key="tournament_name")
if st.button("Create tournament"):
    try:
        created = logic.create_tournament(DB_PATH, PLAYER, tournament_name)
        st.session_state["created_tournament"] = created
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

created = st.session_state.get("created_tournament")
if created:
    st.success(f"Tournament created: {created['name']}")
    st.subheader(f"Join code: {created['code']}")

joined_message = st.session_state.pop("joined_message", None)
if joined_message:
    st.success(joined_message)

st.write("Join a tournament")
join_code = st.text_input("Join code", key="tournament_join_code")
if st.button("Join tournament"):
    try:
        joined = logic.join_tournament(DB_PATH, PLAYER, join_code)
        st.session_state["joined_message"] = (
            f"Joined {joined['name']} in seat {joined['seat']}."
        )
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

try:
    my_stands = logic.get_my_stands(DB_PATH, PLAYER)
except (ValueError, db.DatabaseUnavailable) as error:
    st.error(str(error))
    my_stands = []

if my_stands:
    st.write("My tournament stands")
    for stand in my_stands:
        show_tournament(stand, PLAYER)
