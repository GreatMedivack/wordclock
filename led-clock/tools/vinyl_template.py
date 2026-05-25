#!/usr/bin/env python3
"""Generate an SVG template for vinyl cutting the letter face.

Produces a black rectangle with letter-shaped cutouts — ready for a
Cricut/Silhouette plotter or laser cutter. Light passes only through
the letter openings.

Usage:
    python vinyl_template.py                    — 25mm cells (wall clock)
    python vinyl_template.py --cell 12          — 12mm cells (desktop)
    python vinyl_template.py --cell 35 -o big   — 35mm cells, custom output
"""

import argparse
import os

COLS = 15
ROWS = 11

GRID = [
    "ONEXTWODTHREEIR",
    "FOURFIVESIXHATN",
    "SEVENREIGHTBULK",
    "NINETENVCELEVEN",
    "AMTWELVEXPMHOUR",
    "ZEROXONEDTWOBIA",
    "THREEGFOURFIVER",
    "ZEROXONETWOIAHD",
    "THREEFOURFIVESK",
    "SIXSEVENEIGHTLM",
    "NINEWORDCLOCKZX",
]


def generate(cell_mm=25, output="vinyl_face"):
    grid_w = COLS * cell_mm
    grid_h = ROWS * cell_mm
    margin = 10
    svg_w = grid_w + 2 * margin
    svg_h = grid_h + 2 * margin

    font_size = cell_mm * 0.55
    # Slightly smaller letter height for clean cutout proportions

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w}mm" height="{svg_h}mm" viewBox="0 0 {svg_w} {svg_h}">',
        "  <defs>",
        '    <mask id="letters">',
        f'      <rect x="{margin}" y="{margin}" width="{grid_w}" height="{grid_h}" fill="white"/>',
    ]

    for r in range(ROWS):
        for c in range(COLS):
            cx = margin + c * cell_mm + cell_mm / 2
            cy = margin + r * cell_mm + cell_mm / 2
            lines.append(
                f'      <text x="{cx}" y="{cy}" text-anchor="middle" '
                f'dominant-baseline="central" font-family="Arial Black, Arial, sans-serif" '
                f'font-weight="900" font-size="{font_size}" fill="black">'
                f"{GRID[r][c]}</text>"
            )

    lines += [
        "    </mask>",
        "  </defs>",
        f'  <rect x="{margin}" y="{margin}" width="{grid_w}" height="{grid_h}" '
        f'fill="black" mask="url(#letters)"/>',
        "</svg>",
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(script_dir, f"{output}_{cell_mm}mm.svg")
    with open(fname, "w") as f:
        f.write("\n".join(lines))

    print(f"Saved: {fname}")
    print(f"Grid: {grid_w}×{grid_h}mm ({COLS}×{ROWS} cells @ {cell_mm}mm)")
    print(f"Total: {svg_w}×{svg_h}mm (with {margin}mm margin)")


def main():
    parser = argparse.ArgumentParser(description="Vinyl/laser face template generator")
    parser.add_argument("--cell", type=int, default=25, help="Cell size in mm (default: 25)")
    parser.add_argument("-o", "--output", default="vinyl_face", help="Output file prefix")
    args = parser.parse_args()
    generate(cell_mm=args.cell, output=args.output)


if __name__ == "__main__":
    main()
