import csv
from datetime import datetime

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
    Supports either:
      - datetime / purchase_datetime
      - purchase_date + purchase_hour (hour int 0-23)
      - purchase_date + purchase_time (HH:MM or HH:MM:SS)
    """
    dt_raw = _pick(row, "datetime", "purchase_datetime", "created_at")
    if dt_raw:
        dt_raw = str(dt_raw).strip()
        for fmt in (
            None,  # fromisoformat
        ):
            try:
                return datetime.fromisoformat(dt_raw)
            except Exception:
                pass

    date_raw = _pick(row, "purchase_date", "date", "day")
    if not date_raw:
        return None
    date_raw = str(date_raw).strip()

    hour_raw = _pick(row, "purchase_hour", "hour")
    time_raw = _pick(row, "purchase_time", "time")

    try:
        if hour_raw is not None and str(hour_raw).strip() != "":
            h = int(float(str(hour_raw).strip().replace(",", ".")))
            return datetime.fromisoformat(f"{date_raw} {h:02d}:00:00")

        if time_raw:
            t = str(time_raw).strip()
            # accept HH:MM or HH:MM:SS
            if len(t.split(":")) == 2:
                t = t + ":00"
            return datetime.fromisoformat(f"{date_raw} {t}")

        # fallback: just date at midnight
        return datetime.fromisoformat(f"{date_raw} 00:00:00")
    except Exception:
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

