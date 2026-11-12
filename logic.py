import csv
import io
import secrets

import db

START_CASH = 100.0
RUN_DAYS = 5
MAX_PLAYER_LENGTH = 254
MAX_TOURNAMENT_NAME_LENGTH = 40
JOIN_CODE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# The catalogue: fixed unit cost and reference price per product.
PRODUCTS = {
    "Café": {"unit_cost": 2.00, "reference_price": 4.00},
    "Croissant": {"unit_cost": 1.50, "reference_price": 3.00},
    "Water": {"unit_cost": 0.50, "reference_price": 1.20},
}


def demand(price, reference_price):
    # CT R1
    if price <= reference_price:
        return 10
    if price <= 2 * reference_price:
        return 5
    return 0


def check_product(product):
    if product not in PRODUCTS:
        raise ValueError(f"Unknown product: {product}.")


def market_sales(product, stands, day):
    """Return the number of units sold by each player for one product."""
    check_product(product)
    reference_price = PRODUCTS[product]["reference_price"]
    sold = {}
    for stand in stands:
        sold[stand["player"]] = 0
    if not stands:
        return sold

    # Rotate the joining order so the day's starting seat comes first.
    by_seat = sorted(stands, key=lambda stand: stand["seat"])
    start = (day - 1) % len(by_seat)
    by_turn = by_seat[start:] + by_seat[:start]

    stands_by_price = {}
    for stand in by_turn:
        price = stand["price"]
        stands_by_price.setdefault(price, []).append(stand)
    prices = sorted(stands_by_price)

    # Each customer group starts at the cheapest price and resets the turn.
    for price_limit in (reference_price, 2 * reference_price):
        customers = 5 * len(stands)
        for price in prices:
            if price > price_limit or customers == 0:
                break
            tied_stands = stands_by_price[price]
            while customers > 0:
                sold_this_round = False
                for stand in tied_stands:
                    player = stand["player"]
                    if sold[player] < stand["stock"]:
                        sold[player] += 1
                        customers -= 1
                        sold_this_round = True
                        if customers == 0:
                            break
                # Move to the next price once every stand here is empty.
                if not sold_this_round:
                    break
    return sold


def check_player(player):
    # The player is their email: non-empty text of at most 254 characters.
    if not isinstance(player, str) or player.strip() == "":
        raise ValueError("Player must be a non-empty email.")
    if len(player) > MAX_PLAYER_LENGTH:
        raise ValueError(f"Player can have at most {MAX_PLAYER_LENGTH} characters.")


def player_from_user(user):
    # The signed-in user (st.user, or any mapping like it) becomes the player:
    # their email, trimmed and lowercased.
    if not user.get("is_logged_in"):
        raise ValueError("Sign in to play.")
    if user.get("email_verified") is False:
        raise ValueError("Your Google email is not verified.")
    email = user.get("email")
    if not isinstance(email, str) or email.strip() == "":
        raise ValueError("Your Google account has no email.")
    return email.strip().lower()


def player_name(player):
    # The part of the email before "@"; without "@", the whole text.
    return player.split("@")[0]


def start_game():
    # The state at the start of every run.
    return {
        "cash": START_CASH,
        "day": 1,
        "stock": {name: 0 for name in PRODUCTS},
        "price": {name: PRODUCTS[name]["reference_price"] for name in PRODUCTS},
    }


def check_tournament_name(name):
    if not isinstance(name, str) or name.strip() == "":
        raise ValueError("Tournament name must be a non-empty name.")
    name = name.strip()
    if len(name) > MAX_TOURNAMENT_NAME_LENGTH:
        raise ValueError(
            f"Tournament name can have at most {MAX_TOURNAMENT_NAME_LENGTH} characters."
        )
    return name


def clean_join_code(code):
    if not isinstance(code, str):
        raise ValueError("Tournament code must be text.")
    return code.strip().upper()


def generate_join_code():
    return "".join(secrets.choice(JOIN_CODE_ALPHABET) for _ in range(6))


def create_tournament(db_path, organiser, name):
    check_player(organiser)
    name = check_tournament_name(name)
    for _ in range(10):
        code = generate_join_code()
        if db.get_tournament_by_code(db_path, code) is None:
            return db.create_tournament(db_path, name, code, organiser, 1)
    raise ValueError("Could not generate a unique tournament code.")


def join_tournament(db_path, player, code):
    check_player(player)
    code = clean_join_code(code)
    tournament = db.get_tournament_by_code(db_path, code)
    if tournament is None:
        raise ValueError("Tournament code was not found.")
    if tournament["day"] != 1:
        raise ValueError("Joining is closed because day 1 has ended.")
    if db.stand_exists(db_path, tournament["id"], player):
        raise ValueError("You have already joined this tournament.")
    products = {
        name: {"stock": 0, "price": details["reference_price"]}
        for name, details in PRODUCTS.items()
    }
    seat = db.join_tournament(db_path, tournament["id"], player, START_CASH, 0, products)
    return {**tournament, "seat": seat}


def get_my_stands(db_path, player):
    check_player(player)
    stands = db.get_player_stands(db_path, player)
    for stand in stands:
        stand["products"] = db.get_stand_products(db_path, stand["id"], player)
    return stands


def load_game(db_path, player):
    check_player(player)
    game = db.get_game(db_path, player)
    if game is None:
        # First time: add the player and give them a new practice game.
        game = start_game()
        db.add_player(db_path, player, player_name(player), game)
    return game


def is_run_complete(game):
    # "day" is the next day to trade, so after the fifth trade it is 6.
    return game["day"] > RUN_DAYS


