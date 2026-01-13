"""
Evaluation module.
Generates performance plots and tables.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import joblib
from src import simulator

def perform_evaluation(surrogate_path, results_path):
    print("Evaluating performance...")
    
    # Load optimization results if available to plot optimal points
    # For now, we'll just run a general sensitivity analysis
    
    # 1. ARL vs Shift Curve for a Standard Design vs Optimal Design
    # Standard Design (heuristic): k1=3, k2=2 (example)
    # Optimal Design: Let's assume we load it, or we just pick one.
    
    shifts = np.linspace(1.0, 3.0, 20)
    n = 5
    sigma2 = 1.0
    
    # Heuristic
    k1_h, k2_h = 3.0, 1.5 # Example
    
    arl_h = []
    for c in shifts:
        res = simulator.overall_oc(sigma2, n, k1_h, k2_h, c=c)
        arl_h.append(res["ARL"])
        
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(shifts, arl_h, label=f"Heuristic (k1={k1_h}, k2={k2_h})", marker='o')
    plt.yscale("log")
    plt.xlabel(r"Variance Shift ($c = \sigma_{new}^2 / \sigma_0^2$)")
    plt.ylabel("ARL")
    plt.title("ARL vs Shift")
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend()
    plt.savefig("outputs/arl_curve.png")
    print("Saved outputs/arl_curve.png")
    
    # 2. Heatmap of ARL1 for (k1, k2)
    # Fixed shift c=1.5
    c_target = 1.5
    k1_range = np.linspace(2.0, 5.0, 30)
    k2_range = np.linspace(0.5, 3.5, 30)
    
    Z = np.zeros((len(k2_range), len(k1_range)))
    
    for i, k2 in enumerate(k2_range):
        for j, k1 in enumerate(k1_range):
            if k2 < k1:
                res = simulator.overall_oc(sigma2, n, k1, k2, c=c_target)
                Z[i, j] = res["ARL"]
            else:
                Z[i, j] = np.nan
                
    plt.figure(figsize=(8, 6))
    plt.contourf(k1_range, k2_range, np.log10(Z), levels=20, cmap="viridis")
    plt.colorbar(label="log10(ARL)")
    plt.xlabel("k1")
    plt.ylabel("k2")
    plt.title(f"ARL Performance at c={c_target}")
    plt.plot([2, 5], [2, 5], 'r--', label="k1=k2")
    plt.legend()
    plt.savefig("outputs/heatmap.png")
    print("Saved outputs/heatmap.png")
    
    # Save a summary table
    df = pd.DataFrame({"Shift": shifts, "ARL_Heuristic": arl_h})
    df.to_csv("outputs/evaluation_table.csv", index=False)
    print("Saved outputs/evaluation_table.csv")

    # 3. Pareto Front (ARL1 vs ASN) ensuring ARL0 >= 370
    # Generate random designs
    print("Generating Pareto front analysis...")
    n_pareto = 1000
    rng = np.random.RandomState(42)
    pareto_data = []
    
    for _ in range(n_pareto):
        k1 = rng.uniform(2.0, 6.0)
        k2 = rng.uniform(0.1, k1 - 0.1)
        # Use surrogate for speed if available, else skip or use analytical (slow)
        # We'll use analytical for accuracy in this plot or surrogate if loaded
        # Let's use analytical but only 1000 points is feasible.
        
        # Check ARL0
        r0 = simulator.overall_oc(sigma2, n, k1, k2, c=1.0)
        if r0["ARL"] >= 370:
            # Check ARL1 at c=1.5
            r1 = simulator.overall_oc(sigma2, n, k1, k2, c=1.5)
            pareto_data.append({"k1": k1, "k2": k2, "ARL1": r1["ARL"], "ASN": r1["ASN"]})
            
    if pareto_data:
        pdf = pd.DataFrame(pareto_data)
        plt.figure(figsize=(8, 6))
        plt.scatter(pdf["ASN"], pdf["ARL1"], alpha=0.5, c='blue', s=20, label="Valid Designs")
        plt.xlabel(f"ASN (at c=1.5)")
        plt.ylabel(f"ARL1 (at c=1.5)")
        plt.title("Performance Trade-off (ARL0 >= 370)")
        plt.grid(True, alpha=0.3)
        plt.savefig("outputs/pareto_front.png")
        print("Saved outputs/pareto_front.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--surrogate", type=str)
    parser.add_argument("--out", type=str)
    args = parser.parse_args()
    
    perform_evaluation(args.surrogate, args.out)

if __name__ == "__main__":
    main()
