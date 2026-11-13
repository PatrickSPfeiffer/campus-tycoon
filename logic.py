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


def tournament_status(db_path, player, tournament_id):
    check_player(player)
    tournament = db.get_tournament(db_path, tournament_id)
    if tournament is None:
        raise ValueError("Tournament was not found.")
    stands = db.get_tournament_stands(db_path, tournament_id)
    if player != tournament["organiser"] and player not in stands:
        raise ValueError("You have not joined this tournament.")
    return {
        "day": tournament["day"],
        "organiser": tournament["organiser"],
        "players": [
            {"player": stand["player"], "seat": stand["seat"], "ready": bool(stand["ready"])}
            for stand in sorted(stands.values(), key=lambda item: item["seat"])
        ],
    }


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


def tournament_units_sold(stands):
    """Apply the current per-stand demand rule to each stand's stock and prices."""
    sold = {}
    for player, stand in stands.items():
        sold[player] = {}
        for product in stand["stock"]:
            units = min(
                demand(stand["price"][product], PRODUCTS[product]["reference_price"]),
                stand["stock"][product],
            )
            sold[player][product] = units
    return sold


def _tournament_for_action(db_path, tournament_id, action):
    tournament = db.get_tournament(db_path, tournament_id)
    if tournament is None:
        raise ValueError("Tournament was not found.")
    if action == "ranking":
        if tournament["day"] != RUN_DAYS + 1:
            raise ValueError("The tournament is not complete.")
    elif tournament["day"] == RUN_DAYS + 1:
        raise ValueError("The tournament is complete.")
    return tournament


def _tournament_stand_for_action(db_path, tournament_id, player):
    stands = db.get_tournament_stands(db_path, tournament_id)
    if player not in stands:
        raise ValueError("You have not joined this tournament.")
    return stands[player]


def _check_tournament_quantity(quantity):
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")


def _check_tournament_price(price):
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Price must be a number.")
    if price <= 0:
        raise ValueError("Price must be more than €0.")
    if round(price, 2) != price:
        raise ValueError("Price can have at most 2 decimals.")


def buy_tournament_stock(db_path, player, tournament_id, product, quantity):
    _tournament_for_action(db_path, tournament_id, "buy")
    stand = _tournament_stand_for_action(db_path, tournament_id, player)
    if stand["ready"]:
        raise ValueError("You are Ready and cannot change decisions.")
    check_product(product)
    _check_tournament_quantity(quantity)
    cost = buy_cost(product, quantity)
    if cost > stand["cash"]:
        raise ValueError(
            f"Not enough cash: buying costs €{cost:.2f}, you have €{stand['cash']:.2f}."
        )
    cash = round(stand["cash"] - cost, 2)
    db.set_tournament_stock(db_path, tournament_id, player, product, quantity, cash)
    return {"cash": cash, "stock": stand["stock"][product] + quantity}


def set_tournament_price(db_path, player, tournament_id, product, price):
    _tournament_for_action(db_path, tournament_id, "price")
    stand = _tournament_stand_for_action(db_path, tournament_id, player)
    if stand["ready"]:
        raise ValueError("You are Ready and cannot change decisions.")
    check_product(product)
    _check_tournament_price(price)
    db.set_tournament_price(db_path, tournament_id, player, product, float(price))
    return float(price)


def ready_tournament(db_path, player, tournament_id):
    _tournament_for_action(db_path, tournament_id, "ready")
    stand = _tournament_stand_for_action(db_path, tournament_id, player)
    if stand["ready"]:
        raise ValueError("You are already Ready.")
    all_ready = db.set_tournament_ready(db_path, tournament_id, player)
    if not all_ready:
        return {"closed_day": None}
    return {"closed_day": _close_tournament_day(db_path, tournament_id)}


def close_tournament_day(db_path, player, tournament_id):
    tournament = _tournament_for_action(db_path, tournament_id, "close")
    if player != tournament["organiser"]:
        raise ValueError("Only the organiser can close the day early.")
    stands = db.get_tournament_stands(db_path, tournament_id)
    if not stands:
        raise ValueError("A tournament with no players cannot be closed.")
    return _close_tournament_day(db_path, tournament_id, stands=stands, day=tournament["day"])


def _close_tournament_day(db_path, tournament_id, stands=None, day=None):
    if stands is None:
        stands = db.get_tournament_stands(db_path, tournament_id)
    if day is None:
        day = db.get_tournament(db_path, tournament_id)["day"]
    sales = tournament_units_sold(stands)
    by_player = {}
    for player, stand in stands.items():
        by_player[player] = {}
        for product, units in sales[player].items():
            revenue = round(units * stand["price"][product], 2)
            cogs = round(units * PRODUCTS[product]["unit_cost"], 2)
            by_player[player][product] = {
                "units_sold": units,
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": round(revenue - cogs, 2),
            }
    return db.close_tournament_day(db_path, tournament_id, day, stands, by_player)


def tournament_ranking(db_path, tournament_id):
    _tournament_for_action(db_path, tournament_id, "ranking")
    ranking = []
    for stand in db.get_tournament_ranking_rows(db_path, tournament_id):
        result = final_result({"cash": stand["cash"], "stock": stand["stock"]})
        ranking.append({
            "player": stand["player"], "seat": stand["seat"],
            "final_cash": result["final_cash"], "stock_at_cost": result["stock_at_cost"],
            "gain": result["gain"],
        })
    return sorted(ranking, key=lambda row: (-row["gain"], row["seat"]))


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