def check_run_not_complete(game):
    if is_run_complete(game):
        raise ValueError("The run is complete. Start a new run to keep playing.")


def final_result(game):
    # CT R4: remaining stock is valued at purchase cost.
    stock_at_cost = round(
        sum(game["stock"][name] * PRODUCTS[name]["unit_cost"] for name in PRODUCTS), 2
    )
    return {
        "final_cash": float(game["cash"]),
        "stock_at_cost": float(stock_at_cost),
        "gain": round(game["cash"] + stock_at_cost - START_CASH, 2),
    }


def new_run(db_path, player):
    # Back to the start: €100, no stock, reference prices, day 1, empty history.
    # Loading first makes sure the player is in players.
    load_game(db_path, player)
    game = start_game()
    db.reset_game(db_path, player, game)
    return game


def buy_cost(product, quantity):
    # CT02: total cost shown before buying.
    return round(quantity * PRODUCTS[product]["unit_cost"], 2)


def buy(db_path, player, product, quantity):
    check_player(player)
    check_product(product)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")
    game = load_game(db_path, player)
    check_run_not_complete(game)
    cost = buy_cost(product, quantity)
    if cost > game["cash"]:
        raise ValueError(f"Not enough cash: buying costs €{cost:.2f}, you have €{game['cash']:.2f}.")
    game["cash"] = round(game["cash"] - cost, 2)
    game["stock"][product] = game["stock"][product] + quantity
    db.save_game(db_path, player, game)
    return game


def set_price(db_path, player, product, price):
    check_player(player)
    check_product(product)
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Price must be a number.")
    if price <= 0:
        raise ValueError("Price must be more than €0.")
    if round(price, 2) != price:
        raise ValueError("Price can have at most 2 decimals.")
    game = load_game(db_path, player)
    game["price"][product] = float(price)
    db.save_game(db_path, player, game)
    return game


def total_of(by_product):
    # Adds up the results of all products for one day.
    lines = by_product.values()
    revenue = round(sum(line["revenue"] for line in lines), 2)
    cogs = round(sum(line["cogs"] for line in lines), 2)
    return {
        "units_sold": sum(line["units_sold"] for line in lines),
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": round(revenue - cogs, 2),
    }


def trade_day(db_path, player):
    game = load_game(db_path, player)
    check_run_not_complete(game)
    by_product = {}
    for name in PRODUCTS:
        price = game["price"][name]
        units_sold = min(demand(price, PRODUCTS[name]["reference_price"]), game["stock"][name])
        revenue = round(units_sold * price, 2)
        cogs = round(units_sold * PRODUCTS[name]["unit_cost"], 2)
        by_product[name] = {
            "units_sold": units_sold,
            "revenue": float(revenue),
            "cogs": float(cogs),
            "gross_profit": round(revenue - cogs, 2),
        }
        game["stock"][name] = game["stock"][name] - units_sold
    result = {"day": game["day"], "by_product": by_product, "total": total_of(by_product)}
    game["cash"] = round(game["cash"] + result["total"]["revenue"], 2)
    game["day"] = game["day"] + 1
    db.save_day(db_path, player, game, result)
    return result


def get_results(db_path, player):
    # The database keeps one row per day and product; group them by day.
    check_player(player)
    results = []
    for row in db.get_result_rows(db_path, player):
        if not results or results[-1]["day"] != row["day"]:
            results.append({"day": row["day"], "by_product": {}})
        results[-1]["by_product"][row["product"]] = {
            "units_sold": row["units_sold"],
            "revenue": row["revenue"],
            "cogs": row["cogs"],
            "gross_profit": row["gross_profit"],
        }
    for result in results:
        result["total"] = total_of(result["by_product"])
    return results


def build_run_report_csv(rows):
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        ["day", "product", "units_sold", "price", "revenue", "cogs", "gross_profit"]
    )

    total_units_sold = 0
    total_revenue = 0.0
    total_cogs = 0.0
    total_gross_profit = 0.0
    report_rows = []
    for result in rows:
        for product, line in result["by_product"].items():
            units_sold = line["units_sold"]
            revenue = round(line["revenue"], 2)
            cogs = round(line["cogs"], 2)
            gross_profit = round(line["gross_profit"], 2)
            price = "" if units_sold == 0 else round(revenue / units_sold, 2)
            report_rows.append(
                (result["day"], product, units_sold, price, revenue, cogs, gross_profit)
            )
            total_units_sold += units_sold
            total_revenue = round(total_revenue + revenue, 2)
            total_cogs = round(total_cogs + cogs, 2)
            total_gross_profit = round(total_gross_profit + gross_profit, 2)

    for report_row in sorted(report_rows, key=lambda row: (row[0], row[1])):
        writer.writerow(report_row)
    writer.writerow(
        [
            "TOTAL",
            "",
            total_units_sold,
            "",
            round(total_revenue, 2),
            round(total_cogs, 2),
            round(total_gross_profit, 2),
        ]
    )
    return output.getvalue()


def profit_chart_data(results):
    # Turns the saved history (logic.get_results) into data for the charts:
    # one value per day for each product's gross profit, plus the day's total.
    data = {"Day": []}
    for name in PRODUCTS:
        data[name] = []
    data["Total"] = []
    for result in sorted(results, key=lambda result: result["day"]):
        data["Day"].append(result["day"])
        total = 0.0
        for name in PRODUCTS:
            line = result["by_product"].get(name)
            gross_profit = round(float(line["gross_profit"]), 2) if line else 0.0
            data[name].append(gross_profit)
            total = total + gross_profit
        data["Total"].append(round(total, 2))
    return data
