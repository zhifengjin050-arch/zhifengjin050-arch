# -*- coding: utf-8 -*-
"""
GitHub Profile README 生成器 (v4 · content-first portfolio)

以 lenyanjgk/lenyanjgk 的视觉语言为骨架，升级为自托管动画 SVG + bento 玻璃面板：
- 所有动画均为纯 SMIL，提交进仓库，不依赖任何第三方服务
- 深浅双版本 SVG，<picture> 按系统主题切换
- 内容面向 AI Agent / AIOps / 平台工程，全部基于真实仓库数据

用法：编辑 profile.config.json -> python generate.py
产出：assets/*.svg、README.md、preview.html
"""
import json
import math
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

CFG = json.loads((ROOT / "profile.config.json").read_text(encoding="utf-8"))

THEMES = {
    "light": dict(
        card="#F0EADA", card2="#F8F3E6", ink="#3A2E14", sub="#6B5A33",
        accent="#8A6E14", accent2="#B08D2E", line="#DCCBA6", chip="#E7D9B8",
        green="#4A7C59", glow="#FFFFFF",
    ),
    "dark": dict(
        card="#171309", card2="#211C11", ink="#F5EBD3", sub="#B3A480",
        accent="#E3B341", accent2="#C99A2E", line="#5A4A2A", chip="#302815",
        green="#7FBF8E", glow="#FFE9A8",
    ),
}

SANS = "'Inter','Segoe UI','PingFang SC','Microsoft YaHei',sans-serif"
MONO = "'Fira Code','SFMono-Regular',Consolas,monospace"


def esc(s):
    return html.escape(str(s), quote=True)


def q(s):
    return str(s).replace(" ", "%20")


def S(W, H, body):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">\n'
        f"{body}\n</svg>\n"
    )


def bg(t, W, H, r=16, fill=None, stroke=True):
    f = fill or t["card"]
    s = f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{r}" fill="{f}"'
    if stroke:
        s += f' stroke="{t["line"]}" stroke-width="1"'
    return s + "/>"


def R(x, y, w, h, rx, fill, opacity=None, stroke=None, sw=1):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
    if opacity is not None:
        s += f' opacity="{opacity}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + "/>"


def T(x, y, s, size, t, color=None, weight=400, mono=False, anchor="start",
      opacity=None, spacing=None):
    parts = [
        f'x="{x}"', f'y="{y}"',
        f'font-family="{MONO if mono else SANS}"',
        f'font-size="{size}"', f'font-weight="{weight}"',
        f'fill="{color or t["ink"]}"', f'text-anchor="{anchor}"',
    ]
    if opacity is not None:
        parts.append(f'opacity="{opacity}"')
    if spacing is not None:
        parts.append(f'letter-spacing="{spacing}"')
    return f'<text {" ".join(parts)}>{esc(s)}</text>'


def width_of(s, size=14, mono=False):
    total = 0.0
    for ch in str(s):
        total += size if ord(ch) > 127 else size * (0.60 if mono else 0.56)
    return total


def clip(s, n=62):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def strip_md(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", str(s))
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return html.escape(s)


def chip(x, y, label, t, size=12):
    w = width_of(label, size) + 24
    out = R(x, y, w, 25, 12, t["chip"])
    out += T(x + w / 2, y + 17, label, size, t, color=t["sub"], anchor="middle")
    return out, w


# --------------------------------------------------------------------------
# 玻璃质感 / 动效组件（纯 SMIL，无脚本、无外部资源）
# --------------------------------------------------------------------------

def glass_bg(t, W, H, r=16, mesh=False, mid="mesh"):
    p = [bg(t, W, H, r)]
    if mesh:
        p.append(f'<defs><pattern id="{mid}" width="26" height="26" patternUnits="userSpaceOnUse">'
                 f'<path d="M26 0 L0 0 0 26" fill="none" stroke="{t["line"]}" '
                 f'stroke-width="0.6"/></pattern></defs>')
        p.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="{r}" '
                 f'fill="url(#{mid})" opacity="0.45"/>')
    p.append(f'<path d="M{r+6} 1.5 L{W-r-6} 1.5" stroke="{t["glow"]}" '
             f'stroke-width="1" opacity="0.32"/>')
    return p


def glass_card(t, x, y, w, h, r=12):
    return [
        R(x, y, w, h, r, t["card2"], stroke=t["line"]),
        f'<path d="M{x+r} {y+1.5} L{x+w-r} {y+1.5}" stroke="{t["glow"]}" '
        f'stroke-width="1" opacity="0.28"/>',
    ]


def beam_defs(t, gid="beam", strength="0.16"):
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{t["accent"]}" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="{t["accent"]}" stop-opacity="{strength}"/>'
            f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>'
            f'</linearGradient></defs>')


