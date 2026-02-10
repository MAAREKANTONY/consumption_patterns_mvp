import json, math

def l1(v1, v2):
    return sum(abs(v1[k]-v2[k]) for k in v1)/2

def score_against_patterns(sig, patterns_path):
    with open(patterns_path) as f:
        pats = json.load(f)

    scores = {}
    for p in pats:
        dt = l1(sig["revenue_by_momentum"], p["dimensions"]["revenue_by_momentum"])
        dm = 0.0
        for m, w in p["dimensions"]["revenue_by_momentum"].items():
            # Mix outlet (sécurisé)
            outlet_mix = sig["category_mix_by_momentum"].get(m, {})

            # Mix pattern (référence)
            pattern_mix = p["dimensions"]["category_mix_by_momentum"][m]

            # Forcer toutes les clés (food, hot, soft, beer, wine, spirits)
            outlet_mix_complete = {
                k: outlet_mix.get(k, 0.0) for k in pattern_mix.keys()
            }

            dm += w * l1(outlet_mix_complete, pattern_mix)

        d = 0.6*dt + 0.4*dm
        scores[p["pattern_id"]] = math.exp(-d)

    s = sum(scores.values()) or 1
    return {k:v/s for k,v in scores.items()}
