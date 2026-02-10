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
        bucket = get_bucket(r["cat0"], r["cat1"], r["cat2"])
        if not bucket:
            continue  # produit non classifié → ignoré

        momentum = get_momentum(r["datetime"].hour)
        revenue = r["price"] * r["quantity"]

        total += revenue
        rev_m[momentum] += revenue
        rev_mb[momentum][bucket] += revenue

    # Signature canonique : TOUS les momenta et buckets présents
    signature = {
        "revenue_by_momentum": {m: 0.0 for m in MOMENTA},
        "category_mix_by_momentum": {
            m: {b: 0.0 for b in BUCKETS} for m in MOMENTA
        },
        "total_classified_revenue": total
    }

    if total == 0:
        return signature

    # Part de CA par momentum
    for m in MOMENTA:
        signature["revenue_by_momentum"][m] = rev_m[m] / total

        if rev_m[m] > 0:
            for b in BUCKETS:
                signature["category_mix_by_momentum"][m][b] = (
                    rev_mb[m][b] / rev_m[m]
                )

    return signature

