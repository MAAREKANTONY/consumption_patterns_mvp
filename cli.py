import argparse
from core.signature import compute_outlet_signature
from core.distance import score_against_patterns
from core.decision import select_best_pattern

def main():
    parser = argparse.ArgumentParser(description="Compute consumption pattern for an outlet")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--patterns", required=True)
    args = parser.parse_args()

    sig = compute_outlet_signature(args.csv)
    scores = score_against_patterns(sig, args.patterns)
    best = select_best_pattern(scores)

    print("=== PATTERN PROBABILITIES ===")
    for k, v in scores.items():
        print(f"{k}: {v:.3f}")
    print("\nSELECTED:", best)

if __name__ == "__main__":
    main()
