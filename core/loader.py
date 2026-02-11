import csv
from datetime import datetime
from zoneinfo import ZoneInfo

def _to_float(x):
    if x is None:
        return None
    s = str(x).strip()
    if s == "":
        return None
    # support "12,34"
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def _pick(row, *names):
    """Return first matching column value among possible names (case-sensitive)."""
    for n in names:
        if n in row:
            return row.get(n)
    return None

def _parse_datetime(row):
    """
    Accepts:
      - datetime in format 'YYYY-MM-DD HH:MM:SS UTC'
      - ISO datetime
      - purchase_date + purchase_hour
    Converts everything to Europe/Paris time.
    """

    dt_raw = _pick(row, "datetime", "purchase_datetime")

    if dt_raw:
        dt_raw = str(dt_raw).strip()

        try:
            # Format: 2025-04-18 11:48:00 UTC
            if dt_raw.endswith(" UTC"):
                dt_raw = dt_raw.replace(" UTC", "")
                dt = datetime.fromisoformat(dt_raw)
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                return dt.astimezone(ZoneInfo("Europe/Paris"))

            # ISO with timezone
            dt = datetime.fromisoformat(dt_raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            return dt.astimezone(ZoneInfo("Europe/Paris"))

        except Exception:
            return None

    # fallback legacy format
    date_raw = _pick(row, "purchase_date")
    hour_raw = _pick(row, "purchase_hour")

    try:
        if date_raw and hour_raw:
            dt = datetime.fromisoformat(f"{date_raw} {int(hour_raw):02d}:00:00")
            dt = dt.replace(tzinfo=ZoneInfo("Europe/Paris"))
            return dt
    except Exception:
        return None

    return None


def load_sales(csv_path):
    """
    Yields dict rows in canonical shape:
      datetime, price, quantity, cat0, cat1, cat2
    Accepts taxonomy columns named:
      - cat0/cat1/cat2
      - category0/category1/category2
    Accepts datetime columns named:
      - datetime / purchase_datetime
      - purchase_date + purchase_hour
    Accepts price/quantity columns named:
      - price, quantity (default)
      - unit_price, qty (fallback)
    """
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        # robust delimiter detection (, ; \t)
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except Exception:
            dialect = csv.excel  # default comma

        reader = csv.DictReader(f, dialect=dialect)

        for row in reader:
            dt = _parse_datetime(row)
            if dt is None:
                continue

            price = _to_float(_pick(row, "price", "unit_price", "unitPrice"))
            qty = _to_float(_pick(row, "quantity", "qty", "qte"))

            if price is None or qty is None:
                continue

            cat0 = _pick(row, "cat0", "category0", "category_produit0")
            cat1 = _pick(row, "cat1", "category1", "category_produit1")
            cat2 = _pick(row, "cat2", "category2", "category_produit2")

            # normalize taxonomy strings (strip only; no guessing)
            cat0 = (str(cat0).strip() if cat0 is not None else "")
            cat1 = (str(cat1).strip() if cat1 is not None else "")
            cat2 = (str(cat2).strip() if cat2 is not None else "")

            yield {
                "datetime": dt,
                "price": price,
                "quantity": qty,
                "cat0": cat0,
                "cat1": cat1,
                "cat2": cat2,
            }

