import streamlit as st

import db
import logic

DB_PATH = db.DEFAULT_PATH

st.title("Campus Tycoon")

game = logic.load_game(DB_PATH)

col1, col2 = st.columns(2)
col1.metric("Cash", f"€{game['cash']:.2f}")
col2.metric("Day", game["day"])

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
    except ValueError as error:
        st.error(str(error))

st.subheader("Buy")
buy_product = st.selectbox("Product", list(logic.PRODUCTS), key="buy_product")
quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
st.write(f"Total cost €{logic.buy_cost(buy_product, int(quantity)):.2f}")
if st.button("Buy"):
    try:
        logic.buy(DB_PATH, buy_product, int(quantity))
        st.rerun()
    except ValueError as error:
        st.error(str(error))

st.subheader("Trade")
if st.button("Trade one day"):
    logic.trade_day(DB_PATH)
    st.rerun()

st.subheader("Results")
for result in logic.get_results(DB_PATH):
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
