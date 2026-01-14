
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure src is in python path
sys.path.append(os.getcwd())
try:
    from src import simulator
except ImportError:
    import simulator

# --- Parameters Configuration ---
n = 5
sigma2 = 1.0
ARL0_target = 370

# 1. Proposed (Manuscript Table 3/5)
k1_paper, k2_paper = 4.37021, 1.92006

# 2. Optimized (Project Code)
k1_opt, k2_opt = 4.4168, 1.9171

# 3. Shewhart (Standard)
k_shew = 4.3306
epsilon = 1e-8

shifts = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.5, 3.0, 4.0]

results = []

for c in shifts:
    # Proposed (Paper)
    res_paper = simulator.overall_oc(sigma2, n, k1_paper, k2_paper, c=c)
    
    # Optimized (Code)
    res_opt = simulator.overall_oc(sigma2, n, k1_opt, k2_opt, c=c)
    
    # Shewhart
    res_shew = simulator.overall_oc(sigma2, n, k_shew, k_shew - epsilon, c=c)
    
    results.append({
        "Shift": c,
        "ARL_Proposed": res_paper["ARL"],
        "ARL_Optimized": res_opt["ARL"],
        "ARL_Shewhart": res_shew["ARL"]
    })

df = pd.DataFrame(results)

# --- Visual Comparison (Plot) ---
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

plt.figure(figsize=(10, 6), dpi=300)
sns.set_style("whitegrid", {'font.family':'serif', 'font.serif':'Times New Roman'})
sns.set_context("paper", font_scale=1.5)

# Plotting on log scale for ARL
plt.plot(df["Shift"], df["ARL_Proposed"], marker='o', markersize=8, linewidth=2.5, label='Proposed Repetitive $S^2$ (Paper)', color='#005EB8') # Royal Blue
plt.plot(df["Shift"], df["ARL_Optimized"], marker='s', markersize=7, linestyle='--', linewidth=2, label='Optimized Repetitive $S^2$ (Local)', color='#E87722') # Dark Orange
plt.plot(df["Shift"], df["ARL_Shewhart"], marker='^', markersize=8, linestyle=':', linewidth=2, label='Traditional Shewhart $S^2$', color='#C60C30') # Crimson

plt.yscale('log')
plt.xlabel('Process Variance Shift Ratio ($c = \sigma_1^2 / \sigma_0^2$)', fontsize=14, labelpad=10)
plt.ylabel('Average Run Length (ARL)', fontsize=14, labelpad=10)
plt.title(f'Performance Comparison of Reproductive $S^2$ Chart Designs\n($n={n}$, $ARL_0 \\approx {ARL0_target}$)', fontsize=16, pad=20)
plt.legend(frameon=True, shadow=False, loc='upper right', fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.3)

# Add horizontal line for ARL0
plt.axhline(y=ARL0_target, color='gray', linestyle='--', alpha=0.5)
plt.text(1.05, ARL0_target * 1.1, f'$ARL_0 = {ARL0_target}$', color='gray', fontsize=10)

# Tight layout and save
plt.tight_layout()
plot_path = os.path.join("outputs", "arl_comparison_q1.png")
plt.savefig(plot_path, bbox_inches='tight')
print(f"Plot saved to: {plot_path}")

# --- Journal Style Table Generation ---
print("\n--- JOURNAL QUALITY COMPARISON TABLE ---")
print("| Shift (c) | Proposed (Aslam) | Optimized (Local) | Shewhart | % Improvement |")
print("|:---:|:---:|:---:|:---:|:---:|")
for _, row in df.iterrows():
    improvement = ((row['ARL_Shewhart'] - row['ARL_Proposed']) / row['ARL_Shewhart']) * 100 if row['Shift'] > 1.0 else 0
    print(f"| {row['Shift']:.1f} | {row['ARL_Proposed']:8.2f} | {row['ARL_Optimized']:8.2f} | {row['ARL_Shewhart']:8.2f} | {improvement:6.1f}% |")

# Save table to a markdown file for the manuscript
table_path = os.path.join("outputs", "arl_table_q1.md")
with open(table_path, "w") as f:
    f.write("# ARL Performance Comparison (Journal Standard)\n\n")
    f.write(f"Parameters: Subgroup size $n={n}$, Target In-control $ARL_0={ARL0_target}$\n\n")
    f.write("| Variance Shift ($c$) | Proposed (Paper) | Optimized (Local) | Shewhart | % Improvement |\n")
    f.write("|:---:|:---:|:---:|:---:|:---:|\n")
    for _, row in df.iterrows():
        improvement = ((row['ARL_Shewhart'] - row['ARL_Proposed']) / row['ARL_Shewhart']) * 100 if row['Shift'] > 1.0 else 0
        mark = "**" if row['Shift'] == 1.5 or row['Shift'] == 2.0 else ""
        f.write(f"| {mark}{row['Shift']:.1f}{mark} | {row['ARL_Proposed']:8.2f} | {row['ARL_Optimized']:8.2f} | {row['ARL_Shewhart']:8.2f} | {improvement:6.1f}% |\n")

print(f"Markdown table saved to: {table_path}")
