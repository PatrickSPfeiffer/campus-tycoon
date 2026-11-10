import streamlit as st

import db
import logic

DB_PATH = db.DEFAULT_PATH

st.title("Campus Tycoon")

try:
    game = logic.load_game(DB_PATH)
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
            logic.new_run(DB_PATH)
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
        logic.set_price(DB_PATH, price_product, round(float(new_price), 2))
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

st.subheader("Buy")
buy_product = st.selectbox("Product", list(logic.PRODUCTS), key="buy_product")
quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
st.write(f"Total cost €{logic.buy_cost(buy_product, int(quantity)):.2f}")
if st.button("Buy", disabled=run_complete):
    try:
        logic.buy(DB_PATH, buy_product, int(quantity))
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

st.subheader("Trade")
if st.button("Trade one day", disabled=run_complete):
    try:
        logic.trade_day(DB_PATH)
        st.rerun()
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))

st.subheader("Results")
try:
    results = logic.get_results(DB_PATH)
except db.DatabaseUnavailable as error:
    st.error(str(error))
    results = []
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
