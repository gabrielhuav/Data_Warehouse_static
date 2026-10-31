#!/usr/bin/env python3
"""Figure for the journal version: what each detector sees, spikes against drops.

(a) Recall on injected spikes and on injected drops at the equal operating point,
    under the published injection model (3 %, 70 % spikes, strong).
(b) Precision = recall at the equal operating point as the share of spikes among
    the injected anomalies varies.

Both panels read sensibilidad_anomalias.csv (20 seeds per setting).

    py -3.12 evaluacion-ml/figura_anomalias.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

AQUI = Path(__file__).resolve().parent
# Fixed order: colour, line style and marker follow the method, never its rank.
METODOS = [
    ("A_g (deployed ranking)", "$A_g$ (deployed)", "#2a78d6", "-", "o"),
    ("Isolation Forest", "Isolation Forest", "#eb6834", "--", "s"),
    ("LOF", "LOF", "#1baf7a", ":", "^"),
    ("log-A_g (proposed)", "log-$A_g$", "#6250d6", "-.", "D"),
]
TINTA, TINTA_2, EJE, REJILLA = "#0b0b0b", "#52514e", "#c3c2b7", "#e1e0d9"
PUBLICADO = "70 % spikes (published)"
COMPOSICION = ["10 % spikes", "30 % spikes", "50 % spikes", PUBLICADO, "90 % spikes"]


def ejes(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(EJE)
    ax.tick_params(colors=TINTA_2, labelsize=8, length=3)
    ax.grid(True, axis="y", color=REJILLA, linewidth=0.6)
    ax.set_axisbelow(True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sensibilidad", type=Path, default=AQUI / "sensibilidad_anomalias.csv")
    parser.add_argument("--salida", type=Path, default=AQUI / "figura_anomalias.png")
    args = parser.parse_args()

    sens = pd.read_csv(args.sensibilidad)
    plt.rcParams.update({"font.family": "Times New Roman", "font.size": 9, "hatch.linewidth": 0.8})
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"wspace": 0.30, "width_ratios": [1, 1.1]})

    pub = sens[(sens.factor == "composition") & (sens.setting == PUBLICADO)]
    x = np.arange(len(METODOS))
    ancho = 0.36
    for i, (clave, _, color, _, _) in enumerate(METODOS):
        m = pub[pub.method == clave]
        for j, (col, desplaz) in enumerate((("recall_spikes", -ancho / 2), ("recall_drops", ancho / 2))):
            media, sd = m[col].mean(), m[col].std()
            a.bar(x[i] + desplaz, media, width=ancho - 0.03, color=color if j == 0 else "white",
                  edgecolor=color, linewidth=1.2, hatch=None if j == 0 else "////",
                  yerr=sd, error_kw={"elinewidth": 0.7, "capsize": 2, "ecolor": TINTA_2})
            a.annotate(f"{media:.2f}", (x[i] + desplaz, media + sd), xytext=(0, 2), textcoords="offset points",
                       ha="center", va="bottom", fontsize=6.5, color=TINTA_2)
    a.set_xticks(x, ["$A_g$\n(deployed)", "Isolation\nForest", "LOF", "log-$A_g$\n(proposed)"], fontsize=7.5)
    a.set(ylim=(0, 1.12), ylabel="Recall at equal alerts")
    a.set_title("(a) Spikes (solid) and drops (hatched)", fontsize=9, color=TINTA, loc="left")
    ejes(a)

    xs = [10, 30, 50, 70, 90]
    comp = sens[sens.factor == "composition"]
    for clave, nombre, color, estilo, marca in METODOS:
        m = comp[comp.method == clave].groupby("setting")["P=R=F1"].agg(["mean", "std"])
        y = np.array([m.loc[s, "mean"] for s in COMPOSICION])
        e = np.array([m.loc[s, "std"] for s in COMPOSICION])
        b.fill_between(xs, y - e, y + e, color=color, alpha=0.10, linewidth=0)
        b.plot(xs, y, color=color, linestyle=estilo, linewidth=1.6, marker=marca, markersize=5,
               markeredgecolor="white", markeredgewidth=1.0, label=nombre)
    b.axvline(70, color=EJE, linewidth=0.8, linestyle=(0, (2, 2)), zorder=0)
    b.text(71, 0.04, "published\nmodel", fontsize=7, color=TINTA_2, va="bottom")
    b.set_xticks(xs, [f"{v} %" for v in xs])
    b.set(ylim=(0, 1.0), xlim=(5, 95), xlabel="Share of spikes among injected anomalies",
          ylabel="Precision = recall at equal alerts")
    b.set_title("(b) As drops become more frequent", fontsize=9, color=TINTA, loc="left")
    ejes(b)
    fig.legend(*b.get_legend_handles_labels(), frameon=False, fontsize=8, loc="upper center",
               bbox_to_anchor=(0.5, 0.0), ncol=4, labelcolor=TINTA_2, handlelength=2.6)

    fig.savefig(args.salida, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Figure written to {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
