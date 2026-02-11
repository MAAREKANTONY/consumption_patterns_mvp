import argparse
from core.signature import compute_outlet_signature
from core.distance import score_against_patterns
from core.decision import select_best_pattern

def main():
    parser = argparse.ArgumentParser(description="Compute consumption pattern for an outlet")
    parser.add_argument("--csv", required=True, help="Input CSV file")
    parser.add_argument("--patterns", required=True, help="Patterns JSON file")
    args = parser.parse_args()

    signature = compute_outlet_signature(args.csv)
    stats = signature.get("stats", {})

    # Always print data-quality summary
    print("=== DATA QUALITY ===")
    print(f"rows_total_parsed: {stats.get('rows_total_parsed', 0)}")
    print(f"rows_classified:   {stats.get('rows_classified', 0)}")
    print(f"rows_unclassified: {stats.get('rows_unclassified', 0)}")
    print(f"revenue_all:       {stats.get('revenue_total_all', 0.0):.2f}")
    print(f"revenue_classified:{stats.get('revenue_total_classified', 0.0):.2f}")
    print(f"classified_ratio:  {stats.get('classified_revenue_ratio', 0.0):.3f}")
    print("")

    if stats.get("revenue_total_classified", 0.0) == 0.0:
        print("=== PATTERN PROBABILITIES ===")
        print("UNCLASSIFIABLE: no classified revenue in this CSV (all rows unclassified or mapping mismatch).")
        print("SELECTED: UNCLASSIFIABLE")
        return

    scores = score_against_patterns(signature, args.patterns)
    if not scores:
        print("=== PATTERN PROBABILITIES ===")
        print("UNCLASSIFIABLE: patterns file empty/unreadable or scoring failed.")
        print("SELECTED: UNCLASSIFIABLE")
        return

    best = select_best_pattern(scores)

    print("=== PATTERN PROBABILITIES ===")
    for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: {v:.3f}")

    print("\nSELECTED:", best)

if __name__ == "__main__":
    main()

