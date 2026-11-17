import streamlit as st

import advisor
import db
import logic
import mailer
import weather

DB_PATH = db.DEFAULT_PATH

st.set_page_config(page_title="Campus Tycoon", page_icon=":material/local_cafe:", layout="wide")


ICONS = {
    "coffee": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h13v7a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4V8Z"/><path d="M17 10h1a3 3 0 0 1 0 6h-2M7 3v2m5-2v2m5-2v2"/></svg>',
    "croissant": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8c1-3 4-5 7-5s6 2 7 5l2 8-5 5-4-3-4 3-5-5 2-8Z"/><path d="m5 8 5 5m9-5-5 5m-6 6 3-6m8 6-3-6"/></svg>',
    "droplet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3s-7 7.5-7 12a7 7 0 0 0 14 0c0-4.5-7-12-7-12Z"/><path d="M9 16a3 3 0 0 0 3 3"/></svg>',
    "cart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="20" r="1"/><circle cx="18" cy="20" r="1"/><path d="M2 3h2l3 12h12l3-9H5"/></svg>',
    "wallet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 8h18m-5 6h2M6 5V3h12v2"/></svg>',
    "trending-up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 17 6-6 4 4 8-9"/><path d="M15 6h6v6"/></svg>',
    "trophy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8m-4-4v4M7 4h10v6a5 5 0 0 1-10 0V4Z"/><path d="M7 7H4v2a4 4 0 0 0 4 4m9-6h3v2a4 4 0 0 1-4 4"/></svg>',
    "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2H3Zm13-9a3 3 0 1 0 0-6m1 9a5 5 0 0 1 4 5v1h-3"/></svg>',
    "cloud-rain": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 15a5 5 0 1 1 1-9.9A7 7 0 0 1 21 9a4 4 0 0 1-1 6"/><path d="m8 17-1 3m6-3-1 3m6-3-1 3"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "cloud-sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17a5 5 0 1 1 1-9.9A7 7 0 0 1 21 11a4 4 0 0 1-1 6H7Z"/><path d="M12 2v2m-5 .2 1.4 1.4M3 10h2"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "box": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="M3 8v9l9 5 9-5V8m-9 5v9"/></svg>',
}


def icon(name, size=22):
    svg = ICONS.get(name, ICONS["box"])
    return f'<span class="app-icon" style="width:{size}px;height:{size}px">{svg}</span>'


