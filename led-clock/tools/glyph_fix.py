#!/usr/bin/env python3
"""Widen the stencil bridges of Black Ops One to >= 1mm so the laser shop accepts the
file and the counter islands don't drop out.

Black Ops One is a stencil font: the islands inside О, А, Б, В, Д, Р, Ь, Ы, Ъ, Я ...
are held to the body by thin bridges (перемычки). In this font those bridges are only
0.2-0.4mm wide — below the shop's 1mm minimum gap between cut lines, and too fragile.

Fix: find EVERY sub-1mm material spot (the counter bridges AND the font's thin corner
chamfers at junctions like П/Т/Н) and lay a clean straight 1mm bar over it, along the
spot's own axis so diagonal ones (А, И) get an angled cut. Everything ends up the same
1mm width — consistent and over the shop's minimum. The outer silhouette and stroke
weight stay byte-for-byte the original font; islands only get more firmly attached.

Drop-in usage in a cairo generator (replaces `ctx.move_to(x, y); ctx.text_path(ch)`):

    import glyph_fix
    ...
    ctx.new_path()
    glyph_fix.append_path(ctx, ch, FONT_SIZE, x, y)
    ctx.fill()   # or .stroke(), same as before
"""

import cairo
import ctypes
import os
from functools import reduce

import math

from shapely.affinity import rotate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

R = 0.5         # any material strip a round opening-by-R erosion removes is < 2R = 1mm
BRIDGE_W = 1.1  # every thin spot is rebuilt at this width (mm), a margin over 1mm
BRIDGE_EXT = 0.6   # extend each bar past the thin spot so it fully re-joins the solid parts
MIN_AREA = 0.1  # ignore detected specks below this (mm^2) — sub-pixel corner artifacts
SNAP = 10.0     # snap a bar's angle to horizontal/vertical if within this many degrees

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


def _bar(thin):
    """A clean straight BRIDGE_W-wide bar covering `thin`, along its own long axis
    (axis-snapped when near-orthogonal) so diagonal spots (А, И) get an angled cut."""
    rect = thin.minimum_rotated_rectangle.exterior.coords
    length, angle = 0.0, 0.0
    for i in range(len(rect) - 1):
        dx, dy = rect[i + 1][0] - rect[i][0], rect[i + 1][1] - rect[i][1]
        edge = math.hypot(dx, dy)
        if edge > length:
            length, angle = edge, math.degrees(math.atan2(dy, dx))
    angle %= 180
    for axis in (0, 90, 180):
        if abs(angle - axis) < SNAP:
            angle = axis % 180
    cx, cy = thin.centroid.x, thin.centroid.y
    half = length / 2 + BRIDGE_EXT
    return rotate(box(cx - half, cy - BRIDGE_W / 2, cx + half, cy + BRIDGE_W / 2),
                  angle, origin=(cx, cy))


def _widen_bridges(opening):
    """Bring every sub-1mm material spot (counter bridges AND the font's thin corner
    chamfers) up to a uniform BRIDGE_W by adding a clean straight bar there. A round
    morphological opening of the remaining material finds exactly the strips narrower
    than 2R = 1mm; each becomes a 1mm bar along its own axis. Outer silhouette and
    stroke weight are untouched; islands only get more firmly attached."""
    minx, miny, maxx, maxy = opening.bounds
    material = box(minx - 2, miny - 2, maxx + 2, maxy + 2).difference(opening)
    opened = material.buffer(-R, join_style=1).buffer(+R, join_style=1)
    bars = [_bar(t) for t in _parts(material.difference(opened)) if t.area > MIN_AREA]
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
