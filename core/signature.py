from collections import defaultdict
from core.loader import load_sales
from core.momentum import get_momentum
from core.bucket import get_bucket

MOMENTA = ["breakfast", "lunch", "coffee", "apero", "dinner", "after"]
BUCKETS = ["food", "hot", "soft", "beer", "wine", "spirits"]

def compute_outlet_signature(csv_path):
    rev_m = defaultdict(float)
    rev_mb = defaultdict(lambda: defaultdict(float))
    total = 0.0

    for r in load_sales(csv_path):
        b = get_bucket(r["cat0"], r["cat1"], r["cat2"])
        if not b:
            continue  # non classifié -> ignoré

        m = get_momentum(r["datetime"].hour)
        rev = r["price"] * r["quantity"]

        total += rev
        rev_m[m] += rev
        rev_mb[m][b] += rev

    # signature canonique (TOUS les momenta, même si 0)
    sig = {
        "revenue_by_momentum": {m: 0.0 for m in MOMENTA},
        "category_mix_by_momentum": {m: {b: 0.0 for b in BUCKETS} for m in MOMENTA},
    }

    if total == 0:
        # aucun CA classifié -> signature nulle
        return sig

    # Revenue share by momentum
    for m in MOMENTA:
        sig["revenue_by_momentum"][m] = rev_m[m] / total

    # Category mix within each momentum 
    for m in MOMENTA:
        denom = rev_m[m]
        if denom > 0:
            for b in BUCKETS:
                sig["category_mix_by_momentum"][m][b] = rev_mb[m][b] / denom

    return sig

