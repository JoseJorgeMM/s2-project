"""
Surrogate modeling module.
Trains a machine learning model to approximate the performance surface of the S^2 control chart.
Maps (k1, k2, c) -> (ARL, ASN).
"""

import argparse
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import max_error, mean_absolute_error
from src import simulator

def train_surrogate(data_path: str, out_path: str, n_samples: int = 2000, seed: int = 42):
    print(f"Loading data from {data_path} to infer process parameters...")
    df = pd.read_csv(data_path)
    
    # Infer parameters from in-control data
    ic_data = df[df["state_label"] == "in-control"]
    if len(ic_data) == 0:
        raise ValueError("No in-control data found in historical dataset.")
    
    # We assume the historical data allows us to estimate sigma2. 
    # For this demo, we can just take the median of S2 or mean of S2 as a robust estimator 
    # if we assume mean=0. Or just trust the simulation parameter.
    # The simulator assumes sigma2=1.0 nominal usually, but let's measure it.
    sigma2_est = ic_data["S2"].mean()
    n = int(ic_data["n"].mode()[0])
    
    print(f"Estimated sigma2: {sigma2_est:.4f}, n: {n}")
    
    # Generate training data covering the design space
    # k1 in [1.5, 6.0], k2 in [0.5, k1 - 0.1]
    # c in [0.5, 3.0] (covering decreases and increases)
    
    rng = np.random.RandomState(seed)
    
    X = []
    y = []
    
    print(f"Generating {n_samples} training samples...")
    for _ in range(n_samples):
        k1 = rng.uniform(1.5, 6.0)
        # k2 must be strictly less than k1. 
        # We also want k2 to be reasonable, say > 0.
        k2 = rng.uniform(0.1, k1 - 0.1)
        
        # Shift coefficient c. 
        # We want to learn both in-control (c=1) and out-of-control.
        # Let's mix: 20% c=1, 80% c sampled from range.
        if rng.rand() < 0.2:
            c = 1.0
        else:
            # Sample c from [0.5, 3.0], excluding ~1.0 maybe? 
            # Continuous range is fine, the model handles it.
            c = rng.uniform(0.5, 3.0)
            
        # Calculate Ground Truth
        # Note: We use the estimated sigma2 and n from data relative to the chart design
        results = simulator.overall_oc(sigma2=sigma2_est, n=n, k1=k1, k2=k2, c=c)
        
        # Features: k1, k2, c
        # Targets: log10(ARL), log10(ASN) -> Log transform usually helps with ARL scaling
        # However, for simplicity let's predict raw first, or log. ARL blows up at c=1.
        # Let's predict log10(ARL) because it varies spanning orders of magnitude.
        
        arl = results["ARL"]
        asn = results["ASN"]
        
        if np.isinf(arl):
            arl = 1e6 # cap
            
        X.append([k1, k2, c])
        y.append([np.log10(arl), asn])
        
    X = np.array(X)
    y = np.array(y)
    
    # Train Model
    # We use Gradient Boosting as it handles non-linearities well.
    print("Training surrogate model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)
    
    model = MultiOutputRegressor(GradientBoostingRegressor(n_estimators=200, max_depth=5, random_state=seed))
    model.fit(X_train, y_train)
    
    # Validate
    score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    mae_log_arl = mean_absolute_error(y_test[:, 0], y_pred[:, 0])
    mae_asn = mean_absolute_error(y_test[:, 1], y_pred[:, 1])
    
    print(f"Model R2 Score: {score:.4f}")
    print(f"MAE log10(ARL): {mae_log_arl:.4f}")
    print(f"MAE ASN: {mae_asn:.4f}")
    
    # Save metadata along with model (n, sigma2_est) so optimizer knows context
    artifact = {
        "model": model,
        "n": n,
        "sigma2": sigma2_est,
        "feature_names": ["k1", "k2", "c"],
        "target_names": ["log10_ARL", "ASN"]
    }
    
    joblib.dump(artifact, out_path)
    print(f"Saved surrogate interface to {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to historical data")
    parser.add_argument("--out", required=True, help="Path to save model")
    parser.add_argument("--n_samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    train_surrogate(args.data, args.out, args.n_samples, args.seed)

if __name__ == "__main__":
    main()