def beam(t, W, H, dur="8s", gid="beam"):
    return (f'<rect x="-340" y="0" width="340" height="{H}" fill="url(#{gid})">'
            f'<animate attributeName="x" values="-340;{W+60}" dur="{dur}" '
            f'repeatCount="indefinite"/></rect>')


def pulse(cx, cy, r, color, begin, dur="2.6s"):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}">'
            f'<animate attributeName="opacity" values="0.25;1;0.25" dur="{dur}" '
            f'begin="{begin}s" repeatCount="indefinite"/></circle>')


# --------------------------------------------------------------------------
# 各区块 SVG
# --------------------------------------------------------------------------

def banner(t, c):
    W, H = 1000, 250
    A, AC2, INK, SUB, LINE = (
        t["accent"], t["accent2"], t["ink"], t["sub"], t["line"]
    )
    p = [
        '<defs>',
        '<clipPath id="heroclip"><rect x="1" y="1" width="998" height="248" rx="18"/></clipPath>',
        f'<radialGradient id="halo"><stop offset="0" stop-color="{A}" stop-opacity="0.17"/>'
        f'<stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>',
        f'<pattern id="mesh" width="26" height="26" patternUnits="userSpaceOnUse">'
        f'<path d="M26 0 L0 0 0 26" fill="none" stroke="{LINE}" stroke-width="0.6"/>'
        f'</pattern>',
        beam_defs(t),
        '</defs>',
        bg(t, W, H, 18),
        '<g clip-path="url(#heroclip)">',
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#mesh)" opacity="0.50"/>',
        f'<circle cx="862" cy="108" r="170" fill="url(#halo)"/>',
        beam(t, W, H, "7s"),
        f'<line x1="0" y1="0" x2="{W}" y2="0" stroke="{A}" stroke-width="1" opacity="0.16">'
        f'<animate attributeName="y1" values="0;{H}" dur="5.5s" repeatCount="indefinite"/>'
        f'<animate attributeName="y2" values="0;{H}" dur="5.5s" repeatCount="indefinite"/>'
        f'</line>',
        '</g>',
        f'<path d="M24 1.5 L976 1.5" stroke="{t["glow"]}" stroke-width="1" opacity="0.35"/>',
    ]

    cx, cy = 862, 108
    p.append(f'<circle cx="{cx}" cy="{cy}" r="112" fill="none" stroke="{A}" '
             f'stroke-width="1" stroke-dasharray="3 7" opacity="0.30"/>')
    for i in range(6):
        ang = math.pi * 2 * i / 6 - math.pi / 2
        nx, ny = cx + 78 * math.cos(ang), cy + 78 * math.sin(ang)
        p.append(f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" '
                 f'stroke="{A}" stroke-width="1" stroke-dasharray="3 5" opacity="0.34">'
                 f'<animate attributeName="stroke-dashoffset" values="0;-16" dur="2s" '
                 f'repeatCount="indefinite"/></line>')
        p.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="8" fill="{t["chip"]}" '
                 f'stroke="{A}" stroke-width="1.2"/>')
        p.append(pulse(f"{nx:.1f}", f"{ny:.1f}", 3.5, A, round(i * 0.4, 1)))
    p.append(f'<circle cx="{cx}" cy="{cy}" r="33" fill="{A}" opacity="0.15"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="33" fill="none" stroke="{A}" '
             f'stroke-width="1.5" opacity="0.65"/>')
    p.append(T(cx, cy + 7, "AI", 20, t, color=A, weight=700, mono=True, anchor="middle"))
    p.append(T(cx, 236, "GOVERNED RUNTIME · 2026", 10, t, color=SUB,
               mono=True, anchor="middle", spacing=1.2))

    p.append(R(48, 38, 5, 22, 2, A))
    p.append(T(66, 55, c["eyebrow"], 11, t, color=A, weight=600, mono=True, spacing=2))
    p.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" '
             f'dur="1.3s" fill="freeze"/>')
    p.append(T(46, 126, c["name_en"], 60, t, color=INK, weight=800))
    p.append('</g>')
    p.append(T(50, 160, f'@{c["username"]}', 16, t, color=SUB, mono=True))
    p.append(T(50, 190, c["role"], 14, t, color=AC2, weight=600))
    p.append(f'<line x1="50" y1="202" x2="470" y2="202" stroke="{LINE}" stroke-width="1"/>')
    x = 50
    for label in c["banner_chips"]:
        s, w = chip(x, 214, label, t, 11)
        p.append(s)
        x += w + 10
    return S(W, H, "\n".join(p))


