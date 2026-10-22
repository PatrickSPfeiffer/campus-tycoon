import db

START_CASH = 100.0
UNIT_COST = 2.00
REFERENCE_PRICE = 4.00


def demand(price, reference_price):
    # CT R1
    if price <= reference_price:
        return 10
    if price <= 2 * reference_price:
        return 5
    return 0


def load_game(db_path):
    game = db.get_game(db_path)
    if game is None:
        game = {"cash": START_CASH, "stock": 0, "day": 1, "price": REFERENCE_PRICE}
        db.save_game(db_path, game)
    return game


def buy(db_path, quantity):
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")
    game = load_game(db_path)
    cost = round(quantity * UNIT_COST, 2)
    if cost > game["cash"]:
        raise ValueError(f"Not enough cash: buying costs €{cost:.2f}, you have €{game['cash']:.2f}.")
    game["cash"] = round(game["cash"] - cost, 2)
    game["stock"] = game["stock"] + quantity
    db.save_game(db_path, game)
    return game


def set_price(db_path, price):
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Price must be a number.")
    if price <= 0:
        raise ValueError("Price must be more than €0.")
    if round(price, 2) != price:
        raise ValueError("Price can have at most 2 decimals.")
    game = load_game(db_path)
    game["price"] = float(price)
    db.save_game(db_path, game)
    return game


def trade_day(db_path):
    game = load_game(db_path)
    units_sold = min(demand(game["price"], REFERENCE_PRICE), game["stock"])
    revenue = round(units_sold * game["price"], 2)
    cogs = round(units_sold * UNIT_COST, 2)
    result = {
        "day": game["day"],
        "units_sold": units_sold,
        "revenue": float(revenue),
        "cogs": float(cogs),
        "gross_profit": round(revenue - cogs, 2),
    }
    game["cash"] = round(game["cash"] + revenue, 2)
    game["stock"] = game["stock"] - units_sold
    game["day"] = game["day"] + 1
    db.save_day(db_path, game, result)
    return result


def get_results(db_path):
    return db.get_results(db_path)
