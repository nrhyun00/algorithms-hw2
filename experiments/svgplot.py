"""외부 라이브러리 없이 꺾은선 그래프를 SVG로 그린다."""

import math
from xml.sax.saxutils import escape

COLORS = ["#2563eb", "#dc2626", "#059669", "#d97706", "#7c3aed", "#db2777"]


def line_chart(path, title, xlabel, ylabel, xs, series, ymax=None):
    """series: [(이름, [y...], 점선여부), ...]"""
    W, H = 720, 440
    left, right, top, bottom = 70, 190, 50, 60
    pw, ph = W - left - right, H - top - bottom
    xmin, xmax = 0, max(xs)
    if ymax is None:
        ymax = max(max(ys) for _, ys, _ in series)
    raw = ymax / 5
    mag = 10 ** math.floor(math.log10(raw))
    step = next(k * mag for k in (1, 2, 2.5, 5, 10) if k * mag >= raw)
    ticks = math.ceil(ymax / step - 1e-9)
    ymax = ticks * step

    def px(x):
        return left + (x - xmin) / (xmax - xmin) * pw

    def py(y):
        return top + ph - min(y, ymax) / ymax * ph

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="12">',
        f'<rect width="{W}" height="{H}" fill="white"/>',
        f'<text x="{left + pw / 2}" y="28" text-anchor="middle" font-size="16">{escape(title)}</text>',
    ]
    for i in range(ticks + 1):
        y = step * i
        out.append(f'<line x1="{left}" y1="{py(y):.1f}" x2="{left + pw}" y2="{py(y):.1f}" stroke="#e5e7eb"/>')
        out.append(f'<text x="{left - 8}" y="{py(y) + 4:.1f}" text-anchor="end">{y:g}</text>')
    for x in xs:
        out.append(f'<text x="{px(x):.1f}" y="{top + ph + 18}" text-anchor="middle">{x:g}</text>')
    out.append(f'<line x1="{left}" y1="{top + ph}" x2="{left + pw}" y2="{top + ph}" stroke="black"/>')
    out.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + ph}" stroke="black"/>')
    out.append(f'<text x="{left + pw / 2}" y="{H - 15}" text-anchor="middle">{escape(xlabel)}</text>')
    out.append(f'<text x="18" y="{top + ph / 2}" text-anchor="middle" '
               f'transform="rotate(-90 18 {top + ph / 2})">{escape(ylabel)}</text>')

    for k, (name, ys, dashed) in enumerate(series):
        color = COLORS[(k // 2) % len(COLORS)] if len(series) > 2 else COLORS[k % len(COLORS)]
        pts = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in zip(xs, ys))
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"{dash}/>')
        if not dashed:
            for x, y in zip(xs, ys):
                out.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="3" fill="{color}"/>')
        ly = top + 10 + k * 22
        lx = left + pw + 15
        out.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 28}" y2="{ly}" stroke="{color}" stroke-width="2"{dash}/>')
        out.append(f'<text x="{lx + 34}" y="{ly + 4}">{escape(name)}</text>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