def typing(t, c):
    W, H = 1000, 66
    A, INK, SUB = t["accent"], t["ink"], t["sub"]
    line = c["typing_line"]
    tw = width_of(line, 15, True)
    p = glass_bg(t, W, H, 14, mesh=False)
    p.append(f'<defs><clipPath id="twclip"><rect x="70" y="14" width="0" height="38">'
             f'<animate attributeName="width" values="0;{tw+6:.1f};{tw+6:.1f}" '
             f'keyTimes="0;0.62;1" dur="5s" repeatCount="indefinite"/>'
             f'</rect></clipPath></defs>')
    p.append(f'<circle cx="30" cy="33" r="5" fill="{A}">'
             f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" '
             f'repeatCount="indefinite"/></circle>')
    p.append(T(48, 39, ">", 17, t, color=A, weight=700, mono=True))
    p.append(f'<text x="70" y="39" font-family="{MONO}" font-size="15" '
             f'font-weight="400" fill="{INK}" clip-path="url(#twclip)">{esc(line)}</text>')
    cx = 70 + tw + 9
    p.append(f'<rect x="{cx:.1f}" y="22" width="9" height="21" rx="2" fill="{A}">'
             f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" '
             f'repeatCount="indefinite"/></rect>')
    p.append(T(972, 39, "▌", 13, t, color=SUB, anchor="end", opacity=0.5))
    return S(W, H, "\n".join(p))


def divider(t, c):
    W, H = 1000, 26
    A, LINE = t["accent"], t["line"]
    p = [
        f'<line x1="8" y1="13" x2="468" y2="13" stroke="{LINE}" stroke-width="1"/>',
        f'<line x1="532" y1="13" x2="992" y2="13" stroke="{LINE}" stroke-width="1"/>',
        f'<path d="M500 4 L509 13 L500 22 L491 13 Z" fill="{A}" opacity="0.75"/>',
        f'<circle cx="8" cy="13" r="2.6" fill="{A}">'
        f'<animate attributeName="cx" values="8;992" dur="4.5s" '
        f'repeatCount="indefinite"/></circle>',
    ]
    return S(W, H, "\n".join(p))


def header(t, sec):
    W, H = 1000, 74
    A, INK, SUB, LINE = t["accent"], t["ink"], t["sub"], t["line"]
    title, en, no = sec["title"], sec["en"], sec["no"]
    total = len(CFG["sections"])
    p = [R(2, 20, 5, 36, 2, A)]
    p.append(T(22, 47, title, 26, t, color=INK, weight=700))
    en_x = 26 + width_of(title, 26) + 18
    p.append(T(en_x, 46, en, 11, t, color=A, weight=600, mono=True, spacing=2.2))
    p.append(T(994, 46, f"{no} / {total:02d}", 12, t, color=SUB, mono=True, anchor="end"))
    p.append(f'<path d="M922 40 L928 46 L922 52 L916 46 Z" fill="{A}" opacity="0.45"/>')
    p.append(f'<line x1="2" y1="68" x2="998" y2="68" stroke="{LINE}" stroke-width="1"/>')
    return S(W, H, "\n".join(p))


def terminal(t, c):
    W, H = 1000, 252
    A, INK, SUB, LINE, G = t["accent"], t["ink"], t["sub"], t["line"], t["green"]
    p = glass_bg(t, W, H, 16)
    p += glass_card(t, 16, 14, 968, 224, 12)
    for i, col in enumerate(["#E06C5B", "#E0B45B", "#6DB37A"]):
        p.append(f'<circle cx="{40 + i*20}" cy="40" r="6" fill="{col}" opacity="0.85"/>')
    p.append(T(500, 45, f'~/whoami — {c["username"]}', 12, t, color=SUB, mono=True, anchor="middle"))
    p.append(f'<line x1="16" y1="62" x2="984" y2="62" stroke="{LINE}" stroke-width="1"/>')
    y = 96
    for i, item in enumerate(c["terminal_lines"]):
        p.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" '
                 f'dur="0.7s" begin="{i*0.35}s" fill="freeze"/>')
        p.append(T(42, y, item["prompt"], 14, t, color=A, mono=True))
        p.append(T(42, y + 22, "↳  " + item["out"], 14, t, color=INK, mono=True))
        p.append('</g>')
        y += 50
    p.append(pulse(900, 220, 4, G, 0, "2.2s"))
    p.append(T(958, 224, "online", 11, t, color=G, mono=True, anchor="end"))
    return S(W, H, "\n".join(p))


