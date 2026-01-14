
import sys
import os
import pandas as pd
import numpy as np

# Ensure src is in python path
sys.path.append(os.getcwd())
try:
    from src import simulator
except ImportError:
    import simulator

# Parameters from Paper Table 3 for n=5, ARL0=370
n = 5
sigma2 = 1.0 # Standard assumption
k1_paper = 4.37021
k2_paper = 1.92006

# Shifts c to test (from Table 3)
shifts = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 3.0, 4.0]

# Expected values from Table 3 (n=5) for comparison
paper_values = {
    1.0: {"ARL": 370.00, "ASN": 5.26},
    1.1: {"ARL": 187.55, "ASN": 5.36},
    1.2: {"ARL": 106.51, "ASN": 5.48},
    1.3: {"ARL": 66.01,  "ASN": 5.62},
    1.4: {"ARL": 43.81,  "ASN": 5.75},
    1.5: {"ARL": 30.73,  "ASN": 5.89},
    1.6: {"ARL": 22.55,  "ASN": 6.03},
    1.7: {"ARL": 17.17,  "ASN": 6.16},
    1.8: {"ARL": 13.50,  "ASN": 6.29},
    1.9: {"ARL": 10.90,  "ASN": 6.41},
    2.0: {"ARL": 9.01,   "ASN": 6.52},
    3.0: {"ARL": 2.91,   "ASN": 7.04},
    4.0: {"ARL": 1.84,   "ASN": 6.91}
}

print(f"{'c':<5} | {'ARL (Calc)':<12} | {'ARL (Paper)':<12} | {'Diff':<10} | {'ASN (Calc)':<12} | {'ASN (Paper)':<12}")
print("-" * 85)

all_passed = True
tolerance = 0.5 # Allow small floating point diffs

for c in shifts:
    res = simulator.overall_oc(sigma2, n, k1_paper, k2_paper, c=c)
    arl_calc = res["ARL"]
    asn_calc = res["ASN"]
    
    arl_paper = paper_values[c]["ARL"]
    asn_paper = paper_values[c]["ASN"]
    
    diff_arl = abs(arl_calc - arl_paper)
    
    match_mark = "" if diff_arl < tolerance else " (!)"
    if diff_arl >= tolerance:
        all_passed = False
        
    print(f"{c:<5} | {arl_calc:<12.2f} | {arl_paper:<12.2f} | {diff_arl:<10.2f}{match_mark} | {asn_calc:<12.2f} | {asn_paper:<12.2f}")

if all_passed:
    print("\nSUCCESS: Calculated values match Paper Table 3 closely!")
else:
    print("\nWARNING: Some values deviate from the paper's results.")
