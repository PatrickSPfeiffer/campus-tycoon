import db

START_CASH = 100.0

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


def load_game(db_path):
    game = db.get_game(db_path)
    if game is None:
        game = {
            "cash": START_CASH,
            "day": 1,
            "stock": {name: 0 for name in PRODUCTS},
            "price": {name: PRODUCTS[name]["reference_price"] for name in PRODUCTS},
        }
        db.save_game(db_path, game)
    return game


def buy_cost(product, quantity):
    # CT02: total cost shown before buying.
    return round(quantity * PRODUCTS[product]["unit_cost"], 2)


def buy(db_path, product, quantity):
    check_product(product)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")
    game = load_game(db_path)
    cost = buy_cost(product, quantity)
    if cost > game["cash"]:
        raise ValueError(f"Not enough cash: buying costs €{cost:.2f}, you have €{game['cash']:.2f}.")
    game["cash"] = round(game["cash"] - cost, 2)
    game["stock"][product] = game["stock"][product] + quantity
    db.save_game(db_path, game)
    return game


def set_price(db_path, product, price):
    check_product(product)
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Price must be a number.")
    if price <= 0:
        raise ValueError("Price must be more than €0.")
    if round(price, 2) != price:
        raise ValueError("Price can have at most 2 decimals.")
    game = load_game(db_path)
    game["price"][product] = float(price)
    db.save_game(db_path, game)
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


def trade_day(db_path):
    game = load_game(db_path)
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
    db.save_day(db_path, game, result)
    return result


def get_results(db_path):
    # The database keeps one row per day and product; group them by day.
    results = []
    for row in db.get_result_rows(db_path):
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