def arch(t, c):
    W, H = 1000, 196
    A, INK, SUB, LINE = t["accent"], t["ink"], t["sub"], t["line"]
    p = glass_bg(t, W, H, 16)
    p.append(T(28, 32, "SYSTEM LAYERS", 12, t, color=A, weight=600, mono=True, spacing=2))
    p.append(T(972, 32, "自入口到基础设施", 12, t, color=SUB, anchor="end"))
    for i, l in enumerate(c["layers"]):
        y = 48 + i * 28
        p.append(R(28, y, 944, 24, 5, t["card2"]))
        p.append(f'<rect x="28" y="{y}" width="4" height="24" rx="2" fill="{l["color"]}">'
                 f'<animate attributeName="opacity" values="0.45;1;0.45" dur="3s" '
                 f'begin="{i*0.28:.2f}s" repeatCount="indefinite"/></rect>')
        p.append(T(44, y + 16, l["name"], 12, t, color=INK, weight=700, mono=True))
        p.append(f'<line x1="252" y1="{y+5}" x2="252" y2="{y+19}" '
                 f'stroke="{LINE}" stroke-width="1"/>')
        p.append(T(268, y + 16, l["tech"], 12, t, color=SUB, mono=True))
        p.append(T(962, y + 16, f"L0{i+1}", 10, t, color=A, mono=True,
                   anchor="end", opacity=0.65))
    return S(W, H, "\n".join(p))


def project(t, p_, idx):
    W, H = 1000, 150
    A, INK, SUB, LINE = t["accent"], t["ink"], t["sub"], t["line"]
    p = glass_bg(t, W, H, 16)
    p.append(R(20, 22, 4, 106, 2, A))
    p.append(T(962, 66, f"{idx:02d}", 46, t, color=A, weight=800, mono=True,
               anchor="end", opacity=0.16))
    p.append(T(44, 50, p_["name"], 24, t, color=INK, weight=700))
    p.append(T(45, 72, p_["en"], 11, t, color=A, weight=600, mono=True, spacing=1.6))
    p.append(T(44, 102, clip(p_["desc"]), 14, t, color=SUB))
    x = 44
    for tag in p_["tech"]:
        s, w = chip(x, 114, tag, t, 11)
        p.append(s)
        x += w + 9
    p.append(T(968, 44, "↗", 20, t, color=A, anchor="end"))
    return S(W, H, "\n".join(p))


