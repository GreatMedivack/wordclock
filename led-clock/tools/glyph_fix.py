#!/usr/bin/env python3
"""Widen the stencil bridges of Black Ops One to >= 1mm so the laser shop accepts the
file and the counter islands don't drop out.

Black Ops One is a stencil font: the islands inside О, А, Б, В, Д, Р, Ь, Ы, Ъ, Я ...
are held to the body by thin bridges (перемычки). In this font those bridges are only
0.2-0.4mm wide — below the shop's 1mm minimum gap between cut lines, and too fragile.

Fix: replace each thin bridge with a clean straight bar of a uniform BRIDGE_W width,
aligned to the bridge's own axis. The letters keep their exact original size and weight —
the outer silhouette, stroke weight, chamfers and every non-counter letter are
byte-for-byte the original font; only the sub-mm bridges become uniform ~1mm bars. No
steps, no per-bridge width variation, islands stay firmly attached.

Drop-in usage in a cairo generator (replaces `ctx.move_to(x, y); ctx.text_path(ch)`):

    import glyph_fix
    ...
    ctx.new_path()
    glyph_fix.append_path(ctx, ch, FONT_SIZE, x, y)
    ctx.fill()   # or .stroke(), same as before
"""

import cairo
import ctypes
import math
import os
from functools import reduce

from shapely.affinity import rotate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

SEAL = 0.5        # close radius (mm) that seals the 0.2-0.4mm bridge slits to find islands
DETECT = 0.5      # a bridge is island material an opening-by-DETECT erosion removes (<1mm)
BRIDGE_W = 1.0    # every bridge is rebuilt as a clean straight bar this wide (mm)
BRIDGE_EXT = 0.7  # extend each bar past the neck ends so it fully re-joins island and body
BRIDGE_MIN = 0.1  # ignore detected specks below this area (mm^2) — corner nicks
BRIDGE_MAX = 2.0  # above this a "thin" region is a pointed counter (А), not a bridge

FONT_FACE = "Black Ops One"

_FONT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          os.pardir, "arduino", "wordclock_ru", "BlackOpsOne.ttf")
ctypes.CDLL("libfontconfig.so.1").FcConfigAppFontAddFile(None, _FONT_FILE.encode())

_scratch = cairo.Context(cairo.ImageSurface(cairo.FORMAT_A8, 8, 8))
_scratch.select_font_face(FONT_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
_scratch.set_tolerance(0.05)  # curve flattening chord error (mm)

_cache = {}


def _raw_opening(ch, font_size):
    """Even-odd filled outline of ch at the baseline origin, in mm coordinates.

    Black Ops One's contours are cleanly nested (verified: even-odd == the font's
    intended nonzero fill for every grid glyph), so an even-odd combination of the
    flattened subpaths reproduces the glyph exactly."""
    _scratch.set_font_size(font_size)
    _scratch.new_path()
    _scratch.move_to(0, 0)
    _scratch.text_path(ch)
    path = _scratch.copy_path_flat()
    _scratch.new_path()

    rings = []
    cur = []
    for typ, pts in path:
        if typ == cairo.PATH_MOVE_TO:
            if len(cur) >= 3:
                rings.append(cur)
            cur = [pts]
        elif typ == cairo.PATH_LINE_TO:
            cur.append(pts)
        elif typ == cairo.PATH_CLOSE_PATH:
            if len(cur) >= 3:
                rings.append(cur)
            cur = []
    if len(cur) >= 3:
        rings.append(cur)

    polys = [Polygon(r).buffer(0) for r in rings if len(r) >= 3]
    if not polys:
        return None
    return reduce(lambda a, b: a.symmetric_difference(b), polys)


def _parts(g):
    if g is None or g.is_empty:
        return []
    return [g] if g.geom_type == "Polygon" else list(g.geoms)


def _fill_holes(g):
    return unary_union([Polygon(p.exterior) for p in _parts(g)])


def _bar(neck):
    """A clean straight BRIDGE_W-wide bar spanning `neck` along its own long axis."""
    rect = neck.minimum_rotated_rectangle.exterior.coords
    length, angle = 0.0, 0.0
    for i in range(len(rect) - 1):
        dx, dy = rect[i + 1][0] - rect[i][0], rect[i + 1][1] - rect[i][1]
        edge = math.hypot(dx, dy)
        if edge > length:
            length, angle = edge, math.degrees(math.atan2(dy, dx))
    angle %= 180
    for axis in (0, 90, 180):                    # snap near-axis bridges perfectly straight
        if abs(angle - axis) < 12:
            angle = axis % 180
    cx, cy = neck.centroid.x, neck.centroid.y
    half = length / 2 + BRIDGE_EXT
    return rotate(box(cx - half, cy - BRIDGE_W / 2, cx + half, cy + BRIDGE_W / 2),
                  angle, origin=(cx, cy))


def _widen_bridges(opening):
    """Rebuild each island-holding bridge as a uniform, straight BRIDGE_W bar. The rest
    of the glyph is left exactly as-is (full original size and weight)."""
    # Seal the thin bridge slits so each counter becomes an enclosed island (a hole).
    sealed = opening.buffer(+SEAL, join_style=2, mitre_limit=3) \
                    .buffer(-SEAL, join_style=2, mitre_limit=3)
    islands = unary_union([Polygon(h) for p in _parts(sealed) for h in p.interiors])
    if islands.is_empty:
        return opening                      # no counter island -> glyph untouched
    # Inner material = filled silhouette minus opening = islands + bridges + chamfer bits.
    inner = _fill_holes(sealed).difference(opening)
    island_material = unary_union(
        [c for c in _parts(inner) if c.intersects(islands.buffer(0.02))])
    if island_material.is_empty:
        return opening
    # Bridges = the thin necks of that material; skip pointed counters (too big) and nicks.
    thick = island_material.buffer(-DETECT, join_style=1).buffer(+DETECT, join_style=1)
    bars = [_bar(t) for t in _parts(island_material.difference(thick))
            if BRIDGE_MIN < t.area < BRIDGE_MAX]
    if not bars:
        return opening
    return opening.difference(unary_union(bars))


def fixed_opening(ch, font_size):
    """DRC-fixed glyph opening (shapely geometry) at the baseline origin, cached."""
    key = (ch, round(font_size, 3))
    if key not in _cache:
        geom = _raw_opening(ch, font_size)
        if geom is not None and not geom.is_empty:
            geom = _widen_bridges(geom)
        _cache[key] = geom
    return _cache[key]


def append_path(ctx, ch, font_size, x, y):
    """Append ch's DRC-fixed outline to ctx's current path, glyph origin at (x, y).

    Drop-in replacement for `ctx.move_to(x, y); ctx.text_path(ch)`. Leaves the
    fill/stroke to the caller (works with either fill rule — exteriors are CCW and
    holes CW)."""
    geom = fixed_opening(ch, font_size)
    if geom is None or geom.is_empty:
        return
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for g in polys:
        if g.is_empty:
            continue
        for ring in [g.exterior, *g.interiors]:
            coords = list(ring.coords)
            if not coords:
                continue
            ctx.move_to(x + coords[0][0], y + coords[0][1])
            for px, py in coords[1:]:
                ctx.line_to(x + px, y + py)
            ctx.close_path()
