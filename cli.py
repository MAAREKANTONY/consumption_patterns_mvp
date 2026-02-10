import argparse
from core.signature import compute_outlet_signature
from core.distance import score_against_patterns
from core.decision import select_best_pattern

def main():
    parser = argparse.ArgumentParser(
        description="Compute consumption pattern for an outlet"
    )
    parser.add_argument("--csv", required=True, help="Input CSV file")
    parser.add_argument("--patterns", required=True, help="Patterns JSON file")
    args = parser.parse_args()

    signature = compute_outlet_signature(args.csv)

    if signature["total_classified_revenue"] == 0:
        print("ERROR: No classified revenue found in CSV.")
        print("Check taxonomy columns or values.")
        return

    scores = score_against_patterns(signature, args.patterns)

    if not scores:
        print("ERROR: No pattern scores computed.")
        print("Check patterns file or input data.")
        return

    best = select_best_pattern(scores)

    print("=== PATTERN PROBABILITIES ===")
    for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: {v:.3f}")

    print("\nSELECTED:", best)


if __name__ == "__main__":
    main()