def stats(t, c):
    """Bento 运行视图：左侧工程指标 + 右侧真实仓库矩阵与系统状态。"""
    W, H = 1000, 248
    A, INK, SUB, LINE, G = (
        t["accent"], t["ink"], t["sub"], t["line"], t["green"]
    )
    tel = c["telemetry"]
    p = glass_bg(t, W, H, 16, mesh=True, mid="mesh2")
    p.append('<defs><clipPath id="statclip"><rect x="1" y="1" width="998" '
             'height="246" rx="16"/></clipPath></defs>')
    p.append(beam_defs(t, "statbeam", "0.10"))
    p.append(f'<g clip-path="url(#statclip)">'
             f'<rect x="-340" y="0" width="340" height="{H}" fill="url(#statbeam)">'
             f'<animate attributeName="x" values="-340;{W+60}" dur="10s" '
             f'repeatCount="indefinite"/></rect></g>')

    # 左：工程指标 2x2
    p += glass_card(t, 20, 20, 470, 208, 14)
    p.append(T(40, 46, "ENGINEERING SURFACE", 11, t, color=A, weight=600, mono=True, spacing=1.6))
    p.append(f'<line x1="40" y1="56" x2="470" y2="56" stroke="{LINE}" stroke-width="1"/>')
    for i, st in enumerate(c["stats"]):
        x = 40 + (i % 2) * 222
        y = 88 + (i // 2) * 76
        p.append(T(x, y, st["label"], 10, t, color=A, mono=True, spacing=1))
        p.append(T(x, y + 30, st["value"], 22, t, color=INK, weight=700, mono=True))
        p.append(T(x, y + 50, st["note"], 11, t, color=SUB))

    # 右上：仓库矩阵 + 语言分布
    p += glass_card(t, 502, 20, 478, 100, 14)
    p.append(T(522, 44, "REPOSITORY MATRIX", 11, t, color=A, weight=600, mono=True, spacing=1.6))
    p.append(T(522, 84, f'{tel["repos"]:02d}', 34, t, color=INK, weight=800, mono=True))
    p.append(T(578, 82, "PUBLIC REPOS", 11, t, color=SUB, mono=True))
    bx, by, bw = 522, 96, 438
    p.append(R(bx, by, bw, 7, 3, t["chip"]))
    x = bx
    total = sum(l["count"] for l in tel["languages"]) or 1
    for l in tel["languages"]:
        w = bw * l["count"] / total
        p.append(f'<rect x="{x:.1f}" y="{by}" width="{w+0.5:.1f}" height="7" '
                 f'fill="{l["color"]}"/>')
        x += w
    legend = "  ·  ".join(f'{l["name"]} {l["count"]}' for l in tel["languages"])
    p.append(T(522, 116, legend, 10, t, color=SUB, mono=True))

    # 右下：系统状态脉冲 + 许可
    p += glass_card(t, 502, 132, 478, 96, 14)
    p.append(T(522, 156, "SYSTEM STATUS", 11, t, color=A, weight=600, mono=True, spacing=1.6))
    for i, name in enumerate(tel["core_systems"]):
        sx = 522 + i * 158
        p.append(pulse(sx + 6, 181, 4, G, round(i * 0.5, 1), "2.4s"))
        p.append(T(sx + 18, 185, name, 10, t, color=INK, mono=True))
    p.append(f'<line x1="522" y1="198" x2="960" y2="198" stroke="{LINE}" stroke-width="1"/>')
    p.append(T(522, 218, "  ·  ".join(tel["licenses"]), 10, t, color=SUB, mono=True))
    p.append(T(960, 218, f'{tel["topics"]} TOPICS', 10, t, color=A, mono=True, anchor="end"))
    return S(W, H, "\n".join(p))


def flow(t, c):
    W, H = 1000, 214
    A, INK, SUB, LINE = t["accent"], t["ink"], t["sub"], t["line"]
    p = glass_bg(t, W, H, 16)
    p.append(T(28, 30, "REQUEST PATH", 12, t, color=A, weight=600, mono=True, spacing=2))
    p.append(T(972, 30, "一次受治理的工具调用如何穿过系统", 11, t, color=SUB, anchor="end"))
    nodes = [
        ("01", "INGRESS", "Go / FastAPI"),
        ("02", "AGENT", "LangGraph planner"),
        ("03", "RETRIEVAL", "Hybrid RAG / Graph"),
        ("04", "MCP GATE", "RBAC · execute gate"),
        ("05", "INFRA", "K8s · Docker · SSH"),
    ]
    bw, gap, x0, y0, bh = 168, 26, 28, 56, 76
    for i, (num, name, sub) in enumerate(nodes):
        x = x0 + i * (bw + gap)
        p.append(R(x, y0, bw, bh, 10, t["card2"], stroke=LINE))
        p.append(f'<rect x="{x+10}" y="{y0}" width="{bw-20}" height="2" rx="1" '
                 f'fill="{A}"><animate attributeName="opacity" values="0.25;1;0.25" '
                 f'dur="3s" begin="{i*0.5:.1f}s" repeatCount="indefinite"/></rect>')
        p.append(T(x + 14, y0 + 22, num, 10, t, color=A, mono=True, weight=700))
        p.append(T(x + 14, y0 + 46, name, 13, t, color=INK, weight=700, mono=True))
        p.append(T(x + 14, y0 + 64, sub, 10, t, color=SUB))
        if i < len(nodes) - 1:
            ax = x + bw + gap / 2
            p.append(T(ax, y0 + 43, "→", 14, t, color=A, anchor="middle"))
    p.append(f'<line x1="28" y1="162" x2="972" y2="162" stroke="{LINE}" '
             f'stroke-width="1" stroke-dasharray="4 6"/>')
    p.append(f'<circle cx="28" cy="94" r="4" fill="{A}" opacity="0.9">'
             f'<animate attributeName="cx" values="28;972" dur="4.5s" '
             f'repeatCount="indefinite"/></circle>')
    p.append(f'<circle cx="28" cy="162" r="3" fill="{A}"/>')
    p.append(f'<circle cx="972" cy="162" r="3" fill="{A}"/>')
    p.append(T(500, 190, "←  traces · metrics · audit logs  /  全链路可观测回路  →",
               12, t, color=A, mono=True, anchor="middle"))
    return S(W, H, "\n".join(p))


def focus(t, c):
    W, H = 1000, 176
    A, INK, SUB, LINE = t["accent"], t["ink"], t["sub"], t["line"]
    p = glass_bg(t, W, H, 16)
    for i, f in enumerate(c["principles"]):
        x = 20 + i * 326
        p += glass_card(t, x, 16, 308, 144, 12)
        p.append(T(x + 288, 52, f["tag"], 26, t, color=A, weight=800, mono=True,
                   anchor="end", opacity=0.30))
        p.append(T(x + 20, 76, f["title"], 18, t, color=INK, weight=700))
        p.append(T(x + 20, 98, f["en"], 10, t, color=A, mono=True, spacing=1.4))
        p.append(T(x + 20, 128, clip(f["desc"], 22), 12, t, color=SUB))
        p.append(R(x + 20, 142, 42, 3, 1, A))
    return S(W, H, "\n".join(p))


def links(t, c):
    W, H = 1000, 152
    A, INK, SUB, LINE = t["accent"], t["ink"], t["sub"], t["line"]
    p = glass_bg(t, W, H, 16)
    for i, l in enumerate(c["links"]):
        x = 20 + i * 245
        p += glass_card(t, x, 16, 230, 120, 12)
        p.append(f'<circle cx="{x+36}" cy="52" r="18" fill="{t["chip"]}"/>')
        p.append(T(x + 36, 58, l["icon"], 12, t, color=A, weight=700,
                   mono=True, anchor="middle"))
        p.append(T(x + 20, 92, l["label"], 12, t, color=SUB))
        p.append(T(x + 20, 116, clip(l["value"], 24), 11, t, color=INK, mono=True))
    return S(W, H, "\n".join(p))


# --------------------------------------------------------------------------
# 写出全部 SVG
# --------------------------------------------------------------------------

def emit(name, theme_key, content):
    (ASSETS / f"{name}-{theme_key}.svg").write_text(content, encoding="utf-8")


def build_assets():
    for old in ASSETS.glob("*.svg"):
        old.unlink()
    n = 0
    for key, t in THEMES.items():
        emit("banner", key, banner(t, CFG)); n += 1
        emit("typing", key, typing(t, CFG)); n += 1
        emit("divider", key, divider(t, CFG)); n += 1
        for sec in CFG["sections"]:
            emit(f'hdr-{sec["key"]}', key, header(t, sec)); n += 1
        emit("terminal", key, terminal(t, CFG)); n += 1
        emit("arch", key, arch(t, CFG)); n += 1
        for i, pr in enumerate(CFG["projects"], 1):
            emit(f'proj-{pr["slug"]}', key, project(t, pr, i)); n += 1
        emit("stats", key, stats(t, CFG)); n += 1
        emit("flow", key, flow(t, CFG)); n += 1
        emit("focus", key, focus(t, CFG)); n += 1
        emit("links", key, links(t, CFG)); n += 1
    return n


# --------------------------------------------------------------------------
# README
# --------------------------------------------------------------------------

def pic(name, alt, width="100%"):
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
        f'  <img src="assets/{name}-dark.svg" alt="{esc(alt)}" width="{width}">\n'
        "</picture>"
    )


