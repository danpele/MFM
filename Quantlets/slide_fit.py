"""
slide_fit.py -- charts drawn at the size they have on the slides
================================================================
Every chart is included in the Beamer decks in a fixed box (\\includegraphics[width=..., height=...]).
A chart drawn at 10 x 3.4 in and shown 2.6 in wide has its 9 pt tick labels shrunk to ~2.3 pt.

Importing this module (after matplotlib, before the figures are saved) wraps Figure.savefig. When a chart listed
in slide_fit_sizes.json ([width, height] of its box on the slide, in pt, smallest over all EN/RO lecture and
seminar decks) is saved, the figure is first redrawn at the size of that box, so that 1 pt in the figure is 1 pt on
the slide:

  * fonts: tick labels T_REF pt, the other texts scaled in proportion (hierarchy of the original design kept),
    never below T_MIN nor above T_MAX pt;
  * legends below the plot get as many columns as fit the width, and room is reserved for them;
  * titles and axis labels wrapped to the width of their axes; overlapping x tick labels thinned (numbers,
    dates) or rotated (categories);
  * layout recomputed (tight_layout, unless the figure uses its own layout engine).

Data, computations, colours and contents are not touched: only the geometry of the figure at save time.
Regenerate slide_fit_sizes.json after changing \\includegraphics sizes in the decks. Set SLIDE_FIT=0 to switch off. A figure with fig._sf_manual = True (laid out by hand at the size of its box)
only gets its final size adjusted.
Modelling Financial Markets - Daniel Traian PELE
"""

import os
import re
import json
import atexit
import warnings

from matplotlib.figure import Figure, FigureBase
from matplotlib.axes import Axes
from matplotlib.text import Text
from matplotlib.transforms import Bbox
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.layout_engine import ConstrainedLayoutEngine, TightLayoutEngine, PlaceHolderLayoutEngine

T_REF = 6.6     # tick labels on the slide (pt)
T_MIN = 6.3     # smallest text on the slide (pt)
T_MAX = 8.2     # largest text on the slide (pt)
T_LEG = 7.4     # largest legend text on the slide (pt)
PAD_PT = 7.2    # savefig pad_inches = 0.1 in (each side)
GAP_PT = 3.0    # gap between the plot and a legend below it

_HERE = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(_HERE, 'slide_fit_sizes.json')) as _f:
        SIZES = json.load(_f)
except OSError:
    SIZES = {}

LOG = []          # one dict per fitted chart (diagnostics, written to $SLIDE_FIT_LOG)

# -----------------------------------------------------------------------------------------------------------------
# remember how every legend was created, so that it can be re-created with another number of columns
_orig_ax_legend = Axes.legend
_orig_fig_legend = FigureBase.legend


def _ax_legend(self, *args, **kwargs):
    leg = _orig_ax_legend(self, *args, **kwargs)
    if leg is not None:
        leg._sf_call = ('ax', args, dict(kwargs))
    return leg


def _fig_legend(self, *args, **kwargs):
    leg = _orig_fig_legend(self, *args, **kwargs)
    if leg is not None:
        leg._sf_call = ('fig', args, dict(kwargs))
    return leg


Axes.legend = _ax_legend
FigureBase.legend = _fig_legend


# -----------------------------------------------------------------------------------------------------------------
def _renderer(fig):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _px(fig, pt):
    return pt * fig.dpi / 72


def _axes(fig):
    return [ax for ax in fig.get_axes() if ax.get_visible()]


def _drawn_ticklabels(ax, which):
    axis = ax.xaxis if which == 'x' else ax.yaxis
    out = []
    lo, hi = sorted(axis.get_view_interval())
    eps = 1e-9 * (abs(hi - lo) + 1)
    for tk in axis.get_major_ticks():
        loc = tk.get_loc()
        if loc is None or not (lo - eps <= loc <= hi + eps):
            continue
        for lab in (tk.label1, tk.label2):
            if lab.get_visible() and lab.get_text().strip():
                out.append(lab)
    return out


def _texts(fig):
    """(kind, axes, Text) for every visible text; tick labels only for ticks inside the view."""
    seen, out, tick_ids = set(), [], set()
    for ax in _axes(fig):
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                tick_ids.update((id(tk.label1), id(tk.label2)))
        for w in ('x', 'y'):
            for t in _drawn_ticklabels(ax, w):
                if id(t) not in seen:
                    seen.add(id(t))
                    out.append(('tick' + w, ax, t))
    for t in fig.findobj(Text):
        if id(t) in seen or id(t) in tick_ids:
            continue
        if not t.get_visible() or not t.get_text().strip():
            continue
        seen.add(id(t))
        out.append(('text', t.axes, t))
    return out


