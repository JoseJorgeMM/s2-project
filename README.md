# ML-adaptive repetitive-sampling S² control chart

This project implements and evaluates a machine-learning framework that adaptively tunes the control-limit multipliers (k1, k2)
for the repetitive-sampling S² control chart from the original paper. It includes:

- simulator: analytic and simulation-based evaluation of the repetitive-sampling S² chart
- data generator: create realistic historical datasets (in-control and shifted)
- surrogate: train an ML surrogate to predict ARL0/ARL1/ASN as a function of (k1,k2,context)
- optimizer: use Optuna to find optimal (k1,k2) using either direct simulation or surrogate-assisted optimization
- evaluation: compare original theoretical design, direct optimizer, and surrogate-assisted optimizer
- manuscript: draft ready for submission (manuscript.md and manuscript.tex)

## Quick start

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the demo driver (will generate simulated data, train surrogate, run optimizers and produce plots):
```bash
bash run_demo.sh
```

3. Inspect outputs in the `outputs/` folder (CSV, models, plots). See code comments for function-level documentation.

## Project structure

- `src/` : Python modules
- `data/` : example CSV schema and generated datasets
- `outputs/` : results (created by running demo)
- `manuscript.md` / `manuscript.tex` : ready-to-edit submission draft

## Notes

- The code is well-commented; start with `src/simulator.py` and `src/data_generation.py`.
- The default demo uses simulated data only; replace `data/historical.csv` with real data if available.