def badge(b, style="flat-square"):
    label = b["label"]
    url = f'https://img.shields.io/badge/{label}-{b["color"]}?style={style}'
    if b.get("logo"):
        url += f'&logo={b["logo"]}&logoColor={b.get("logoColor", "white")}'
    return f'![{label}]({url})'


def top_langs(u):
    return ("https://github-readme-stats.vercel.app/api/top-langs/?username=" + u
            + "&hide_title=true&hide_border=true&layout=compact&theme=graywhite&locale=cn")


def build_readme():
    u = CFG['username']
    L = []
    a = L.append
    a('<div align="center">\n')
    a(pic('banner', f'Zhifeng Jin · @{u}'))
    a('\n**AI Agent · AIOps · Platform Engineering**\n')
    a('让知识可检索，让工具可治理，让系统可观测。\n')
    for b in CFG['top_badges']:
        a(f'![{b["label"]}](https://img.shields.io/badge/{b["label"]}-F0EADA?style=for-the-badge&logo={b["logo"]}&logoColor={b["logoColor"]})')
    a('\n[👋 关于我](#about) · [🚀 代表项目](#projects) · [🛠️ 技术能力](#stack) · [📚 技术笔记](#notes) · [🤝 交流合作](#contact)\n')
    a('</div>\n')
    a('<a id="about"></a>\n\n## 👋 关于我 · About\n')
    for line in CFG['bio']: a('- ' + line)
    a('\n> ✨ **我的工程兴趣**：把文档、模型、工具和基础设施连接起来，做出能解释、能部署、能继续演进的系统。\n')
    a('### 🧭 从哪里开始看？\n')
    a('- **想了解 AI 应用开发** → 从企业知识库 Agent 入手，看连接器、Hybrid RAG、知识图谱与工作流。')
    a('- **想了解 AIOps / SRE** → 从故障诊断 Agent 入手，看 Kubernetes 现场证据、Runbook 与 Trace。')
    a('- **想了解 MCP / 工具工程** → 从 DevOps MCP Server 入手，看工具目录、执行门与审计。\n')
    a('<a id="projects"></a>\n\n## 🚀 代表项目 · Selected Work\n')
    a('以 **知识自动化 → 故障诊断 → 工具治理** 为主线，下面展开项目场景、系统能力与值得深入阅读的工程设计。\n')
    for i, (pr, detail) in enumerate(zip(CFG['projects'], CFG['project_details'])):
        if i == 3:
            a('## 🧩 更多开源实践 · Engineering Portfolio\n')
            a('补充展示模型网关、全栈业务与网络认证三个方向。以下介绍仓库能力与实践主题；具体实现与许可说明以各仓库为准。\n')
        a(f'### {detail["icon"]} {i+1:02d} · [{pr["name"]}]({pr["url"]})\n')
        a(f'**{detail["tag"]}** · ' + ' / '.join(f'`{x}`' for x in pr['tech']) + '\n')
        if i < 3:
            a(f'<a href="{pr["url"]}">\n' + pic('proj-'+pr['slug'], pr['name']) + '\n</a>\n')
        a(detail['intro'] + '\n')
        for line in detail['highlights']: a('- ' + line)
        a('\n> 🔧 ' + detail['focus'] + '\n')
        links=[('💻 源码',pr['url'])]+detail['links']
        a(' · '.join(f'[{label}]({url})' for label,url in links)+'\n')
        if i < 2:
            repo=pr['url'].rsplit('/',1)[-1]
            a('<details>\n<summary>🖼️ 展开项目演示入口</summary>\n')
            a(f'[![{pr["name"]} 演示封面](https://raw.githubusercontent.com/{u}/{repo}/main/docs/videos/cover.png)](https://{u}.github.io/{repo}/)\n')
            a('点击封面前往演示页，项目架构、部署方法与功能边界见仓库文档。\n\n</details>\n')
        a('---\n')
    a('<a id="stack"></a>\n\n## 🛠️ 技术能力 · Engineering Stack\n')
    a('### 🧠 AI / Agent / Retrieval\n')
    a('- **Agent 编排**：LangGraph、Planner、Tool Calling、Memory、MCP 工具发现与调用。')
    a('- **知识工程**：文档接入、分块、Embedding、向量与全文混合检索、知识图谱、Rerank 与引用回答。')
    a('- **工作流**：DAG、审批节点、Webhook / Schedule 触发与执行生命周期。\n')
    a('### ⚙️ Backend / Data / Product\n')
    a('- **后端与 API**：Python、FastAPI、SQLAlchemy async、Alembic；Go 服务与网关实践。')
    a('- **数据与缓存**：PostgreSQL、Redis、ChromaDB；关注租户约束、数据模型与异步任务协作。')
    a('- **控制台与全栈**：React / Vue 3、TypeScript、Vite、Tailwind；将业务接口与可操作界面连接起来。\n')
    a('### ☁️ Infrastructure / Security / Delivery\n')
    a('- **基础设施**：Linux、Docker、Kubernetes、SSH，以及 LDAP / FreeRADIUS / UniFi 集成实践。')
    a('- **权限与治理**：JWT、RBAC、多租户隔离、工具风险分级、执行保护与审计日志。')
    a('- **交付与观测**：Docker Compose、Kubernetes manifests、Helm、GitHub Actions、OpenTelemetry、Prometheus 与 Grafana。\n')
    a(pic('arch','从 API 入口到 Agent、检索、工具治理与基础设施的分层'))
    a('\n### 🔗 把这些技术放进一条链路\n')
    a(pic('flow','请求规划、工具调用、检索与响应的示意链路'))
    a('\n*上图为项目能力的组合示意，各项目实际集成范围见对应仓库。*\n')
    a('<a id="notes"></a>\n\n## 📚 技术笔记与阅读入口 · Build in Public\n')
    a('将项目文档作为技术笔记入口，沿着一个问题读到设计与实现：\n')
    base=f'https://github.com/{u}'
    for title,body,url in [
        ('🔍 企业知识如何进入 RAG？','从文档同步、智能分块读到混合检索、图谱与引用回答。',f'{base}/enterprise-ai-agent-platform#rag-pipeline'),
        ('🧩 Agent 如何执行多步任务？','从 Planner、工具注册与 Memory 读到工作流编排。',f'{base}/enterprise-ai-agent-platform#核心能力'),
        ('🩺 故障诊断如何组织证据？','从 LangGraph Agent 循环读到 Kubernetes 工具、Runbook 与 Incident Report。',f'{base}/enterprise-ai-sre-platform#features'),
        ('🔐 MCP 如何划分读与写？','从工具目录的风险 / 权限读到默认只读与执行保护。',f'{base}/enterprise-devops-mcp-server#mcp-tool-catalog'),
        ('📦 系统如何交付？','从环境配置与 Compose 读到 Kubernetes 和 Helm 部署入口。',f'{base}/enterprise-ai-agent-platform#部署架构')]:
        a(f'- **[{title}]({url})** — {body}')
    a('\n## 🌱 持续探索 · What’s Next\n')
    a('- **检索质量**：如何组织评测样本、定位召回与排序问题，让回答更有依据。')
    a('- **执行可靠性**：如何处理超时、重试、部分失败与长任务状态，让 Agent 任务更可控。')
    a('- **可观测性**：如何把模型决策、工具调用、耗时与成本放入同一个分析上下文。')
    a('- **平台体验**：如何降低系统配置、知识接入与工具集成的使用门槛。\n')
    a('## 💡 写代码时在意的事\n')
    a('- 🛡️ **边界明确**：权限、租户、数据访问与执行范围应在接口和实现中看得见。')
    a('- 🔎 **过程可查**：错误要能定位，工具调用要有记录，结论要有证据。')
    a('- 📦 **交付完整**：代码之外，补上配置模板、启动方式、部署入口与技术文档。')
    a('- 🧱 **持续演进**：先理清模块职责，再扩展能力；让后续阅读和修改都有路径。\n')
    a('<a id="contact"></a>\n\n## 🤝 交流与合作 · Let’s Connect\n')
    a('欢迎围绕 **Agent 工程、RAG、MCP、Kubernetes 诊断、平台工程** 交流。发现问题或有改进建议，可以在对应仓库提交 Issue / PR。\n')
    a(f'[🐙 GitHub](https://github.com/{u}) · [📂 所有仓库](https://github.com/{u}?tab=repositories) · [🧠 Agent Platform]({base}/enterprise-ai-agent-platform) · [🛡️ MCP Server]({base}/enterprise-devops-mcp-server)\n')
    a('---\n\n<div align="center">\n\n**'+CFG['closing']+'**\n\n如果某个项目对你有帮助，欢迎留下一个 ⭐\n\n</div>\n')
    (ROOT/'README.md').write_text('\n'.join(L)+'\n',encoding='utf-8')


