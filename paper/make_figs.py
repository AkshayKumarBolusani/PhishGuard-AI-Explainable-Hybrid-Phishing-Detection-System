"""Generate paper figures: architecture flowchart + results chart."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1a1a1a"
ACCENT = "#0b5394"
LIGHT = "#eaf1f8"
GREEN = "#1a7a3a"

# ── Fig 1: architecture ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

def box(x, y, w, h, text, fontsize=7.5, fill=LIGHT, edge=ACCENT, tc=INK, style="round,pad=0.08"):
    p = FancyBboxPatch((x, y), w, h, boxstyle=style, facecolor=fill,
                       edgecolor=edge, linewidth=1.2)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=tc, weight="bold", linespacing=1.3)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.1, color=INK))

# input + validation
box(3.6, 8.6, 2.8, 0.9, "Email Input\n(subject, sender, body)", fontsize=7.5)
box(3.6, 7.3, 2.8, 0.9, "Pydantic Validation", fontsize=7.5)
arrow(5.0, 8.6, 5.0, 8.2)

# three parallel layers
box(0.4, 5.5, 2.9, 1.3, "Rule Engine\n29 regex rules · ~5 ms", fontsize=7)
box(3.55, 5.5, 2.9, 1.3, "TF-IDF + ML\nLR + RF ensemble · ~50 ms", fontsize=7)
box(6.7, 5.5, 2.9, 1.3, "DistilBERT\nconfigurable · not evaluated", fontsize=7,
    fill="#f4f4f4", edge="#999999", tc="#555555")
for x in (1.85, 5.0, 8.15):
    arrow(x, 7.3, x, 6.8)

# ensemble
box(3.55, 3.9, 2.9, 1.1, "Weighted Ensemble\n0.35 rules + 0.65 ML", fontsize=7.5, fill="#fff4e0", edge="#b7791f")
for x in (1.85, 5.0, 8.15):
    arrow(x, 5.5, 4.2 if x < 5 else (5.8 if x > 5 else 5.0), 5.0)

# analysis + explainer
box(3.55, 2.3, 2.9, 1.1, "URL + Sender + NLP\nAnalysis", fontsize=7.5)
arrow(5.0, 3.9, 5.0, 3.4)
box(3.55, 0.7, 2.9, 1.1, "LLM Explainer\nAnalyst security report", fontsize=7.5, fill="#e8f5e9", edge=GREEN)
arrow(5.0, 2.3, 5.0, 1.8)

# outputs
box(0.4, 0.7, 2.9, 1.1, "MongoDB\nScan history", fontsize=7.5)
box(6.7, 0.7, 2.9, 1.1, "React Dashboard\nTriage UI", fontsize=7.5)
arrow(3.55, 1.25, 3.3, 1.25)
arrow(6.45, 1.25, 6.7, 1.25)

fig.tight_layout(pad=0.4)
fig.savefig("/home/hatch/workspace/phishguard-benchmark/paper/fig_architecture.png", dpi=300)
plt.close(fig)

# ── Fig 2: results chart ─────────────────────────────────────────
corpora = ["TREC_07", "CEAS_08", "Nazario_5", "Nigerian_5", "SpamAssassin"]
f1 = {
    "PILFER-style RF": [0.869, 0.782, 0.778, 0.740, 0.730],
    "TF-IDF + LR":     [0.994, 0.996, 0.991, 0.993, 0.973],
    "TF-IDF + SVM":    [0.996, 0.998, 0.996, 0.996, 0.984],
    "PhishGuard hybrid": [0.986, 0.980, 0.933, 0.980, 0.908],
}
colors = ["#999999", "#5b9bd5", "#0b5394", "#e67e22"]

fig, ax = plt.subplots(figsize=(7.5, 3.4))
x = range(len(corpora))
w = 0.19
for i, (name, vals) in enumerate(f1.items()):
    offs = [(xi - 1.5 * w + i * w) for xi in x]
    bars = ax.bar(offs, vals, width=w, label=name, color=colors[i], edgecolor="white")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.008, f"{v:.3f}",
                ha="center", va="bottom", fontsize=6, color=INK)
ax.set_xticks(list(x))
ax.set_xticklabels(corpora, fontsize=7.5)
ax.set_ylabel("F1 (phishing class)", fontsize=8)
ax.set_ylim(0.6, 1.06)
ax.legend(fontsize=7, loc="lower left", frameon=True)
ax.grid(axis="y", linestyle=":", alpha=0.5)
ax.set_title("F1 score per model and corpus (pooled 5-fold out-of-fold predictions)",
             fontsize=8.5, weight="bold", pad=8)
fig.tight_layout(pad=0.5)
fig.savefig("/home/hatch/workspace/phishguard-benchmark/paper/fig_results.png", dpi=300)
plt.close(fig)
print("figures written")