def inject_css():
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root { --bg1:#140B08; --glow1:#7A3B16; --glow2:#C2410C; --amber:#F5A524; --orange:#FF7A18; --text:#F6EBDD; --muted:#C9B8A6; --card:rgba(255,255,255,0.06); --card-border:rgba(255,255,255,0.10); --good:#4ADE80; --bad:#F87171; }
html, body, [class*="css"] { font-family:'Plus Jakarta Sans', sans-serif; }
.stApp { background: radial-gradient(900px 500px at 8% -5%, var(--glow1), transparent 60%), radial-gradient(800px 500px at 100% 0%, rgba(194,65,12,.22), transparent 55%), linear-gradient(180deg, #1B0F0A, var(--bg1)); background-attachment:fixed; color:var(--text); }
[data-testid="stHeader"], [data-testid="stToolbar"] { background:transparent; }
[data-testid="stMainBlockContainer"] { max-width:1240px; margin:0 auto; padding:2rem 2rem 4rem; }
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] { background:var(--card); border:1px solid var(--card-border); border-radius:20px; backdrop-filter:blur(12px); box-shadow:0 12px 36px rgba(0,0,0,.18); transition:transform .2s ease, box-shadow .2s ease; }
[data-testid="stMetric"] { padding:16px; }
[data-testid="stMetric"]:hover, [data-testid="stVerticalBlockBorderWrapper"]:hover { transform:translateY(-2px); box-shadow:0 16px 40px rgba(0,0,0,.25); }
.stButton button, .stDownloadButton button { border-radius:14px; font-weight:700; transition:all .2s ease; }
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] { background:linear-gradient(135deg,var(--amber),var(--orange)); border:0; color:#2B1608; }
.stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover { box-shadow:0 0 24px rgba(245,165,36,.35); }
.stButton button:not([kind="primary"]), .stDownloadButton button:not([kind="primary"]) { background:transparent; border:1px solid var(--card-border); }
.stButton button:not([kind="primary"]):hover, .stDownloadButton button:not([kind="primary"]):hover { border-color:var(--amber); color:var(--amber); }
input, textarea, [data-baseweb="select"] > div { border-radius:12px !important; background:var(--card) !important; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:8px; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"] { display:none; }
[data-testid="stTabs"] [data-testid="stTab"], [data-testid="stTabs"] [role="tab"] { border-radius:999px; padding:8px 20px; background:var(--card); border:1px solid transparent; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { background:linear-gradient(135deg,var(--amber),var(--orange)); color:#2B1608; }
[data-testid="stMetricValue"] { color:var(--text); font-size:2rem; font-weight:800; }
[data-testid="stMetricLabel"] { color:var(--muted); }
.hero { background:linear-gradient(135deg,rgba(245,165,36,.18),rgba(255,122,24,.10)),var(--card); border:1px solid rgba(245,165,36,.28); border-radius:24px; padding:28px 32px; margin-bottom:12px; box-shadow:0 0 40px rgba(194,65,12,.12); backdrop-filter:blur(12px); }
.hero h1 { background:linear-gradient(90deg,var(--amber),var(--orange)); background-clip:text; -webkit-background-clip:text; color:transparent; font-size:2.7rem; font-weight:800; margin:0; }
.hero p { color:var(--muted); font-size:1rem; margin:4px 0 0; }
.app-icon { display:inline-flex; color:var(--amber); vertical-align:middle; flex:none; }
.app-icon svg { width:100%; height:100%; }
[data-testid="stDataFrame"], [data-testid="stTable"] { color:var(--text); }
[data-testid="stTable"] table { background:var(--card); }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition:none !important; scroll-behavior:auto !important; } }
</style>""", unsafe_allow_html=True)


inject_css()


def show_hero():
    st.markdown(f'<div class="hero"><h1>{icon("coffee", 30)} Campus Tycoon</h1><p>Run a small campus shop for five days.</p></div>', unsafe_allow_html=True)

# Before signing in: only a short welcome and the sign-in button, no game data.
if not st.user.is_logged_in:
    show_hero()
    st.write("Welcome! Run a small campus shop for five days. Sign in to play.")
    if st.button("Sign in with Google", type="primary"):
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

show_hero()
col1, col2 = st.columns([12, 1], vertical_alignment="center")
with col1:
    st.caption(f"Signed in as {PLAYER}")
with col2:
    if st.button("Sign out"):
        st.logout()

try:
    game = logic.load_game(DB_PATH, PLAYER)
except db.DatabaseUnavailable as error:
    st.error(str(error))
    st.stop()
run_complete = logic.is_run_complete(game)

col1, col2, col3 = st.columns(3)
col1.metric("Cash", f"€{game['cash']:.2f}")
if run_complete:
    col2.metric("Progress", "Run complete")
else:
    col2.metric("Progress", f"Day {game['day']} of {logic.RUN_DAYS}")
col3.metric("Loan to repay", f"€{game['debt']:.2f}")
st.caption(f"Level: {logic.level_name(game)} (started with €{game['start_cash']:.2f})")

practice_tab, tournament_tab, help_tab = st.tabs([
    ":material/storefront: Practice",
    ":material/emoji_events: Tournaments",
    ":material/help: How to play",
])

with practice_tab:

    if run_complete:
        final = logic.final_result(game)
        st.subheader("Final result")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Final cash", f"€{final['final_cash']:.2f}")
        col2.metric("Remaining stock at cost", f"€{final['stock_at_cost']:.2f}")
        col3.metric("Loan to repay", f"€{game['debt']:.2f}")
        col4.metric("Overall gain or loss", f"€{final['gain']:.2f}")
        email_status = st.session_state.pop("email_status", None)
        if email_status == "sent":
            st.success(f"Your result was emailed to {PLAYER}.")
        elif email_status == "skipped":
            st.info("Result email is not configured, so no email was sent.")
        elif email_status == "failed":
            st.warning("We could not send the email, but your result is saved.")

    if not run_complete:
      with st.expander("AI business advisor"):
        if st.button("Ask the advisor"):
            api_key = st.secrets.get("OPENROUTER_API_KEY", "")
            advice = logic.get_advice(
                game,
                lambda prompt: advisor.ask_openrouter(prompt, api_key),
            )
            label = "AI suggestion" if advice["source"] == "ai" else "Basic tip (AI not available)"
            st.write(label)
            st.table(
                [
                    {
                        "Product": product,
                        "Price": f"€{line['price']:.2f}",
                        "Reason": line["reason"],
                    }
                    for product, line in advice["prices"].items()
                ]
            )

    with st.expander("New run", expanded=run_complete):
        new_level = st.selectbox(
            "Difficulty",
            list(logic.DIFFICULTY_LEVELS),
            index=list(logic.DIFFICULTY_LEVELS).index("Normal"),
            format_func=lambda name: f"{name} (€{logic.DIFFICULTY_LEVELS[name]:.0f} to start)",
            key="new_run_level",
        )
        if not st.session_state.get("confirm_new_run"):
            if st.button("Start a new run"):
                st.session_state["confirm_new_run"] = True
                st.rerun()
        else:
            st.warning(f"Start a new {new_level} run? The current run and its history will be lost.")
            col1, col2 = st.columns(2)
            if col1.button("Yes, start a new run"):
                try:
                    logic.new_run(DB_PATH, PLAYER, new_level)
                    st.session_state["confirm_new_run"] = False
                    st.rerun()
                except (ValueError, db.DatabaseUnavailable) as error:
                    st.error(str(error))
            if col2.button("Cancel"):
                st.session_state["confirm_new_run"] = False
                st.rerun()

    st.markdown(f"{icon('cart')} Products", unsafe_allow_html=True)
    if not run_complete:
        preview = logic.demand_preview(game)

    icons = {"Café": "coffee", "Croissant": "croissant", "Water": "droplet"}
    product_columns = st.columns(3)
    for index, (name, details) in enumerate(logic.PRODUCTS.items()):
        with product_columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"{icon(icons.get(name, 'box'))} {name}", unsafe_allow_html=True)
                st.write(f"Stock: {game['stock'][name]}")
                st.write(f"Price: €{game['price'][name]:.2f}")
                if not run_complete:
                    st.write(f"Demand: {preview[name]['demand']}")
                    st.write(f"Will sell: {preview[name]['will_sell']}")
                st.caption(f"Unit cost: €{details['unit_cost']:.2f} · Reference price: €{details['reference_price']:.2f}")
    st.caption(
        "Demand per product per day: 10 units at or below its reference price, "
        "5 units up to twice the reference price, 0 units above that."
    )

    action_columns = st.columns(3)
    with action_columns[0]:
      with st.container(border=True):
        st.markdown(f"{icon('trending-up')} Selling price", unsafe_allow_html=True)
        price_product = st.selectbox("Product", list(logic.PRODUCTS), key="price_product")
        new_price = st.number_input(
            "Price (€)", step=0.01, value=game["price"][price_product], format="%.2f",
            key=f"price_{price_product}",
        )
        if st.button("Set price", use_container_width=True):
            try:
                logic.set_price(DB_PATH, PLAYER, price_product, round(float(new_price), 2))
                st.rerun()
            except (ValueError, db.DatabaseUnavailable) as error:
                st.error(str(error))

    with action_columns[1]:
      with st.container(border=True):
        st.markdown(f"{icon('wallet')} Loan", unsafe_allow_html=True)
        st.caption(
            f"Borrow up to €{logic.LOAN_MAX} once per run. You pay it back with "
            f"{logic.LOAN_INTEREST:.0%} interest: the debt is subtracted from your final gain."
        )
        has_loan = game["debt"] > 0
        loan_amount = st.number_input(
            "Amount (€)", min_value=1, max_value=logic.LOAN_MAX, step=1, value=logic.LOAN_MAX,
            key="loan_amount",
        )
        st.write(f"You will owe €{logic.loan_debt(int(loan_amount)):.2f}")
        if st.button("Take loan", disabled=run_complete or has_loan, use_container_width=True):
            try:
                logic.take_loan(DB_PATH, PLAYER, int(loan_amount))
                st.rerun()
            except (ValueError, db.DatabaseUnavailable) as error:
                st.error(str(error))

    with action_columns[2]:
      with st.container(border=True):
        st.markdown(f"{icon('cart')} Buy", unsafe_allow_html=True)
        buy_product = st.selectbox("Product", list(logic.PRODUCTS), key="buy_product")
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
        st.write(f"Total cost €{logic.buy_cost(buy_product, int(quantity)):.2f}")
        if st.button("Buy", disabled=run_complete, use_container_width=True, icon=":material/shopping_cart:"):
            try:
                logic.buy(DB_PATH, PLAYER, buy_product, int(quantity))
                st.rerun()
            except (ValueError, db.DatabaseUnavailable) as error:
                st.error(str(error))

    if st.button("Trade one day", disabled=run_complete, type="primary", use_container_width=True, icon=":material/play_arrow:"):
        try:
            logic.trade_day(DB_PATH, PLAYER)
            game = logic.load_game(DB_PATH, PLAYER)
            if logic.is_run_complete(game):
                with st.spinner("Sending your result by email..."):
                    st.session_state["email_status"] = mailer.send_result_email(
                        PLAYER, logic.final_result(game)
                    )
            st.rerun()
        except (ValueError, db.DatabaseUnavailable) as error:
            st.error(str(error))

    st.markdown(f"{icon('trending-up')} Results", unsafe_allow_html=True)
    try:
        results = logic.get_results(DB_PATH, PLAYER)
    except db.DatabaseUnavailable as error:
        st.error(str(error))
        results = []

    # History charts: built only from this player's own saved results.
    chart_data = logic.profit_chart_data(results)
    if chart_data["Day"]:
        st.write("Gross profit per day by product")
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.bar_chart(
                chart_data, x="Day", y=list(logic.PRODUCTS), stack=False,
                x_label="Day", y_label="Gross profit (€)",
            )
        with chart_col2:
            st.write("Total gross profit per day")
            st.line_chart(
                chart_data, x="Day", y="Total", x_label="Day", y_label="Gross profit (€)",
            )
    else:
        st.info("Trade a day to see your charts.")

    for result in results:
        with st.expander(f"Day {result['day']}"):
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
            type="primary",
        )

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
        today_weather = logic.tournament_weather(DB_PATH, tournament_id, weather.fetch_lisbon_weather)
        if today_weather["rain"]:
            weather_name = "rain"
        elif today_weather["hot"]:
            weather_name = "hot"
        else:
            weather_name = "normal"
        st.write(f"Today in Lisbon: {weather_name}")
    except (ValueError, db.DatabaseUnavailable) as error:
        st.error(str(error))
        return
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

            st.write("Upgrades")
            try:
                owned = logic.tournament_upgrades(DB_PATH, player, tournament_id)
                for name, details in logic.UPGRADES.items():
                    if name in owned:
                        st.write(f"{name}: Owned")
                    elif st.button(
                        f"Buy {name} (€{details['cost']:.2f})",
                        key=f"tournament_upgrade_{tournament_id}_{name}",
                    ):
                        try:
                            logic.buy_tournament_upgrade(
                                DB_PATH, player, tournament_id, name
                            )
                            action_message = "Upgrade purchased."
                        except (ValueError, db.DatabaseUnavailable) as error:
                            action_error = str(error)
            except (ValueError, db.DatabaseUnavailable) as error:
                st.error(str(error))

            if st.button("Ready", key=f"tournament_ready_{tournament_id}", icon=":material/check:"):
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

with tournament_tab:
    st.markdown(f"{icon('trophy')} Create a tournament", unsafe_allow_html=True)
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

    st.markdown(f"{icon('users')} Join a tournament", unsafe_allow_html=True)
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


with help_tab:
    st.subheader("Goal")
    st.write("Finish five days with the highest gain.")
    st.subheader("Each day")
    st.write("Buy stock, set prices, then trade one day.")
    st.subheader("Demand")
    st.write(
        "Demand per product per day: 10 units at or below its reference price, "
        "5 units up to twice the reference price, 0 units above that."
    )
    st.subheader("Loan")
    st.write(
        f"Borrow up to €{logic.LOAN_MAX} once per run. You pay it back with "
        f"{logic.LOAN_INTEREST:.0%} interest, which is subtracted from your final gain."
    )
    st.subheader("Tournaments")
    upgrade_cost = next(details["cost"] for details in logic.UPGRADES.values())
    st.write(
        "Join with a code to play in a shared market. The cheapest price sells first. "
        "Players use Ready and the organiser can Close day. Weather comes from Lisbon. "
        f"You can buy a Coffee machine upgrade for €{upgrade_cost:.2f}."
    )
