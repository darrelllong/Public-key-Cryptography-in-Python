#!/usr/bin/env python3
"""
Radar charts driven by $BENCH_OUT/results.csv (pilot run_program means).

One chart per (operation, bits) combination. Spokes are algorithms; one polygon
per language. Annotations show pilot's mean with a `±X%` CI tag when the CI
exceeds 25% — that flags cells where the sample distribution is noisy enough
(typically Julia GC pauses) that the mean should not be over-interpreted.
"""
import csv, math, os
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT  = os.environ.get("BENCH_OUT", "/tmp/bench_data")
RESULTS = os.path.join(OUT, "results.csv")
OUT_DIR = os.path.join(OUT, "charts")
os.makedirs(OUT_DIR, exist_ok=True)

ALGOS = ["rsa", "elgamal", "rabin", "paillier", "ss", "cocks"]
ALGO_LABELS = {"rsa":"RSA","elgamal":"ElGamal","rabin":"Rabin",
               "paillier":"Paillier","ss":"Schmidt-Samoa","cocks":"Cocks"}
OPS  = ["keygen", "encrypt", "decrypt"]
BITS = [512, 1024, 2048]
LANG_STYLE = {
    "python": {"color": "#3776ab", "marker": "o", "label": "Python"},
    "julia":  {"color": "#9558b2", "marker": "s", "label": "Julia"},
}

def load():
    by_cell = defaultdict(lambda: defaultdict(dict))
    with open(RESULTS) as f:
        for r in csv.DictReader(f):
            try: mean = float(r["mean_us"]); ci_p = float(r["ci_perc"])
            except: mean, ci_p = float("nan"), float("nan")
            cell = (r["operation"], int(r["bits"]))
            by_cell[cell][r["lang"]][r["algorithm"]] = (mean, ci_p)
    return by_cell

def fmt_us(v):
    if v != v or v == 0: return "—"
    if v >= 1e6: return f"{v/1e6:.1f}s"
    if v >= 1e3: return f"{v/1e3:.1f}ms"
    return f"{v:.1f}µs"

def plot_one(op, bits, by_cell):
    cell = by_cell.get((op, bits))
    if not cell: return None
    series = {lang: [cell.get(lang, {}).get(a, (float("nan"), float("nan"))) for a in ALGOS]
              for lang in LANG_STYLE.keys()}

    def to_log(xs): return [math.log10(m) if (m and m == m and m > 0) else float("nan")
                            for (m, _) in xs]
    log_series = {l: to_log(v) for l, v in series.items()}

    all_vals = [v for vs in log_series.values() for v in vs if not math.isnan(v)]
    if not all_vals: return None
    rmin = math.floor(min(all_vals))
    rmax = math.ceil(max(all_vals))
    if rmax == rmin: rmax = rmin + 1

    angles = np.linspace(0, 2 * np.pi, len(ALGOS), endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(7.5, 7.5))
    ax = plt.subplot(111, projection="polar")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([ALGO_LABELS[a] for a in ALGOS], fontsize=11)
    ax.set_rlabel_position(180 / len(ALGOS) / 2)
    rticks = list(range(rmin, rmax + 1))
    ax.set_rticks(rticks)
    ax.set_yticklabels([fmt_us(10 ** k) for k in rticks], fontsize=8, color="#666")
    ax.set_ylim(rmin, rmax)
    ax.grid(True, alpha=0.4)

    for lang, style in LANG_STYLE.items():
        log_vals = log_series[lang][:]
        plot_vals = [v if not math.isnan(v) else rmin for v in log_vals]
        plot_vals += plot_vals[:1]
        ax.plot(angles, plot_vals, color=style["color"], marker=style["marker"],
                markersize=7, linewidth=2, label=style["label"])
        ax.fill(angles, plot_vals, color=style["color"], alpha=0.13)
        for ang, v_log, (mean, ci_p) in zip(angles[:-1], log_vals, series[lang]):
            if math.isnan(v_log): continue
            tag = fmt_us(mean)
            if ci_p == ci_p and ci_p > 25: tag += f"\n±{ci_p:.0f}%"
            ax.annotate(tag, (ang, v_log),
                        xytext=(0, -15 if lang == "python" else 11), textcoords="offset points",
                        ha="center", fontsize=8, color=style["color"])

    ax.set_title(f"{op.title()} — {bits}-bit modulus\n"
                 f"(pilot run_program mean; lower is faster; log scale; ±N% = wide CI)",
                 pad=20, fontsize=12)
    ax.legend(loc="upper right", bbox_to_anchor=(1.22, 1.10), fontsize=10)

    out = os.path.join(OUT_DIR, f"{op}_{bits}.png")
    fig.tight_layout()
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out

def main():
    by_cell = load()
    n = 0
    for op in OPS:
        for bits in BITS:
            p = plot_one(op, bits, by_cell)
            if p: print(f"  wrote {p}"); n += 1
    print(f"\nTotal: {n} charts.")

if __name__ == "__main__":
    main()
