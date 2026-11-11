import csv
import io

from logic import build_run_report_csv


def read_report(rows):
    return list(csv.DictReader(io.StringIO(build_run_report_csv(rows))))


def test_report_has_correct_header():
    rows = [
        {
            "day": 1,
            "by_product": {
                "Café": {
                    "units_sold": 2,
                    "revenue": 8.0,
                    "cogs": 4.0,
                    "gross_profit": 4.0,
                }
            },
        }
    ]

    report = build_run_report_csv(rows)

    assert report.splitlines()[0] == "day,product,units_sold,price,revenue,cogs,gross_profit"


def test_report_calculates_price():
    rows = [
        {
            "day": 1,
            "by_product": {
                "Café": {
                    "units_sold": 3,
                    "revenue": 10.0,
                    "cogs": 6.0,
                    "gross_profit": 4.0,
                }
            },
        }
    ]

    report = read_report(rows)

    assert report[0]["price"] == "3.33"


def test_report_leaves_price_empty_when_no_units_sold():
    rows = [
        {
            "day": 1,
            "by_product": {
                "Water": {
                    "units_sold": 0,
                    "revenue": 0.0,
                    "cogs": 0.0,
                    "gross_profit": 0.0,
                }
            },
        }
    ]

    report = read_report(rows)

    assert report[0]["price"] == ""


def test_report_total_row_has_right_sums():
    rows = [
        {
            "day": 1,
            "by_product": {
                "Café": {
                    "units_sold": 2,
                    "revenue": 8.0,
                    "cogs": 4.0,
                    "gross_profit": 4.0,
                },
                "Water": {
                    "units_sold": 3,
                    "revenue": 3.6,
                    "cogs": 1.5,
                    "gross_profit": 2.1,
                },
            },
        }
    ]

    report = read_report(rows)

    assert report[-1] == {
        "day": "TOTAL",
        "product": "",
        "units_sold": "5",
        "price": "",
        "revenue": "11.6",
        "cogs": "5.5",
        "gross_profit": "6.1",
    }


def test_report_rows_are_sorted_by_day_then_product():
    rows = [
        {
            "day": 2,
            "by_product": {
                "Water": {
                    "units_sold": 1,
                    "revenue": 1.2,
                    "cogs": 0.5,
                    "gross_profit": 0.7,
                },
                "Café": {
                    "units_sold": 1,
                    "revenue": 4.0,
                    "cogs": 2.0,
                    "gross_profit": 2.0,
                },
            },
        },
        {
            "day": 1,
            "by_product": {
                "Water": {
                    "units_sold": 1,
                    "revenue": 1.2,
                    "cogs": 0.5,
                    "gross_profit": 0.7,
                },
                "Café": {
                    "units_sold": 1,
                    "revenue": 4.0,
                    "cogs": 2.0,
                    "gross_profit": 2.0,
                },
            },
        },
    ]

    report = read_report(rows)

    assert [(row["day"], row["product"]) for row in report[:-1]] == [
        ("1", "Café"),
        ("1", "Water"),
        ("2", "Café"),
        ("2", "Water"),
    ]
