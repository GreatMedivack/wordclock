#!/usr/bin/env python3
"""Widen the stencil bridges of Black Ops One to >= 1mm so the laser shop accepts the
file and the counter islands don't drop out.

Black Ops One is a stencil font: the islands inside О, А, Б, В, Д, Р, Ь, Ы, Ъ, Я ...
are held to the body by thin bridges (перемычки). In this font those bridges are only
0.2-0.4mm wide — below the shop's 1mm minimum gap between cut lines, and too fragile.

Fix: rebuild each bridge as a clean straight 1mm bar, with one long edge snapped flush
to the counter's edge so the widening cut runs into the counter (no stair-step on the
outside). Bars are axis-aligned rectangles — no rounding, no steps, all the same width.
The outer silhouette, stroke weight, chamfers and every non-counter letter are
byte-for-byte the original font; only the counters give up a 1mm strip to their bridge.
Islands stay firmly attached.

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

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

SEAL = 0.5      # close radius (mm) that seals the 0.2-0.4mm bridge slits to find islands
DETECT = 0.5    # a bridge is island material an opening-by-DETECT erosion removes (<1mm)
BRIDGE_W = 1.0  # rebuilt bridge width (mm), just over the shop's 1mm minimum
BRIDGE_EXT = 0.8   # extend the bar past the neck ends so it fully re-joins island and body
EDGE_SNAP = 0.8    # a bridge within this of a counter edge is snapped flush to that edge

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


def _flush_bar(neck, island):
    """A clean straight BRIDGE_W bar over `neck`, one long edge snapped flush to the
    counter island's edge so the cut runs into the counter (no stair-step on the outside);
    a mid-counter neck (e.g. О's centre bar) is centred instead."""
    bx0, by0, bx1, by1 = neck.bounds
    ix0, iy0, ix1, iy1 = island.bounds
    if (by1 - by0) > (bx1 - bx0):                       # vertical bridge
        if min(abs(bx0 - ix0), abs(bx1 - ix1)) > EDGE_SNAP:
            cx = (bx0 + bx1) / 2
            x0, x1 = cx - BRIDGE_W / 2, cx + BRIDGE_W / 2
        elif abs(bx0 - ix0) <= abs(bx1 - ix1):          # flush to counter's left edge
            x0, x1 = ix0, ix0 + BRIDGE_W
        else:                                            # flush to counter's right edge
            x0, x1 = ix1 - BRIDGE_W, ix1
        return box(x0, by0 - BRIDGE_EXT, x1, by1 + BRIDGE_EXT)
    if min(abs(by0 - iy0), abs(by1 - iy1)) > EDGE_SNAP:  # horizontal bridge
        cy = (by0 + by1) / 2
        y0, y1 = cy - BRIDGE_W / 2, cy + BRIDGE_W / 2
    elif abs(by0 - iy0) <= abs(by1 - iy1):
        y0, y1 = iy0, iy0 + BRIDGE_W
    else:
        y0, y1 = iy1 - BRIDGE_W, iy1
    return box(bx0 - BRIDGE_EXT, y0, bx1 + BRIDGE_EXT, y1)


def _widen_bridges(opening):
    """Rebuild each island bridge as a clean straight BRIDGE_W bar, flush to the counter
    edge. The outer silhouette, stroke weight and every non-counter letter stay
    byte-for-byte the original font; only the sub-mm bridges become uniform 1mm bars."""
    # Seal the thin bridge slits so each counter becomes an enclosed island (a hole).
    sealed = opening.buffer(+SEAL, join_style=2, mitre_limit=3) \
                    .buffer(-SEAL, join_style=2, mitre_limit=3)
    inner = _fill_holes(sealed).difference(opening)   # islands + bridges + chamfer bits
    bars = []
    for p in _parts(sealed):
        for hole in p.interiors:
            island = Polygon(hole)
            material = unary_union(
                [c for c in _parts(inner) if c.intersects(island.buffer(0.02))])
            if material.is_empty:
                continue
            thick = material.buffer(-DETECT, join_style=1).buffer(+DETECT, join_style=1)
            for neck in _parts(material.difference(thick)):
                if 0.1 < neck.area < 2.0:      # real bridge (skip nicks and pointed counters)
                    bars.append(_flush_bar(neck, island))
    if not bars:
        return opening                          # no counter island -> glyph untouched
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
