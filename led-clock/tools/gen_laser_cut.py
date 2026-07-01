#!/usr/bin/env python3
"""Generate laser-cutting layout for the clock front mask.

Outputs a PDF (deliverable — the shop accepts .PDF, not .SVG) at true 1:1 in
millimetres, plus an SVG for on-screen preview. Red hairline strokes only, no
fills, no background. All glyphs are emitted as closed vector outlines (curves),
never as text. Convention: red (255,0,0) = cut. Most laser shops accept this.
"""

import cairo
import ctypes
import math
import os
import shutil

# Register the project font with fontconfig so cairo finds it by family name
_FONT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          os.pardir, "arduino", "wordclock_ru", "BlackOpsOne.ttf")
ctypes.CDLL("libfontconfig.so.1").FcConfigAppFontAddFile(None, _FONT_FILE.encode())

GRID = [
    "ЪДВАДЦАТЬНПЯТЬИЧ",
    "РЦДЕСЯТЬГМИНУТЛЗ",
    "ЧЕТВЕРТЬПОЛОВИНА",
    "ЭБЕЗХДВАДЦАТИПСК",
    "ПЯТИУЧЕТВЕРТИАЯБ",
    "ДЕСЯТИПЕРВОГОТРИ",
    "ВТОРОГОПЯТОГОЧАС",
    "ТРЕТЬЕГОШЕСТОГОВ",
    "ЧЕТВЕРТОГОЧЕТЫРЕ",
    "СЕДЬМОГОВОСЬМОГО",
    "ДЕВЯТОГОДЕСЯТОГО",
    "ОДИННАДЦАТОГОДВА",
    "ДВЕНАДЦАТОГОПЯТЬ",
    "ДВЕНАДЦАТЬДЕСЯТЬ",
    "ОДИННАДЦАТЬШЕСТЬ",
    "СЕМЬВОСЕМЬДЕВЯТЬ",
]

COLS = 16
ROWS = 16

# Panel is the physical 30×30cm board
PANEL_W = 300.0
PANEL_H = 300.0

# Horizontal: native strip pitch (60 LED/m), grid centered on the panel
PITCH_X = 16.67
MARGIN_X = (PANEL_W - PITCH_X * COLS) / 2.0   # ≈ 16.64mm side margins

# Vertical: 1.8cm top/bottom margins around the 16 rows fix the pitch
MARGIN_TOP = 18.0
PITCH_Y = (PANEL_H - 2 * MARGIN_TOP) / ROWS   # = 16.5mm
GRID_BOTTOM = MARGIN_TOP + PITCH_Y * ROWS     # = 282mm

# 6-LED dot strip below the grid, under grid columns 5..10 (centered).
# Only the lit pairs (5,6 and 9,10) get cut openings; the middle two (7,8)
# stay solid so the dark separator reads as a gap.
DOT_GAP = 5.0
DOT_RADIUS = 5.0
DOT_ROW_Y = GRID_BOTTOM + DOT_GAP + DOT_RADIUS  # center = 292mm
DOT_LIT_COLS = [5, 6, 9, 10]

FONT_FACE = "Black Ops One"
FONT_SIZE = 15.0  # widest glyph Ж ≈ 15.8mm at this size, fits the pitch

CUT_COLOR = (1.0, 0.0, 0.0)
CUT_WIDTH = 0.1      # mm — hairline; laser software cuts by color, not width

# Blank margin around the panel so the 300x300 border isn't clipped at the page
# edge (a stroke sitting exactly on the boundary loses its outer half).
PAGE_MARGIN = 10.0   # mm
MM_TO_PT = 72.0 / 25.4


def cell_center(row, col):
    return MARGIN_X + (col + 0.5) * PITCH_X, MARGIN_TOP + (row + 0.5) * PITCH_Y


def dot_xs():
    return [cell_center(0, c)[0] for c in DOT_LIT_COLS]


def draw(ctx):
    """Draw the full cut layout in millimetres onto an mm-scaled context."""
    ctx.set_source_rgb(*CUT_COLOR)
    ctx.set_line_width(CUT_WIDTH)

    # Outer border — closed cut rectangle
    ctx.rectangle(0, 0, PANEL_W, PANEL_H)
    ctx.stroke()

    # Letter outlines — closed cut paths (glyphs converted to curves, not text)
    ctx.select_font_face(FONT_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(FONT_SIZE)

    # Common baseline from a reference cap glyph so all letters share the
    # same top edge (descenders of Д/Ц/Щ hang below, as in normal text)
    ref = ctx.text_extents("Н")

    for r in range(ROWS):
        for c in range(COLS):
            cx, cy = cell_center(r, c)
            ch = GRID[r][c]

            ext = ctx.text_extents(ch)
            x = cx - ext.width / 2 - ext.x_bearing
            y = cy - ref.height / 2 - ref.y_bearing

            ctx.new_path()
            ctx.move_to(x, y)
            ctx.text_path(ch)   # each glyph contour is already a closed TrueType outline
            ctx.stroke()

    # Dot circles — explicitly closed cut paths
    for dx in dot_xs():
        ctx.new_path()
        ctx.arc(dx, DOT_ROW_Y, DOT_RADIUS, 0, 2 * math.pi)
        ctx.close_path()
        ctx.stroke()


def _page_pt():
    # Page = panel + margin on every side (still 1:1; only the sheet is bigger)
    return (PANEL_W + 2 * PAGE_MARGIN) * MM_TO_PT, (PANEL_H + 2 * PAGE_MARGIN) * MM_TO_PT


def generate_pdf(pdf_path):
    w_pt, h_pt = _page_pt()
    surface = cairo.PDFSurface(pdf_path, w_pt, h_pt)
    ctx = cairo.Context(surface)
    ctx.scale(MM_TO_PT, MM_TO_PT)      # 1 user unit = 1 mm (vector, DPI-independent)
    ctx.translate(PAGE_MARGIN, PAGE_MARGIN)
    draw(ctx)
    surface.finish()


def generate_svg(svg_path):
    w_pt, h_pt = _page_pt()
    surface = cairo.SVGSurface(svg_path, w_pt, h_pt)
    ctx = cairo.Context(surface)
    ctx.scale(MM_TO_PT, MM_TO_PT)
    ctx.translate(PAGE_MARGIN, PAGE_MARGIN)
    draw(ctx)
    surface.finish()


if __name__ == "__main__":
    base = "/home/medivack/work/puppet/clock/led-clock/arduino/wordclock_ru"
    pdf = f"{base}/laser_cut_mask.pdf"
    svg = f"{base}/laser_cut_mask.svg"
    generate_pdf(pdf)
    generate_svg(svg)

    for src in (pdf, svg):
        shutil.copy2(src, f"/home/medivack/Downloads/{os.path.basename(src)}")

    print("Laser cut layout generated (send the PDF to the shop):")
    print(f"  PDF (1:1, mm): {pdf}")
    print(f"  SVG (preview): {svg}")
    print(f"  Panel: {PANEL_W:.1f} x {PANEL_H:.1f} mm  (page size 1:1)")
    print(f"  Cut lines: red hairline ({CUT_WIDTH}mm), glyphs as closed curves")
    print("  Copied both to ~/Downloads")
