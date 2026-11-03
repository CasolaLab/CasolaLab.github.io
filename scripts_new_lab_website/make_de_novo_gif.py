"""Render an animated GIF of de novo gene birth for the lab website.

Stages: ancestral noncoding DNA, transcription after an enabler mutation,
ORF gain (start codon gained, stop codon lost), translation, and retention
of the new gene alongside a sister species that keeps the noncoding state.

Usage:
    python scripts_new_lab_website/make_de_novo_gif.py [project_root]
Writes assets/img/de_novo_gene_birth.gif.
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch, Polygon
import numpy as np

MAROON = "#500000"
GENE = "#b9b0a8"
DNA = "#8a817a"
STOP = "#c0392b"
MUT = "#e08e0b"
RNA = "#2e6f9e"
TEXT = "#1d1b1a"
MUTED = "#5f5955"

FPS = 12
STAGE_FRAMES = 40
HOLD_FRAMES = 40
CAPTIONS = [
    "1  Ancestral genome. A noncoding region between two genes,\n"
    "    interrupted by stop codons",
    "2  An enabler mutation creates a promoter,\n"
    "    and the noncoding region is transcribed",
    "3  Further enabler mutations gain a start codon and remove a stop codon,\n"
    "    opening a reading frame",
    "4  The open reading frame is translated into a novel protein",
    "5  Selection retains the de novo gene, while the sister species\n"
    "    keeps the ancestral noncoding sequence",
]
N_STAGES = len(CAPTIONS)
N_FRAMES = N_STAGES * STAGE_FRAMES + HOLD_FRAMES

ORF_START, ORF_END = 36, 66
LOST_STOP = 48
KEPT_STOP = 66
# Stops outside the future ORF; only LOST_STOP lies inside it.
OTHER_STOPS = [27, 73]
TSS = 32
Y_TOP, Y_BOT = 0.0, -2.6


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)


def stage_progress(frame):
    s = min(frame // STAGE_FRAMES, N_STAGES - 1)
    p = (frame - s * STAGE_FRAMES) / (STAGE_FRAMES * 0.6)
    return s, ease(p) if frame < N_STAGES * STAGE_FRAMES else 1.0


def gene_box(ax, x0, x1, y, color, label=None, alpha=1.0, h=0.5):
    ax.add_patch(FancyBboxPatch((x0, y - h / 2), x1 - x0, h,
                                boxstyle="round,pad=0,rounding_size=0.15",
                                fc=color, ec="none", alpha=alpha, zorder=3))
    if label:
        ax.text((x0 + x1) / 2, y - 0.65, label, ha="center", va="top",
                fontsize=10, color=MUTED, alpha=alpha)


def stop_mark(ax, x, y, alpha=1.0):
    ax.plot([x, x], [y - 0.32, y + 0.32], color=STOP, lw=3, alpha=alpha,
            solid_capstyle="butt", zorder=4)
    ax.text(x, y + 0.42, "stop", ha="center", va="bottom", fontsize=8,
            color=STOP, alpha=alpha)


def mutation_star(ax, x, y, alpha):
    if alpha <= 0:
        return
    ax.plot(x, y, marker="*", ms=16, color=MUT, alpha=alpha, zorder=6,
            markeredgecolor="white", markeredgewidth=0.8)


def chromosome(ax, y, label):
    ax.plot([2, 98], [y, y], color=DNA, lw=3, zorder=2, solid_capstyle="round")
    ax.text(1, y, label, ha="right", va="center", fontsize=10.5, color=TEXT,
            fontweight="bold")
    gene_box(ax, 6, 22, y, GENE, "gene A")
    gene_box(ax, 80, 94, y, GENE, "gene B")


def draw(frame, ax):
    ax.clear()
    ax.set_xlim(-14, 100)
    ax.set_ylim(-4.4, 3.4)
    ax.axis("off")
    s, p = stage_progress(frame)

    ax.text(-13, 3.2, CAPTIONS[s], ha="left", va="top", fontsize=12.5,
            color=TEXT, linespacing=1.35)

    chromosome(ax, Y_TOP, "Species A")

    # Stop codons: the lost one fades during stage 3.
    for x in OTHER_STOPS:
        stop_mark(ax, x, Y_TOP)
    lost_alpha = 1.0 if s < 2 else (1 - p if s == 2 else 0.0)
    if lost_alpha > 0:
        stop_mark(ax, LOST_STOP, Y_TOP, lost_alpha)
    stop_mark(ax, KEPT_STOP, Y_TOP)

    # Stage 2: promoter mutation and transcript growing left to right.
    if s >= 1:
        mutation_star(ax, TSS - 1, Y_TOP, 1.0 if s > 1 else p)
        grow = 1.0 if s > 1 else p
        x_end = TSS + (70 - TSS) * grow
        xs = np.linspace(TSS, x_end, 200)
        ys = Y_TOP + 0.95 + 0.12 * np.sin(xs * 1.6)
        ax.plot(xs, ys, color=RNA, lw=2.2, zorder=4)
        ax.annotate("", xy=(TSS + 3, Y_TOP + 0.62), xytext=(TSS, Y_TOP + 0.62),
                    arrowprops=dict(arrowstyle="-|>", color=RNA, lw=1.8))
        if s == 1:
            ax.text(51, Y_TOP + 1.25, "transcript", ha="center", va="bottom",
                    fontsize=10, color=RNA, alpha=p)

    # Stage 3: start codon gained, stop codon lost, ORF opens.
    if s >= 2:
        a = 1.0 if s > 2 else p
        mutation_star(ax, ORF_START, Y_TOP - 0.55, a)
        mutation_star(ax, LOST_STOP, Y_TOP - 0.55, a)
        ax.text(ORF_START, Y_TOP - 0.95, "ATG", ha="center", va="top",
                fontsize=9, color=MAROON, fontweight="bold", alpha=a)
        orf_color = MAROON
        orf_alpha = 0.35 * a if s < 4 else 0.35 + 0.65 * p
        gene_box(ax, ORF_START, ORF_END, Y_TOP, orf_color, alpha=orf_alpha,
                 h=0.42)
        if s == 2:
            ax.text((ORF_START + ORF_END) / 2, Y_TOP - 0.95, "open reading frame",
                    ha="center", va="top", fontsize=10, color=MAROON, alpha=a)

    # Stage 4: ribosome walks the transcript, protein beads accumulate.
    if s >= 3:
        n_beads = 14
        shown = n_beads if s > 3 else int(round(n_beads * p))
        bx = np.linspace(ORF_START + 1, ORF_END - 1, n_beads)[:shown]
        by = Y_TOP + 1.85 + 0.18 * np.sin(np.arange(shown) * 1.1)
        ax.plot(bx, by, color=MAROON, lw=1.2, zorder=4, alpha=0.6)
        ax.scatter(bx, by, s=70, color=MAROON, zorder=5, edgecolors="white",
                   linewidths=0.8)
        if s == 3 and shown:
            ax.add_patch(Polygon([[bx[-1] - 1.4, Y_TOP + 1.0],
                                  [bx[-1] + 1.4, Y_TOP + 1.0],
                                  [bx[-1] + 1.0, Y_TOP + 1.45],
                                  [bx[-1] - 1.0, Y_TOP + 1.45]],
                                 closed=True, fc=GENE, ec="none", zorder=5))
        ax.text(ORF_END + 2.5, Y_TOP + 1.85, "novel protein", ha="left",
                va="center", fontsize=10, color=MAROON,
                alpha=1.0 if s > 3 else p)

    # Stage 5: new gene labeled, sister species shown without enablers.
    if s >= 4:
        ax.text((ORF_START + ORF_END) / 2, Y_TOP - 0.95, "de novo gene",
                ha="center", va="top", fontsize=11, color=MAROON,
                fontweight="bold", alpha=p)
        chromosome(ax, Y_BOT, "Species B")
        for x in OTHER_STOPS + [LOST_STOP, KEPT_STOP]:
            stop_mark(ax, x, Y_BOT, alpha=p)
        ax.text(51, Y_BOT - 0.95, "orthologous region, still noncoding",
                ha="center", va="top", fontsize=10, color=MUTED, alpha=p)
        for x in (ORF_START, ORF_END):
            ax.plot([x, x], [Y_BOT + 0.3, Y_TOP - 1.4], color=DNA, lw=0.8,
                    ls=":", alpha=p, zorder=1)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    assets = os.path.join(root, "assets")
    if not os.path.isdir(assets):
        sys.exit(f"error: {assets} not found; run from the project root")
    out_dir = os.path.join(assets, "img")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "de_novo_gene_birth.gif")

    fig = plt.figure(figsize=(9, 4), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    anim = FuncAnimation(fig, draw, frames=N_FRAMES, fargs=(ax,))
    print(f"rendering {N_FRAMES} frames at {FPS} fps", file=sys.stderr)
    anim.save(out, writer=PillowWriter(fps=FPS))
    print(out)


if __name__ == "__main__":
    main()
