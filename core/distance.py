import json
import math

MOMENTA = ["breakfast", "lunch", "coffee", "apero", "dinner", "after"]
BUCKETS = ["food", "hot", "soft", "beer", "wine", "spirits"]

def l1_on_keys(v1, v2, keys):
    """
    Distance L1 normalisée calculée sur une liste de clés canonique.
    Les clés manquantes sont considérées à 0.
    """
    return sum(abs(v1.get(k, 0.0) - v2.get(k, 0.0)) for k in keys) / 2


def score_against_patterns(signature, patterns_path):
    with open(patterns_path, "r", encoding="utf-8") as f:
        patterns = json.load(f)

    if not patterns:
        return {}

    scores = {}

    for pattern in patterns:
        # 1) Distance temporelle (répartition des ventes)
        dt = l1_on_keys(
            signature["revenue_by_momentum"],
            pattern["dimensions"]["revenue_by_momentum"],
            MOMENTA
        )

        # 2) Distance mix produit pondérée par l'importance du momentum
        dm = 0.0
        for m in MOMENTA:
            weight = pattern["dimensions"]["revenue_by_momentum"].get(m, 0.0)

            outlet_mix = signature["category_mix_by_momentum"].get(m, {})
            pattern_mix = pattern["dimensions"]["category_mix_by_momentum"].get(m, {})

            dm += weight * l1_on_keys(outlet_mix, pattern_mix, BUCKETS)

        # Distance globale
        d_total = 0.6 * dt + 0.4 * dm
        scores[pattern["pattern_id"]] = math.exp(-d_total)

    # Normalisation en probabilités
    total_score = sum(scores.values())
    if total_score == 0:
        return {}

    return {k: v / total_score for k, v in scores.items()}

