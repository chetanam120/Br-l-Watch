import numpy as np
from statsmodels.stats.power import TTestIndPower

# Initialize power calculator
analysis = TTestIndPower()
n = 21
alpha = 0.05
target_power = 0.80

# Calculate minimum detectable effect size (Cohen's d)
detectable_d = analysis.solve_power(power=target_power, nobs1=n, alpha=alpha)

# Convert Cohen's d to correlation r: r = d / sqrt(d^2 + 4)
detectable_r = detectable_d / np.sqrt(detectable_d**2 + 4)

# Calculate sample size needed to detect subtle biological signal (r = 0.1335)
target_r = 0.1335
target_d = (2 * target_r) / np.sqrt(1 - target_r**2)
required_n = analysis.solve_power(effect_size=target_d, power=target_power, alpha=alpha)

print("=========================================================")
print("             STATISTICAL POWER ANALYSIS                  ")
print("=========================================================")
print(f"Current Dataset Size:             N = {n} site-years")
print(f"Minimum Detectable Correlation:   |r| >= {detectable_r:.4f} (at 80% power, alpha=0.05)")
print(f"Observed Biological Signal:       r = {target_r:.4f}")
print(f"Required N to Detect r = {target_r:.4f}:  N ≈ {int(np.ceil(required_n))} site-years")
print("=========================================================")