"""Plot pass@K curves for Qwen3-VL and Qwen3.5 on ARC-AGI-2."""

import matplotlib.pyplot as plt
import numpy as np

# Qwen3-VL-30B (temp=0.0, max_retries=2) on ARC-AGI-1: 400 tasks
qwen3_vl_k = [1, 2]
qwen3_vl_pass = [3.7, 4.7]  # cumulative pass rates

# Qwen3.5-35B-A3B-GPTQ-Int4 (temp=0.7, max_retries=5) on ARC-AGI-2 training: 190 tasks
qwen35_k = [1, 2, 3, 4, 5]
qwen35_pass = np.array([113, 121, 126, 129, 131]) / 190 * 100

fig, ax = plt.subplots(figsize=(6, 4))

ax.plot(qwen3_vl_k, qwen3_vl_pass, "o-", label="Qwen3-VL-30B (temp=0.0)", color="#2196F3", linewidth=2, markersize=8)
ax.plot(qwen35_k, qwen35_pass, "s-", label="Qwen3.5-35B-A3B (temp=0.7)", color="#FF5722", linewidth=2, markersize=8)

ax.set_xlabel("K (number of attempts)", fontsize=12)
ax.set_ylabel("Pass@K (%)", fontsize=12)
ax.set_title("Pass@K Curves on ARC-AGI-2", fontsize=13)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_ylim(0, 80)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("docs/proposal/passk_curve.png", dpi=200)
print("Saved passk_curve.png")
