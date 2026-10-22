import streamlit as st

import db
import logic

DB_PATH = db.DEFAULT_PATH

st.title("Campus Tycoon")

game = logic.load_game(DB_PATH)

col1, col2, col3 = st.columns(3)
col1.metric("Cash", f"€{game['cash']:.2f}")
col2.metric("Café stock", game["stock"])
col3.metric("Day", game["day"])

st.subheader("Selling price")
st.write(f"Current price €{game['price']:.2f}")
st.caption(
    f"Demand per day: 10 units at or below €{logic.REFERENCE_PRICE:.2f}, "
    f"5 units up to €{2 * logic.REFERENCE_PRICE:.2f}, 0 units above that."
)
new_price = st.number_input("Price (€)", step=0.01, value=game["price"], format="%.2f")
if st.button("Set price"):
    try:
        logic.set_price(DB_PATH, round(float(new_price), 2))
        st.rerun()
    except ValueError as error:
        st.error(str(error))

st.subheader("Buy Café")
st.write(f"Unit cost €{logic.UNIT_COST:.2f}")
quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
if st.button("Buy"):
    try:
        logic.buy(DB_PATH, int(quantity))
        st.rerun()
    except ValueError as error:
        st.error(str(error))

st.subheader("Trade")
if st.button("Trade one day"):
    logic.trade_day(DB_PATH)
    st.rerun()

st.subheader("Results")
for result in logic.get_results(DB_PATH):
    st.write(
        f"Day {result['day']}: sold {result['units_sold']}, "
        f"revenue €{result['revenue']:.2f}, "
        f"COGS €{result['cogs']:.2f}, "
        f"gross profit €{result['gross_profit']:.2f}"
    )
