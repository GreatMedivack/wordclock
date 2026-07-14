#!/usr/bin/env python3
"""Widen the stencil bridges of Black Ops One to >= 1mm so the laser shop accepts the
file and the counter islands don't drop out.

Black Ops One is a stencil font: the islands inside О, А, Б, В, Д, Р, Ь, Ы, Ъ, Я ...
are held to the body by thin bridges (перемычки). In this font those bridges are only
0.2-0.4mm wide — below the shop's 1mm minimum gap between cut lines, and too fragile.

Fix: widen ONLY those bridges — the letters keep their exact original size and weight.
Per glyph: seal the bridge slits to reveal the counter islands, isolate just the material
connected to an island, take its thin necks (the bridges) and grow them by GROW each side
into the surrounding opening. Nothing else on the glyph moves — the outer silhouette,
stroke weight, chamfers and every non-counter letter are byte-for-byte the original font.
The thinnest ~0.25mm bridge ends up ~1.15mm, the island only more firmly attached.

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

from shapely.geometry import Polygon
from shapely.ops import unary_union

SEAL = 0.5     # close radius (mm) that seals the 0.2-0.4mm bridge slits to reveal islands
GROW = 0.4     # grow each counter island (with its bridges) by this much -> bridges +0.8mm

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


def _widen_bridges(opening):
    """Widen the island-holding bridges to >= ~1mm by growing each counter island (with
    its bridges) uniformly. The outer silhouette and stroke weight stay exactly the same;
    only the counters shrink a touch and their bridges thicken — cleanly, symmetrically."""
    # Seal the thin bridge slits so each counter becomes an enclosed island (a hole).
    sealed = opening.buffer(+SEAL, join_style=2, mitre_limit=3) \
                    .buffer(-SEAL, join_style=2, mitre_limit=3)
    islands = unary_union([Polygon(h) for p in _parts(sealed) for h in p.interiors])
    if islands.is_empty:
        return opening                      # no counter island -> glyph untouched
    # Inner material = filled silhouette minus opening = islands + bridges + chamfer bits.
    inner = _fill_holes(sealed).difference(opening)
    # Keep only the material connected to an island (islands + their bridges).
    island_material = unary_union(
        [c for c in _parts(inner) if c.intersects(islands.buffer(0.02))])
    if island_material.is_empty:
        return opening
    # Grow it into the surrounding counter opening: bridges gain 2*GROW, counters shrink
    # by GROW all round (shape preserved), island only more firmly attached.
    return opening.difference(island_material.buffer(GROW, join_style=2, mitre_limit=3))


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
