
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
plt.figure(figsize=(10, 6), dpi=300)
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.4)

# Plotting on log scale for ARL
plt.plot(df["Shift"], df["ARL_Proposed"], marker='o', linewidth=2.5, label='Nueva Carta Propuesta (Journal)', color='#1f77b4')
plt.plot(df["Shift"], df["ARL_Optimized"], marker='s', linestyle='--', linewidth=2, label='Carta Optimizada (Local)', color='#ff7f0e')
plt.plot(df["Shift"], df["ARL_Shewhart"], marker='^', linestyle=':', linewidth=2, label='Shewhart Tradicional', color='#d62728')

plt.yscale('log')
plt.xlabel('Desviación de la Varianza (c = $\sigma_1^2 / \sigma_0^2$)', fontweight='bold')
plt.ylabel('ARL (Escala Logarítmica)', fontweight='bold')
plt.title(f'Comparación Profesional de ARL (n={n}, $ARL_0 \\approx {ARL0_target}$)', fontsize=16, pad=20)
plt.legend(frameon=True, shadow=True)
plt.grid(True, which="both", ls="-", alpha=0.5)

# Tight layout and save
plt.tight_layout()
plot_path = os.path.join("outputs", "arl_comparison_q1.png")
plt.savefig(plot_path)
print(f"Plot saved to: {plot_path}")

# --- Journal Style Table Generation ---
print("\n--- JOURNAL STYLE TABLE ---")
print("| c | Nueva Propuesta (Aslam) | Optimizada (Aslam) | Shewhart |")
print("|---|:---:|:---:|:---:|")
for _, row in df.iterrows():
    print(f"| {row['Shift']:.1f} | {row['ARL_Proposed']:8.2f} | {row['ARL_Optimized']:8.2f} | {row['ARL_Shewhart']:8.2f} |")

# Save table to a text file for easy copy-pasting
table_path = os.path.join("outputs", "arl_table_q1.md")
with open(table_path, "w") as f:
    f.write("# Tabla de Comparación ARL (Calidad Q1)\n\n")
    f.write(f"Parámetros: n={n}, ARL0={ARL0_target}\n\n")
    f.write("| c | Nueva Propuesta (Paper) | Optimizada (Local) | Shewhart | % Mejora |\n")
    f.write("|---|:---:|:---:|:---:|:---:|\n")
    for _, row in df.iterrows():
        mejora = ((row['ARL_Shewhart'] - row['ARL_Proposed']) / row['ARL_Shewhart']) * 100 if row['Shift'] > 1.0 else 0
        f.write(f"| {row['Shift']:.1f} | {row['ARL_Proposed']:8.2f} | {row['ARL_Optimized']:8.2f} | {row['ARL_Shewhart']:8.2f} | {mejora:6.1f}% |\n")

print(f"Markdown table saved to: {table_path}")