def _ref_size(texts):
    ticks = sorted(t.get_fontsize() for kind, _, t in texts if kind.startswith('tick'))
    if ticks:
        return ticks[len(ticks) // 2]
    allz = sorted(t.get_fontsize() for _, _, t in texts)
    return allz[len(allz) // 2] if allz else 9.0


def _map_fonts(fig, f_ref):
    """Tick labels T_REF pt on the slide, the rest in proportion, within [T_MIN, T_MAX]."""
    def m(f):
        return min(max(T_REF * f / f_ref, T_MIN), T_MAX)
    for ax in _axes(fig):
        for w in ('x', 'y'):
            labs = _drawn_ticklabels(ax, w)
            if labs:
                ax.tick_params(axis=w, which='both', labelsize=m(labs[0].get_fontsize()))
    leg_texts = set()
    for leg in list(fig.legends) + [a.get_legend() for a in _axes(fig) if a.get_legend() is not None]:
        leg_texts.update(id(t) for t in leg.get_texts())
        leg_texts.add(id(leg.get_title()))
    for kind, ax, t in _texts(fig):
        if not kind.startswith('tick'):
            t.set_fontsize(min(m(t.get_fontsize()), T_LEG) if id(t) in leg_texts else m(t.get_fontsize()))


def _clamp_fonts(fig, s):
    """No text below T_MIN pt on the slide when the figure is shown at scale s."""
    lo = T_MIN / s
    for ax in _axes(fig):
        for w in ('x', 'y'):
            labs = _drawn_ticklabels(ax, w)
            if labs and labs[0].get_fontsize() < lo:
                ax.tick_params(axis=w, which='both', labelsize=lo)
    for kind, ax, t in _texts(fig):
        if not kind.startswith('tick') and t.get_fontsize() < lo:
            t.set_fontsize(lo)


# -----------------------------------------------------------------------------------------------------------------
_MATH = re.compile(r'(\$[^$]*\$)')


def _tokens(s):
    """Words of a label; $...$ never split."""
    toks, glue = [], False
    for part in _MATH.split(s):
        if not part:
            continue
        if part.startswith('$') and part.endswith('$') and len(part) > 1:
            if toks and glue:
                toks[-1] += part
            else:
                toks.append(part)
            glue = True
            continue
        words = part.split(' ')
        for i, w in enumerate(words):
            if not w:
                glue = False
                continue
            if i == 0 and glue and toks:
                toks[-1] += w
            else:
                toks.append(w)
            glue = True
        glue = not part.endswith(' ')
    return toks


def _extent_along(t, renderer):
    bb = t.get_window_extent(renderer)
    return bb.height if abs((t.get_rotation() % 180) - 90) < 1 else bb.width


def _wrap(t, width_px, renderer):
    """Wrap a text on spaces (outside $...$) into 2-4 balanced lines so that it fits width_px."""
    if not hasattr(t, '_sf_orig'):
        t._sf_orig = t.get_text()
    orig = t._sf_orig
    t.set_text(orig)
    if width_px <= 0 or _extent_along(t, renderer) <= width_px:
        return False
    toks = _tokens(orig.replace('\n', ' '))
    if len(toks) < 2:
        return False
    best = orig
    for n in range(2, min(len(toks), 4) + 1):
        total = sum(len(x) for x in toks) + len(toks) - 1
        target = total / n
        lines, line = [], ''
        for w in toks:
            if line and len(line) + 1 + len(w) > target * 1.1 and len(lines) < n - 1:
                lines.append(line)
                line = w
            else:
                line = (line + ' ' + w) if line else w
        lines.append(line)
        best = '\n'.join(lines)
        t.set_text(best)
        if _extent_along(t, renderer) <= width_px:
            return True
    return True


def _slot(ax, renderer):
    """Width and height (px) of the grid cell of the axes (stable while the layout moves the axes)."""
    abb = ax.get_window_extent(renderer)
    try:
        ss = ax.get_subplotspec()
        pos = ss.get_position(ax.figure) if ss is not None else None
    except Exception:
        pos = None
    if pos is None:
        return abb.width, abb.height
    fb = ax.figure.bbox
    return max(abb.width, 0.82 * pos.width * fb.width), max(abb.height, 0.75 * pos.height * fb.height)


def _wrap_labels(fig, renderer):
    for ax in _axes(fig):
        abb = ax.get_window_extent(renderer)
        sw, sh = _slot(ax, renderer)
        abb = Bbox.from_bounds(abb.x0, abb.y0, sw, sh)
        # a title with no titled axes to its right may use the width up to the right edge of the figure
        titled = [o for o in _axes(fig) if o is not ax and any(
            tt.get_visible() and tt.get_text().strip() for tt in (o.title, o._left_title, o._right_title))]
        ob = [o.get_window_extent(renderer) for o in titled]
        right_free = not any(b.x0 > abb.x0 + 5 and b.y0 < abb.y1 and b.y1 > abb.y0 for b in ob)
        for t in (ax.title, ax._left_title, ax._right_title):
            if t.get_visible() and t.get_text().strip():
                width = abb.width * 1.08
                if right_free and t is ax._left_title:
                    width = max(width, fig.bbox.x1 - abb.x0 - _px(fig, 4))
                _wrap(t, width, renderer)
        if ax.xaxis.label.get_visible() and ax.xaxis.label.get_text().strip():
            _wrap(ax.xaxis.label, abb.width * 1.1, renderer)
        if ax.yaxis.label.get_visible() and ax.yaxis.label.get_text().strip():
            _wrap(ax.yaxis.label, abb.height * 1.15, renderer)
    st = getattr(fig, '_suptitle', None)
    if st is not None and st.get_visible() and st.get_text().strip():
        _wrap(st, fig.bbox.width * 0.98, renderer)


# -----------------------------------------------------------------------------------------------------------------
def _ncol(leg):
    return getattr(leg, '_ncols', getattr(leg, '_ncol', 1))


def _n_entries(leg):
    return len(leg.get_texts())


def _is_bottom_fig_legend(fig, leg):
    try:
        a = leg.get_bbox_to_anchor()
    except Exception:
        return False
    return a.y1 <= fig.bbox.height * 0.2 + 1 and leg._loc in (8, 9, 3, 4, 2, 1, 0)


def _is_bottom_ax_legend(ax, leg):
    try:
        a = leg.get_bbox_to_anchor()
    except Exception:
        return False
    return a.y1 < ax.bbox.y0 + 1


def _recreate(leg, ncol, fig, ax=None):
    call = getattr(leg, '_sf_call', None)
    if call is None:
        return leg
    kind, args, kw = call
    kw = dict(kw)
    kw.pop('ncols', None)
    kw['ncol'] = ncol
    kw.setdefault('columnspacing', 1.0)
    kw.setdefault('handlelength', 1.6)
    kw.setdefault('handletextpad', 0.5)
    texts = leg.get_texts()
    if texts:
        kw['fontsize'] = texts[0].get_fontsize()
    # current handles and labels (labels may have been wrapped)
    kw.pop('handles', None)
    kw.pop('labels', None)
    args = (leg.legend_handles, [t.get_text() for t in texts])
    title = leg.get_title()
    if title.get_text():
        kw['title'] = title.get_text()
        kw['title_fontsize'] = title.get_fontsize()
    vis = leg.get_visible()
    anchor = leg.get_bbox_to_anchor()
    loc = leg._loc
    leg.remove()
    new = ax.legend(*args, **kw) if kind == 'ax' else fig.legend(*args, **kw)
    new.set_visible(vis)
    return new


def _best_ncol(leg, fig, renderer, avail_px, ax=None):
    """Most columns (fewest rows) with the legend no wider than avail_px."""
    n_ent = _n_entries(leg)
    if n_ent <= 1:
        return leg
    best = None
    for n in range(n_ent, 0, -1):
        if _ncol(leg) != n or not getattr(leg, '_sf_compact', False):
            leg = _recreate(leg, n, fig, ax)
            if getattr(leg, '_sf_call', None) is None:
                return leg
            leg._sf_compact = True
            renderer = _renderer(fig)
        if leg.get_window_extent(renderer).width <= avail_px:
            best = n
            break
    if best is None and _ncol(leg) != 1:
        leg = _recreate(leg, 1, fig, ax)
        renderer = _renderer(fig)
    if best is None and leg.get_window_extent(renderer).width > avail_px:
        # even one column is too wide: long labels on several lines
        hl = leg.get_window_extent(renderer).width - max(t.get_window_extent(renderer).width for t in leg.get_texts())
        for t in leg.get_texts():
            _wrap(t, avail_px - hl - 6, renderer)
        leg = _recreate(leg, 1, fig, ax)
        leg._sf_compact = True
        renderer = _renderer(fig)
    # a tall single-column legend: labels on two lines, two columns
    if _ncol(leg) == 1 and n_ent >= 4 and not getattr(leg, '_sf_wrapped2', False) and \
            leg.get_window_extent(renderer).height > 0.28 * fig.bbox.height:
        hl = leg.get_window_extent(renderer).width - max(t.get_window_extent(renderer).width for t in leg.get_texts())
        for t in leg.get_texts():
            _wrap(t, avail_px / 2 - hl - 6, renderer)
        new = _recreate(leg, 2, fig, ax)
        renderer = _renderer(fig)
        if new.get_window_extent(renderer).width <= avail_px:
            leg = new
        else:
            leg = _recreate(new, 1, fig, ax)
        leg._sf_wrapped2 = True
        leg._sf_compact = True
    return leg


def _to_fig_legend(fig, ax, leg):
    """An axes legend below the plot becomes a figure legend below the figure (stable layout)."""
    texts = leg.get_texts()
    kw = dict(loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=_ncol(leg), frameon=False,
              fontsize=texts[0].get_fontsize() if texts else None)
    call = getattr(leg, '_sf_call', None)
    if call is not None:
        for k in ('handlelength', 'handletextpad', 'columnspacing', 'markerscale', 'numpoints', 'scatterpoints'):
            if k in call[2]:
                kw[k] = call[2][k]
    handles, labels = leg.legend_handles, [t.get_text() for t in texts]
    leg.remove()
    new = fig.legend(handles, labels, **kw)
    new._sf_bottom = True
    return new


def _legends_setup(fig, renderer):
    """Bottom legends: as many columns as fit the width."""
    bottom_ax = [ax for ax in _axes(fig) if ax.get_legend() is not None and ax.get_legend().get_visible()
                 and _is_bottom_ax_legend(ax, ax.get_legend())]
    if len(bottom_ax) == 1 and not fig.legends:
        _to_fig_legend(fig, bottom_ax[0], bottom_ax[0].get_legend())
        renderer = _renderer(fig)
    for leg in list(fig.legends):
        if leg.get_visible() and _is_bottom_fig_legend(fig, leg):
            leg = _best_ncol(leg, fig, renderer, fig.bbox.width * 0.98)
            leg._sf_bottom = True
            renderer = _renderer(fig)
    for ax in _axes(fig):
        leg = ax.get_legend()
        if leg is not None and leg.get_visible() and _is_bottom_ax_legend(ax, leg):
            n_axes = len([a for a in _axes(fig) if a.get_legend() is not None])
            avail = fig.bbox.width * 0.98 if n_axes == 1 else ax.get_window_extent(renderer).width * 1.15
            leg = _best_ncol(leg, fig, renderer, avail, ax)
            leg._sf_bottom = True
            renderer = _renderer(fig)


def _bottom_reserve(fig, renderer):
    """Height (figure fraction) taken by the bottom figure legends."""
    h = 0
    for leg in fig.legends:
        if leg.get_visible() and getattr(leg, '_sf_bottom', False):
            h = max(h, leg.get_window_extent(renderer).height)
    return (h + _px(fig, GAP_PT)) / fig.bbox.height if h else 0


def _place_legends(fig, renderer, reserve):
    for leg in fig.legends:
        if leg.get_visible() and getattr(leg, '_sf_bottom', False):
            x = getattr(leg, '_sf_x', None)
            if x is None:
                a = leg.get_bbox_to_anchor()
                x = leg._sf_x = min(max(((a.x0 + a.x1) / 2) / fig.bbox.width, 0.0), 1.0)
            leg.set_bbox_to_anchor((x, max(reserve - _px(fig, GAP_PT) / fig.bbox.height, 0)),
                                   transform=fig.transFigure)
            leg._loc = 9
    for ax in _axes(fig):
        leg = ax.get_legend()
        if leg is None or not leg.get_visible() or not getattr(leg, '_sf_bottom', False):
            continue
        try:
            xbb = ax.xaxis.get_tightbbox(renderer)
        except Exception:
            xbb = None
        abb = ax.get_window_extent(renderer)
        y_px = (xbb.y0 if xbb is not None else abb.y0) - _px(fig, GAP_PT)
        leg.set_bbox_to_anchor((0.5, (y_px - abb.y0) / abb.height), transform=ax.transAxes)
        leg._loc = 9


def _relayout(fig, reserve=0.0):
    eng = fig.get_layout_engine()
    rect = (0, min(reserve, 0.6), 1, 1)
    if isinstance(eng, ConstrainedLayoutEngine):
        eng.set(rect=rect)
        return
    if eng is not None and not isinstance(eng, (TightLayoutEngine, PlaceHolderLayoutEngine)):
        return
    # tight_layout from the same starting point every time (repeated calls compound with gridspec colorbars)
    from matplotlib.gridspec import GridSpec
    keys = ('left', 'right', 'bottom', 'top', 'wspace', 'hspace')
    if not hasattr(fig, '_sf_sp0'):
        sp = fig.subplotpars
        fig._sf_sp0 = {k: getattr(sp, k) for k in keys}
        fig._sf_gs0 = {}
        for ax in fig.get_axes():
            ss = ax.get_subplotspec() if hasattr(ax, 'get_subplotspec') else None
            g = ss.get_gridspec() if ss is not None else None
            if isinstance(g, GridSpec) and id(g) not in fig._sf_gs0:
                fig._sf_gs0[id(g)] = (g, {k: getattr(g, k) for k in keys})
    fig.subplots_adjust(**fig._sf_sp0)
    for g, params in fig._sf_gs0.values():
        g.update(**params)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            fig.tight_layout(pad=0.3, rect=rect)
            failed = any('not compatible with tight_layout' in str(w.message) for w in caught)
        except Exception:
            failed = True
    if failed:
        _manual_tight(fig, rect)


def _manual_tight(fig, rect, pad_pt=3.0):
    """Fallback when tight_layout cannot handle the axes: the block of axes is moved and scaled (relative
    arrangement kept) so that all their decorations fit inside rect."""
    axs = [ax for ax in fig.get_axes() if ax.get_visible()]
    if not axs:
        return
    for _ in range(3):
        renderer = _renderer(fig)
        W, H = fig.bbox.width, fig.bbox.height
        pos = [ax.get_position() for ax in axs]
        tb = [ax.get_tightbbox(renderer) for ax in axs]
        ux0 = min(p.x0 for p in pos); ux1 = max(p.x1 for p in pos)
        uy0 = min(p.y0 for p in pos); uy1 = max(p.y1 for p in pos)
        tx0 = min(t.x0 for t in tb if t is not None) / W; tx1 = max(t.x1 for t in tb if t is not None) / W
        ty0 = min(t.y0 for t in tb if t is not None) / H; ty1 = max(t.y1 for t in tb if t is not None) / H
        pad_x, pad_y = _px(fig, pad_pt) / W, _px(fig, pad_pt) / H
        ml, mr = ux0 - tx0, tx1 - ux1          # decorations outside the block of axes
        mb, mt = uy0 - ty0, ty1 - uy1
        nx0 = rect[0] + pad_x + ml; nx1 = rect[2] - pad_x - mr
        ny0 = rect[1] + pad_y + mb; ny1 = rect[3] - pad_y - mt
        if nx1 - nx0 < 0.05 or ny1 - ny0 < 0.05:
            return
        sx = (nx1 - nx0) / (ux1 - ux0); sy = (ny1 - ny0) / (uy1 - uy0)
        if abs(sx - 1) < 0.005 and abs(sy - 1) < 0.005 and abs(nx0 - ux0) < 0.003 and abs(ny0 - uy0) < 0.003:
            return
        for ax, p in zip(axs, pos):
            ax.set_position([nx0 + (p.x0 - ux0) * sx, ny0 + (p.y0 - uy0) * sy, p.width * sx, p.height * sy])


# -----------------------------------------------------------------------------------------------------------------
def _overlap(labs, renderer, axis='x'):
    bbs = [t.get_window_extent(renderer) for t in labs]
    if len(bbs) < 2:
        return False
    if axis == 'x':
        bbs.sort(key=lambda b: b.x0)
        return any(a.x1 + 2 > b.x0 and a.y0 < b.y1 and b.y0 < a.y1 for a, b in zip(bbs, bbs[1:]))
    bbs.sort(key=lambda b: b.y0)
    return any(a.y1 + 0.5 > b.y0 and a.x0 < b.x1 and b.x0 < a.x1 for a, b in zip(bbs, bbs[1:]))


def _numeric(s):
    s = s.replace('−', '-').replace(',', '').replace('%', '').replace('$', '').strip()
    try:
        float(s)
        return True
    except ValueError:
        return False


def _fix_ticks(fig, renderer):
    changed = False
    for ax in _axes(fig):
        if ax.name != 'rectilinear':
            continue
        for w in ('x', 'y'):
            axis = ax.xaxis if w == 'x' else ax.yaxis
            if axis.get_scale() == 'log':
                abb = ax.get_window_extent(renderer)
                length = (abb.width if w == 'x' else abb.height) * 72 / fig.dpi
                if length < 90 and not isinstance(axis.get_minor_formatter(), mticker.NullFormatter):
                    axis.set_minor_formatter(mticker.NullFormatter())
                    renderer = _renderer(fig)
            labs = _drawn_ticklabels(ax, w)
            if not _overlap(labs, renderer, w):
                continue
            changed = True
            loc = axis.get_major_locator()
            n = len(labs)
            if isinstance(loc, (mdates.AutoDateLocator, mdates.RRuleLocator, mdates.YearLocator)):
                fmt = axis.get_major_formatter()
                for k in range(max(n - 1, 2), 1, -1):
                    nl = mdates.AutoDateLocator(minticks=2, maxticks=k)
                    axis.set_major_locator(nl)
                    if isinstance(fmt, mdates.AutoDateFormatter):
                        axis.set_major_formatter(mdates.AutoDateFormatter(nl))
                    renderer = _renderer(fig)
                    if not _overlap(_drawn_ticklabels(ax, w), renderer, w):
                        break
            elif isinstance(loc, mticker.LogLocator) or axis.get_scale() == 'log':
                axis.set_minor_formatter(mticker.NullFormatter())
                renderer = _renderer(fig)
                if isinstance(loc, mticker.FixedLocator):
                    # fixed ticks chosen in the script: keep every second one
                    locs = [v for v in axis.get_majorticklocs()]
                    while len(locs) > 1 and _overlap(_drawn_ticklabels(ax, w), renderer, w):
                        locs = locs[::2]
                        axis.set_major_locator(mticker.FixedLocator(locs))
                        renderer = _renderer(fig)
                else:
                    for k in (5, 4, 3, 2):
                        if not _overlap(_drawn_ticklabels(ax, w), renderer, w):
                            break
                        axis.set_major_locator(mticker.LogLocator(numticks=k))
                        renderer = _renderer(fig)
                    if not _drawn_ticklabels(ax, w):
                        axis.set_major_locator(loc)
                        renderer = _renderer(fig)
                    # still crowded: keep every second tick that is drawn
                    while _overlap(_drawn_ticklabels(ax, w), renderer, w) and len(_drawn_ticklabels(ax, w)) > 1:
                        lo_, hi_ = sorted(axis.get_view_interval())
                        locs = [v for v in axis.get_majorticklocs() if lo_ <= v <= hi_]
                        axis.set_major_locator(mticker.FixedLocator(locs[::2]))
                        renderer = _renderer(fig)
            elif isinstance(loc, (mticker.AutoLocator, mticker.MaxNLocator)) and \
                    not isinstance(loc, mticker.LogLocator):
                for k in range(max(n - 2, 2), 1, -1):
                    axis.set_major_locator(mticker.MaxNLocator(nbins=k, steps=[1, 2, 2.5, 5, 10]))
                    renderer = _renderer(fig)
                    if not _overlap(_drawn_ticklabels(ax, w), renderer, w):
                        break
            elif w == 'x':
                texts = [t.get_text() for t in labs]
                if texts and all(_numeric(x) for x in texts) and n > 3:
                    locs = list(axis.get_majorticklocs())
                    tl = [t.get_text() for t in axis.get_majorticklabels()]
                    keep = list(range(0, len(locs), 2))
                    axis.set_ticks([locs[i] for i in keep], [tl[i] for i in keep])
                else:
                    # categories: wrapped to the tick spacing first, rotated only if that is not enough
                    xs = sorted(t.get_window_extent(renderer).x0 for t in labs)
                    locs_px = sorted(ax.transData.transform([(v, 0) for v in axis.get_majorticklocs()])[:, 0])
                    gap = min((b - a for a, b in zip(locs_px, locs_px[1:])), default=0)
                    for t in axis.get_majorticklabels():
                        if getattr(t, '_sf_rot', False):        # rotated in an earlier pass: start again flat
                            t.set_rotation(0)
                            t.set_ha('center')
                            t.set_rotation_mode('default')
                            t._sf_rot = False
                    renderer = _renderer(fig)
                    if not hasattr(axis, '_sf_cat'):
                        axis._sf_cat = (list(axis.get_majorticklocs()), [t.get_text() for t in axis.get_majorticklabels()])
                    cat_locs, cat_txt = axis._sf_cat
                    for frac in ((0.85, 0.7, 0.55) if gap > 0 else ()):
                        # the labels are set through the axis (tick label texts are rebuilt at every draw)
                        probe = Text(0, 0, '', fontsize=labs[0].get_fontsize(), fontproperties=labs[0].get_fontproperties())
                        probe.set_figure(fig)
                        wrapped = []
                        for txt in cat_txt:
                            probe._sf_orig = txt
                            _wrap(probe, gap * frac, renderer)
                            wrapped.append(probe.get_text())
                        axis.set_ticks(cat_locs, wrapped)
                        renderer = _renderer(fig)
                        if not _overlap(_drawn_ticklabels(ax, w), renderer, w):
                            break
                    if _overlap(_drawn_ticklabels(ax, w), renderer, w):
                        axis.set_ticks(cat_locs, cat_txt)
                        for t in axis.get_majorticklabels():
                            t.set_rotation(35)
                            t.set_ha('right')
                            t.set_rotation_mode('anchor')
                            t._sf_rot = True
                renderer = _renderer(fig)
    return changed


# -----------------------------------------------------------------------------------------------------------------

def _shift_text(fig, t, dy_px, renderer):
    """Move a text (or the text of an annotation) vertically by dy_px."""
    from matplotlib.text import Annotation
    from matplotlib.transforms import ScaledTranslation
    if isinstance(t, Annotation):
        coords = t.anncoords if isinstance(t.anncoords, str) else None
        if coords in ('offset points', 'offset fontsize', 'offset pixels'):
            x, y = t.xyann
            k = {'offset points': 72 / fig.dpi, 'offset pixels': 1.0,
                 'offset fontsize': 72 / fig.dpi / max(t.get_fontsize(), 1)}[coords]
            t.xyann = (x, y + dy_px * k)
            return True
        try:
            tr = t._get_xy_transform(renderer, t.anncoords)
            px, py = tr.transform(t.xyann)
            t.xyann = tuple(tr.inverted().transform((px, py + dy_px)))
            return True
        except Exception:
            return False
    t.set_transform(t.get_transform() + ScaledTranslation(0, dy_px / fig.dpi, fig.dpi_scale_trans))
    return True


def _repel(fig, renderer, max_pt=10.0):
    """Push apart overlapping annotations of the same axes (small vertical moves only)."""
    lim = _px(fig, max_pt)
    for ax in _axes(fig):
        ts = [t for t in ax.texts if t.get_visible() and t.get_text().strip()]
        if len(ts) < 2 or len(ts) >= 12:      # >= 12: cell labels of a heatmap or table, never moved
            continue
        moved = {id(t): getattr(t, '_sf_moved', 0.0) for t in ts}   # cumulative over the layout passes
        for _ in range(12):
            renderer = _renderer(fig)
            bbs = [t.get_window_extent(renderer) for t in ts]
            hit = False
            for i in range(len(ts)):
                for j in range(i + 1, len(ts)):
                    a, b = bbs[i], bbs[j]
                    if a.x1 <= b.x0 or b.x1 <= a.x0 or a.y1 <= b.y0 or b.y1 <= a.y0:
                        continue
                    lo, hi = (i, j) if (a.y0 + a.y1) <= (b.y0 + b.y1) else (j, i)
                    need = min(bbs[lo].y1, bbs[hi].y1) - max(bbs[lo].y0, bbs[hi].y0) + 1
                    d = need / 2
                    if abs(moved[id(ts[hi])]) + d > lim or abs(moved[id(ts[lo])]) + d > lim:
                        continue
                    if _shift_text(fig, ts[hi], d, renderer) and _shift_text(fig, ts[lo], -d, renderer):
                        moved[id(ts[hi])] += d
                        moved[id(ts[lo])] -= d
                        ts[hi]._sf_moved = moved[id(ts[hi])]
                        ts[lo]._sf_moved = moved[id(ts[lo])]
                        hit = True
            if not hit:
                break
    return _renderer(fig)


def _pdf_size_pt(fig):
    """Size (pt) of the PDF that savefig(bbox_inches='tight') writes."""
    import io
    buf = io.BytesIO()
    _orig_savefig(fig, buf, format='pdf', bbox_inches='tight', pad_inches=PAD_PT / 72, transparent=True)
    m = re.search(rb'/MediaBox\s*\[\s*([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)\s*\]', buf.getvalue())
    x0, y0, x1, y1 = (float(v) for v in m.groups())
    return x1 - x0, y1 - y0


def _saved_size_pt(fig, renderer):
    bb = fig.get_tightbbox(renderer)
    return bb.width * 72 + 2 * PAD_PT, bb.height * 72 + 2 * PAD_PT


def _layout(fig):
    """Legends, layout, wrapped labels, tick labels; returns a fresh renderer."""
    renderer = _renderer(fig)
    _legends_setup(fig, renderer)
    renderer = _renderer(fig)
    reserve = _bottom_reserve(fig, renderer)
    for _ in range(2):
        _relayout(fig, reserve)
        renderer = _renderer(fig)
        _wrap_labels(fig, renderer)
        _relayout(fig, reserve)
        renderer = _renderer(fig)
        _fix_ticks(fig, renderer)
        _place_legends(fig, renderer, reserve)
        renderer = _renderer(fig)
    return _repel(fig, renderer)


def _axes_sizes(fig, renderer, s):
    """Smallest plot area (width, height) on the slide, in pt (diagnostic)."""
    out = []
    for ax in _axes(fig):
        if not ax.axison or ax.get_label() == '<colorbar>':
            continue
        bb = ax.get_window_extent(renderer)
        out.append((bb.width * 72 / fig.dpi * s, bb.height * 72 / fig.dpi * s))
    if not out:
        return None
    return [round(min(w for w, h in out), 1), round(min(h for w, h in out), 1)]


def _count_overlaps(fig, renderer):
    """Overlapping pairs of visible texts (diagnostic only)."""
    bbs = []
    for kind, ax, t in _texts(fig):
        try:
            bbs.append(t.get_window_extent(renderer).shrunk(0.9, 0.8))
        except Exception:
            pass
    return sum(1 for i in range(len(bbs)) for j in range(i + 1, len(bbs)) if bbs[i].overlaps(bbs[j]))


def _fit_size(fig, BW, BH):
    """Figure size such that the saved chart (tight bbox + pad) fills the box (BW, BH); the layout choices
    (legend columns, wrapped labels, thinned ticks) can make the size oscillate: the best size found that fits
    the box is kept."""
    tried = []

    def record(W, H):
        tried.append((tuple(fig.get_size_inches()), W, H))

    renderer = _layout(fig)
    for _ in range(10):
        W, H = _saved_size_pt(fig, renderer)
        record(W, H)
        ex_w, ex_h = W - BW, H - BH
        if abs(ex_w) <= 0.6 and abs(ex_h) <= 0.6:
            break
        fw, fh = fig.get_size_inches()
        nfw = max(fw - ex_w / 72, 0.7 * (BW - 2 * PAD_PT) / 72)
        nfh = max(fh - ex_h / 72, 0.7 * (BH - 2 * PAD_PT) / 72)
        if abs(nfw - fw) < 1e-3 and abs(nfh - fh) < 1e-3:
            break
        fig.set_size_inches(nfw, nfh)
        renderer = _layout(fig)
    # final check on the PDF itself (text metrics of the PDF backend differ slightly from Agg)
    pdf_tried = []

    def min_axes():
        r = _renderer(fig)
        hs = [ax.get_window_extent(r).height * 72 / fig.dpi for ax in _axes(fig)
              if ax.axison and ax.get_label() != '<colorbar>']
        return min(hs) if hs else 100.0

    for _ in range(6):
        W, H = _pdf_size_pt(fig)
        pdf_tried.append((tuple(fig.get_size_inches()), W, H, min_axes()))
        ex_w, ex_h = W - BW, H - BH
        if abs(ex_w) <= 0.4 and abs(ex_h) <= 0.4:
            return renderer
        fw, fh = fig.get_size_inches()
        fig.set_size_inches(max(fw - ex_w / 72, 0.3), max(fh - ex_h / 72, 0.3))
        renderer = _layout(fig)
    W, H = _pdf_size_pt(fig)
    pdf_tried.append((tuple(fig.get_size_inches()), W, H, min_axes()))
    # not converged: the size that fits the box with the largest area and plots that are not squashed (the PDF is
    # then padded to the proportions of the box)
    fits = [t for t in pdf_tried if t[1] <= BW + 0.5 and t[2] <= BH + 0.5 and t[3] >= 15]
    best = max(fits, key=lambda t: t[1] * t[2]) if fits else \
        min(pdf_tried, key=lambda t: max(t[1] / BW, t[2] / BH) + (1 if t[3] < 15 else 0))
    if tuple(fig.get_size_inches()) != best[0]:
        fig.set_size_inches(*best[0])
        renderer = _layout(fig)
    return renderer


def _collapsed(fig, renderer):
    for ax in _axes(fig):
        if not ax.axison or ax.get_label() == '<colorbar>':
            continue
        bb = ax.get_window_extent(renderer)
        if bb.width * 72 / fig.dpi < 30 or bb.height * 72 / fig.dpi < 18:
            return True
    return False


def _unwrap(fig):
    for t in fig.findobj(Text):
        if hasattr(t, '_sf_orig'):
            t.set_text(t._sf_orig)
    for ax in _axes(fig):
        for axis in (ax.xaxis, ax.yaxis):
            if hasattr(axis, '_sf_cat'):
                axis.set_ticks(*axis._sf_cat)


def fit(fig, name):
    """Redraw the figure at the size of its box on the slide (1 pt in the figure = 1 pt on the slide)."""
    box = SIZES.get(name)
    if not box or getattr(fig, '_sf_fitted', None) == name:
        return
    BW, BH = box
    renderer = _renderer(fig)
    w0, h0 = fig.get_size_inches()
    if getattr(fig, '_sf_manual', False):
        # chart laid out by hand at the size of its box: only the final size is adjusted
        for _ in range(4):
            W, H = _pdf_size_pt(fig)
            if abs(W - BW) <= 0.4 and abs(H - BH) <= 0.4:
                break
            fw, fh = fig.get_size_inches()
            fig.set_size_inches(max(fw - (W - BW) / 72, 0.3), max(fh - (H - BH) / 72, 0.3))
        W, H = _pdf_size_pt(fig)
        s = min(BW / W, BH / H)
        renderer = _renderer(fig)
        sizes = [t.get_fontsize() * s for _, _, t in _texts(fig)]
        LOG.append(dict(name=name, box=[BW, BH], from_in=[round(w0, 2), round(h0, 2)],
                        to_in=[round(x, 2) for x in fig.get_size_inches()], saved=[round(W, 1), round(H, 1)],
                        scale=round(s, 3), min_pt=round(min(sizes), 2) if sizes else None,
                        overlaps=_count_overlaps(fig, renderer), axes=_axes_sizes(fig, renderer, s), manual=True))
        fig._sf_fitted = name
        return
    _map_fonts(fig, _ref_size(_texts(fig)))
    fig.set_size_inches((BW - 2 * PAD_PT) / 72, (BH - 2 * PAD_PT) / 72)
    renderer = _renderer(fig)
    _legends_setup(fig, renderer)
    renderer = _fit_size(fig, BW, BH)
    W, H = _pdf_size_pt(fig)
    s = min(BW / W, BH / H)
    if 0.6 < s < 0.995:
        _clamp_fonts(fig, s)
        renderer = _layout(fig)
        W, H = _saved_size_pt(fig, renderer)
        s = min(BW / W, BH / H)
    sizes = [t.get_fontsize() * s for _, _, t in _texts(fig)]
    LOG.append(dict(name=name, box=[BW, BH], from_in=[round(w0, 2), round(h0, 2)],
                    to_in=[round(x, 2) for x in fig.get_size_inches()], saved=[round(W, 1), round(H, 1)],
                    scale=round(s, 3), min_pt=round(min(sizes), 2) if sizes else None,
                    overlaps=_count_overlaps(fig, renderer), axes=_axes_sizes(fig, renderer, s)))
    fig._sf_fitted = name


_orig_savefig = Figure.savefig


def _pdf_tightbbox(fig):
    """Tight bounding box (inches) as the PDF backend computes it in savefig(bbox_inches='tight')."""
    from matplotlib.backend_bases import _get_renderer
    with fig.canvas._switch_canvas_and_return_print_method('pdf') as print_method:
        renderer = _get_renderer(fig, print_method)
        return fig.get_tightbbox(renderer)


def _box_bbox(fig, BW, BH):
    """Area saved (inches): the tight bounding box plus the pad, widened or heightened (centred) to the exact
    proportions of the box on the slide, so that \\includegraphics given only a width or only a height never
    makes the chart larger than its box."""
    tb = _pdf_tightbbox(fig)
    pad = PAD_PT / 72
    x0, y0, x1, y1 = tb.x0 - pad, tb.y0 - pad, tb.x1 + pad, tb.y1 + pad
    w, h = x1 - x0, y1 - y0
    a = BW / BH
    if w / h < a:
        extra = h * a - w
        x0, x1 = x0 - extra / 2, x1 + extra / 2
    else:
        extra = w / a - h
        y0, y1 = y0 - extra / 2, y1 + extra / 2
    return Bbox.from_extents(x0, y0, x1, y1)


def _pickle(fig, name):
    """Optional (development): keep the figure as drawn by the script, before fitting ($SLIDE_FIT_PICKLE)."""
    d = os.environ.get('SLIDE_FIT_PICKLE')
    if not d or getattr(fig, '_sf_fitted', None) == name or getattr(fig, '_sf_pickled', None) == name:
        return
    import pickle
    try:
        data = pickle.dumps(fig)
    except Exception:
        try:
            import cloudpickle
            data = cloudpickle.dumps(fig)
        except Exception as exc:
            print('slide_fit: cannot pickle', name, exc)
            return
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + '.pkl'), 'wb') as f:
        f.write(data)
    fig._sf_pickled = name


def _savefig(self, fname, *args, **kwargs):
    try:
        base = os.path.splitext(os.path.basename(os.fspath(fname)))[0]
    except TypeError:
        base = None
    if base and base in SIZES and os.environ.get('SLIDE_FIT', '1') != '0':
        _pickle(self, base)
        fit(self, base)
        kwargs['bbox_inches'] = _box_bbox(self, *SIZES[base])
        kwargs['pad_inches'] = 0
    return _orig_savefig(self, fname, *args, **kwargs)


Figure.savefig = _savefig


def _dump_log():
    path = os.environ.get('SLIDE_FIT_LOG')
    if path and LOG:
        with open(path, 'a') as f:
            for row in LOG:
                f.write(json.dumps(row) + '\n')


atexit.register(_dump_log)
