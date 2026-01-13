"""
Data generation script: create synthetic historical datasets (in-control and shifted segments).
Command-line usage:
    python -m src.data_generation --out data/historical.csv --n_subgroups 5000

Generates:
- CSV with columns: timestamp, subgroup_id, n, mean, S2, state_label, event_flag, machine
Notes:
- Designed for experiments where nominal sigma2 = 1.0 for simplicity.
- You can adapt to real data by replacing this file.
"""

import argparse
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from tqdm import trange


def generate_historical(n_subgroups=5000, n=5, ic_fraction=0.8, sigma2=1.0, seed=42):
    """
    Generate a sequence of subgroup summaries. A fraction ic_fraction are in-control; the rest are OC segments
    produced by applying variance multipliers c sampled from a set.
    Returns pandas DataFrame.
    """
    rng = np.random.RandomState(seed)
    rows = []
    timestamp = datetime.now()
    oc_cs = [1.3, 1.5, 2.0, 0.7]  # examples of variance multipliers for OC segments
    for i in trange(n_subgroups, desc="generating subgroups"):
        subgroup_id = f"sg{i:05d}"
        # decide state
        if rng.rand() < ic_fraction:
            state_label = "in-control"
            c = 1.0
            event_flag = 0
        else:
            state_label = "out-of-control"
            c = float(rng.choice(oc_cs))
            event_flag = 1
        # generate n raw observations ~ N(0, c*sigma2) (mean irrelevant for variance)
        data = rng.normal(loc=0.0, scale=np.sqrt(c * sigma2), size=n)
        s2 = float(np.var(data, ddof=1))
        mean = float(np.mean(data))
        rows.append({
            "timestamp": (timestamp + timedelta(seconds=i)).isoformat(),
            "subgroup_id": subgroup_id,
            "n": n,
            "mean": mean,
            "S2": s2,
            "state_label": state_label,
            "event_flag": event_flag,
            "machine": f"M{rng.randint(1,5)}"
        })
    df = pd.DataFrame(rows)
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic historical subgroups for S2 chart experiments.")
    parser.add_argument("--out", type=str, default="data/historical.csv", help="Output CSV path")
    parser.add_argument("--n_subgroups", type=int, default=5000, help="Number of subgroups to generate")
    parser.add_argument("--n", type=int, default=5, help="Subgroup size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    df = generate_historical(n_subgroups=args.n_subgroups, n=args.n, seed=args.seed)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()
