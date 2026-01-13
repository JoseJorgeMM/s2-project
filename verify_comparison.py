
import sys
import os
sys.path.append(os.getcwd())
from src import simulator

# Heuristic
k1_h, k2_h = 3.0, 1.5
# Optimal (from JSON - Analytical)
k1_opt, k2_opt = 4.4168, 1.9171

def get_metrics(k1, k2):
    r0 = simulator.overall_oc(1.0, 5, k1, k2, c=1.0)
    r1 = simulator.overall_oc(1.0, 5, k1, k2, c=1.5)
    return {
        "ARL0": r0["ARL"],
        "ARL1": r1["ARL"],
        "ASN0": r0["ASN"],
        "ASN1": r1["ASN"]
    }

m_h = get_metrics(k1_h, k2_h)
m_opt = get_metrics(k1_opt, k2_opt)

print(f"Heuristic: {m_h}")
print(f"Optimal: {m_opt}")
