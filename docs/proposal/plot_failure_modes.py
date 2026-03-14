"""Plot failure mode breakdown for Qwen3.5 on ARC-AGI-2."""

import matplotlib.pyplot as plt

# Qwen3.5-35B-A3B-GPTQ-Int4: per-task outcomes on 190 ARC-AGI-2 tasks
labels = ["Training Fail", "Wrong Output", "Solved"]
counts = [49, 10, 131]
colors = ["#EF5350", "#FFA726", "#66BB6A"]

fig, ax = plt.subplots(figsize=(5, 4))

bars = ax.bar(labels, counts, color=colors, edgecolor="white", linewidth=1.5)

for bar, count in zip(bars, counts):
    pct = count / sum(counts) * 100
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
            f"{count}\n({pct:.0f}%)", ha="center", va="bottom", fontsize=11)

ax.set_ylabel("Number of Tasks", fontsize=12)
ax.set_title("Failure Mode Breakdown (Qwen3.5, ARC-AGI-2)", fontsize=13)
ax.set_ylim(0, 160)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("docs/proposal/failure_modes.png", dpi=200)
print("Saved failure_modes.png")
