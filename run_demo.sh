#!/usr/bin/env bash
set -e
mkdir -p outputs models data
python -m src.data_generation --out data/historical.csv --n_subgroups 5000
python -m src.surrogate --data data/historical.csv --out models/surrogate.joblib --n_samples 2000
python -m src.optimizer --mode compare --surrogate models/surrogate.joblib --out outputs/optimization_results.json
python -m src.evaluate --surrogate models/surrogate.joblib --out outputs/evaluation_results.json
echo "Demo completed. See outputs/ and models/ directories."
