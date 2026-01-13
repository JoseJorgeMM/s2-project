"""
Optimizer module.
Uses Optuna to find optimal (k1, k2) parameters.
Supports 'analytical' (exact) and 'surrogate' (ML-based) evaluation.
"""

import argparse
import optuna
import numpy as np
import joblib
import json
from src import simulator

def objective(trial, mode, surrogate_artifact, target_arl0, shift, n, sigma2):
    # Suggest parameters
    k1 = trial.suggest_float("k1", 1.5, 6.0)
    # k2 must be < k1. We can enforce this by sampling k2 from [0.1, k1).
    k2 = trial.suggest_float("k2", 0.1, k1 - 0.01)
    
    # Calculate ARL0 (c=1.0) and ARL1 (c=shift)
    
    if mode == "analytical":
        # Direct calculation
        res0 = simulator.overall_oc(sigma2, n, k1, k2, c=1.0)
        res1 = simulator.overall_oc(sigma2, n, k1, k2, c=shift)
        
        arl0 = res0["ARL"]
        arl1 = res1["ARL"]
        asn1 = res1["ASN"]
        
    elif mode == "surrogate":
        model = surrogate_artifact["model"]
        # Predict for c=1.0
        # Input shape: [[k1, k2, c]]
        p0 = model.predict([[k1, k2, 1.0]])[0] # [log_arl, asn]
        p1 = model.predict([[k1, k2, shift]])[0]
        
        arl0 = 10**p0[0]
        arl1 = 10**p1[0]
        asn1 = p1[1]
        
    else:
        raise ValueError(f"Unknown mode {mode}")
        
    # Constraints
    # We want ARL0 >= target_arl0
    # Soft or Hard constraint? Optuna supports pruning or penalty.
    # We'll return a penalty if constraint violated.
    
    if arl0 < target_arl0:
        # Penalize. 
        # A simple penalty is a large value + distance.
        return 1e4 + (target_arl0 - arl0)
    
    # Objective: Minimize ARL1 (detect shift fast)
    # Could also mix with ASN: minimize ARL1 + lambda * ASN
    return arl1

def run_optimization(mode, surrogate_path, out_path, n_trials=100, target_arl0=370, shift=1.5):
    print(f"Starting optimization in mode: {mode}")
    
    surrogate_artifact = None
    if mode == "surrogate":
        surrogate_artifact = joblib.load(surrogate_path)
        n = surrogate_artifact["n"]
        sigma2 = surrogate_artifact["sigma2"]
        print(f"Loaded surrogate context: n={n}, sigma2={sigma2}")
    else:
        # Default defaults if no surrogate context
        # Ideally we read data config, but for now we assume defaults or use a config
        n = 5
        sigma2 = 1.0
    
    study = optuna.create_study(direction="minimize")
    study.optimize(
        lambda t: objective(t, mode, surrogate_artifact, target_arl0, shift, n, sigma2),
        n_trials=n_trials
    )
    
    best_params = study.best_params
    best_value = study.best_value
    
    print("Best params:", best_params)
    print("Best ARL1:", best_value)
    
    # Re-evaluate best params to get full stats
    k1 = best_params["k1"]
    k2 = best_params["k2"]
    
    # Always verify with analytical at the end for reporting
    final_verify = simulator.overall_oc(sigma2, n, k1, k2, c=shift)
    final_arl0 = simulator.overall_oc(sigma2, n, k1, k2, c=1.0)["ARL"]
    
    results = {
        "mode": mode,
        "best_k1": k1,
        "best_k2": k2,
        "achieved_ARL1": final_verify["ARL"],
        "achieved_ARL0": final_arl0,
        "achieved_ASN": final_verify["ASN"],
        "trials": n_trials
    }
    
    # Append to file if exists (for comparison mode) or overwrite? 
    # For now, just write this result.
    # Actually, the user wants 'compare' mode in run_demo.sh.
    # Let's support running both and saving a list if needed.
    # But for a single run, I'll just save this dict.
    
    # If mode is 'compare', we run both and save both.
    
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["analytical", "surrogate", "compare"], required=True)
    parser.add_argument("--surrogate", type=str, help="Path to surrogate model")
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--trials", type=int, default=50)
    args = parser.parse_args()
    
    final_output = {}
    
    if args.mode == "compare":
        # Run both
        res_analytical = run_optimization("analytical", args.surrogate, args.out, n_trials=args.trials)
        res_surrogate = run_optimization("surrogate", args.surrogate, args.out, n_trials=args.trials)
        final_output["analytical"] = res_analytical
        final_output["surrogate"] = res_surrogate
    else:
        res = run_optimization(args.mode, args.surrogate, args.out, n_trials=args.trials)
        final_output[args.mode] = res
        
    with open(args.out, "w") as f:
        json.dump(final_output, f, indent=2)
    print(f"Results saved to {args.out}")

if __name__ == "__main__":
    main()
