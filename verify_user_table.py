
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.getcwd())
try:
    from src import simulator
except ImportError:
    import simulator

# User provided parameters
# Format: n: (k1_prop, k2_prop, k_shew)
params = {
    4: (4.406, 2.092, 4.370),
    5: (4.184, 2.405, 4.163),
    6: (4.053, 1.953, 4.019),
    7: (3.938, 2.043, 3.910)
}

epsilon = 1e-6

# Check specific points to verify match
check_points = [
    (4, 1.0, 300.00),
    (5, 1.0, 300.00),
    (6, 1.0, 370.00), # Note user had 370 here for Proposed
    (6, 1.0, 300.00), # Shewhart target according to table? User wrote "370.00,300.00" for n=6 row
    (5, 1.5, 28.31),
    (7, 1.5, 20.50)
]

print(f"{'n':<3} | {'Type':<10} | {'c':<4} | {'Expected':<10} | {'Calculated':<10} | {'Diff':<10}")
print("-" * 60)

for n, (k1, k2, k_shew) in params.items():
    # Check Proposed c=1.0
    res_prop = simulator.overall_oc(1.0, n, k1, k2, c=1.0)
    print(f"{n:<3} | {'Proposed':<10} | {1.0:<4} | {'?':<10} | {res_prop['ARL']:<10.2f} |")
    
    # Check Shewhart c=1.0
    res_shew = simulator.overall_oc(1.0, n, k1=k_shew, k2=k_shew-epsilon, c=1.0)
    print(f"{n:<3} | {'Shewhart':<10} | {1.0:<4} | {'?':<10} | {res_shew['ARL']:<10.2f} |")
    
    # Check c=1.5
    res_prop_15 = simulator.overall_oc(1.0, n, k1, k2, c=1.5)
    print(f"{n:<3} | {'Proposed':<10} | {1.5:<4} | {'?':<10} | {res_prop_15['ARL']:<10.2f} |")

