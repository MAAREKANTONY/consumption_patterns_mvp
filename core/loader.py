import csv
from datetime import datetime

def load_sales(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                yield {
                    "datetime": datetime.fromisoformat(r["datetime"]),
                    "price": float(r["price"]),
                    "quantity": float(r["quantity"]),
                    "cat0": r["cat0"],
                    "cat1": r["cat1"],
                    "cat2": r["cat2"],
                }
            except Exception:
                continue