def build_preview():
    import markdown
    source=(ROOT/'README.md').read_text(encoding='utf-8').replace('<div align="center">', '<div align="center" markdown="1">').replace('<details>', '<details markdown="1">')
    content=markdown.markdown(source,extensions=['extra','sane_lists','md_in_html'])
    page='''<!doctype html><html lang="zh-CN" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Zhifeng Jin · Profile v4</title><style>
:root{--bg:#fff;--fg:#1f2328;--sub:#59636e;--line:#d1d9e0;--card:#f6f8fa;--link:#0969da}html[data-theme=dark]{--bg:#0d1117;--fg:#e6edf3;--sub:#9198a1;--line:#30363d;--card:#161b22;--link:#58a6ff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}.toolbar{position:sticky;top:0;background:var(--card);border-bottom:1px solid var(--line);padding:10px 24px;z-index:2;display:flex;justify-content:space-between;gap:12px}button{border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);padding:5px 12px;cursor:pointer}.readme{max-width:980px;margin:28px auto;padding:28px;border:1px solid var(--line);border-radius:6px}img{max-width:100%;vertical-align:middle}picture img{display:block;width:100%;height:auto}h2{margin-top:32px;padding-bottom:8px;border-bottom:1px solid var(--line);font-size:24px}h3{font-size:20px;margin:26px 0 14px}a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}li{margin:8px 0}p{margin:14px 0}code{background:var(--card);border-radius:5px;padding:2px 5px;font:85% Consolas,monospace}blockquote{margin:18px 0;border-left:3px solid #b29a58;padding:2px 16px;color:var(--sub);background:var(--card)}hr{border:0;border-top:1px solid var(--line);margin:30px 0}summary{cursor:pointer;color:var(--sub)}details{border:1px solid var(--line);border-radius:8px;padding:12px 16px}details[open] img{margin-top:16px}@media(max-width:650px){.readme{margin:0;border:0;padding:18px;font-size:15px}.toolbar{font-size:12px}}
</style></head><body><div class="toolbar"><span>Profile v4 · GitHub README 内容预览</span><span><button onclick="setTheme('light')">浅色</button> <button onclick="setTheme('dark')">深色</button></span></div><article class="readme">__BODY__</article><script>function setTheme(t){document.documentElement.dataset.theme=t;document.querySelectorAll('picture').forEach(p=>{let i=p.querySelector('img');if(!i.dataset.light)i.dataset.light=i.src.replace('-dark.svg','-light.svg');i.src=i.dataset.light.replace('-light.svg','-'+t+'.svg');p.querySelectorAll('source').forEach(s=>s.media='not all')})}</script></body></html>'''
    (ROOT/'preview.html').write_text(page.replace('__BODY__',content),encoding='utf-8')


def main():
    n = build_assets()
    build_readme()
    build_preview()
    print(f"OK: {n} animated SVG + README.md + preview.html")
    print(f"assets -> {ASSETS}")


if __name__ == "__main__":
    main()
