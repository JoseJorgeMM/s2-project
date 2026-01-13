
import sys
import os
import pandas as pd
import numpy as np
sys.path.append(os.getcwd())
try:
    from src import simulator
except ImportError:
    import simulator

# Parameters
# Parameters
k1_h, k2_h = 3.0, 1.5
k1_opt, k2_opt = 4.4168, 1.9171
k1_aslam, k2_aslam = 4.3899, 1.5964 # Optimized for ARL0=370, min ARL1@c=1.5
k_shew = 4.3306
epsilon = 1e-6

n = 5
sigma2 = 1.0
shifts = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2.0, 2.5, 3.0]

results = []

print(f"{'Shift':<10} | {'Heuristic':<12} | {'Optimized':<12} | {'Aslam(Opt)':<12} | {'Shewhart':<12}")
print("-" * 70)

for c in shifts:
    # Heuristic
    res_h = simulator.overall_oc(sigma2, n, k1_h, k2_h, c=c)
    arl_h = res_h["ARL"]
    
    # Optimized
    res_opt = simulator.overall_oc(sigma2, n, k1_opt, k2_opt, c=c)
    arl_opt = res_opt["ARL"]

    # Aslam (Traditional Optimization)
    res_aslam = simulator.overall_oc(sigma2, n, k1_aslam, k2_aslam, c=c)
    arl_aslam = res_aslam["ARL"]

    # Shewhart
    # k1=k_shew, k2=k_shew - epsilon
    res_shew = simulator.overall_oc(sigma2, n, k1=k_shew, k2=k_shew - epsilon, c=c)
    arl_shew = res_shew["ARL"]
    
    results.append({
        "Shift": c,
        "ARL_Heuristic": arl_h,
        "ARL_Optimized": arl_opt,
        "ARL_Aslam": arl_aslam,
        "ARL_Shewhart": arl_shew
    })
    print(f"{c:<10} | {arl_h:<12.2f} | {arl_opt:<12.2f} | {arl_aslam:<12.2f} | {arl_shew:<12.2f}")

df = pd.DataFrame(results)
df.to_csv("outputs/arl_comparison_full.csv", index=False)
print("\nResults saved to outputs/arl_comparison_full.csv")
