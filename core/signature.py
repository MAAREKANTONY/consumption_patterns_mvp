from collections import defaultdict
from core.loader import load_sales
from core.momentum import get_momentum
from core.bucket import get_bucket

BUCKETS = ["food","hot","soft","beer","wine","spirits"]

def compute_outlet_signature(csv_path):
    rev_m = defaultdict(float)
    rev_mb = defaultdict(lambda: defaultdict(float))
    total = 0.0

    for r in load_sales(csv_path):
        b = get_bucket(r["cat0"], r["cat1"], r["cat2"])
        if not b:
            continue
        m = get_momentum(r["datetime"].hour)
        rev = r["price"] * r["quantity"]
        total += rev
        rev_m[m] += rev
        rev_mb[m][b] += rev

    sig = {"revenue_by_momentum":{}, "category_mix_by_momentum":{}}
    for m, v in rev_m.items():
        sig["revenue_by_momentum"][m] = v/total if total else 0
        sig["category_mix_by_momentum"][m] = {
            b: (rev_mb[m][b]/v if v else 0) for b in BUCKETS
        }
    return sig
