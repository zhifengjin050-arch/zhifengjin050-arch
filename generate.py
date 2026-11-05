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
        card="#FAF8F3", card2="#F7F4EE", ink="#302A1C", sub="#71674F",
        accent="#96781A", accent2="#A8862A", line="#DFD8C8", chip="#F0EBDF",
        green="#628571", glow="#FFFFFF",
    ),
    "dark": dict(
        card="#17140D", card2="#211C13", ink="#F5EEDB", sub="#B8AC90",
        accent="#D6B85C", accent2="#E7CD86", line="#51452B", chip="#30291A",
        green="#8FAE92", glow="#FFE9A8",
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
    W,H=1000,340
    A=t['accent']; B=t['accent2']
    p=[bg(t,W,H,20),f'<defs><linearGradient id="aurora"><stop stop-color="{A}"/><stop offset="1" stop-color="{B}"/></linearGradient><radialGradient id="nebula"><stop stop-color="{A}" stop-opacity=".22"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient></defs>']
    p.append('<style>@media(prefers-reduced-motion:reduce){.orbit{display:none}}</style>')
    p.append('<rect x="1" y="1" width="998" height="338" rx="20" fill="none" stroke="url(#aurora)" opacity=".5"/>')
    p.append('<path d="M32 1 H968" stroke="url(#aurora)" stroke-width="3"/>')
    p.append('<circle cx="800" cy="160" r="170" fill="url(#nebula)"/>')
    for y in range(35,330,28):
        for x in range(640,975,28):
            p.append(f'<circle cx="{x}" cy="{y}" r=".8" fill="{A}" opacity=".2"/>')
    p.append(T(42,44,'ZF / ENGINEERING NOTEBOOK',12,t,color=A,mono=True,spacing=2))
    p.append(T(42,112,'ZHIFENG JIN',55,t,weight=800))
    p.append(T(44,147,'AI AGENT  /  AIOPS  /  PLATFORM',15,t,color=B,mono=True,spacing=1))
    p.append(T(44,191,'从知识到行动，从代码到系统。',24,t,weight=600))
    p.append(T(44,222,'Build with context. Execute with boundaries.',14,t,color=t['sub'],mono=True))
    x=44
    for label in ['Hybrid RAG','MCP Tools','Cloud Native']:
        part,w=chip(x,246,label,t,12);p.append(part);x+=w+10
    p.append(T(44,315,'@'+c['username'],12,t,color=t['sub'],mono=True))
    cx,cy=810,156
    for r in [57,90,123]:
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*.62}" transform="rotate(-28 {cx} {cy})" fill="none" stroke="url(#aurora)" opacity=".5"/>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="39" fill="{t["chip"]}" stroke="{A}"/>')
    p.append(T(cx,cy+9,'ZF',28,t,color=A,weight=800,mono=True,anchor='middle'))
    for i in range(3):
        p.append(f'<g class="orbit"><animateTransform attributeName="transform" type="rotate" from="{i*120} {cx} {cy}" to="{i*120+360} {cx} {cy}" dur="{18+i*6}s" repeatCount="indefinite"/><circle cx="{cx+90}" cy="{cy}" r="4" fill="{B}"/></g>')
    for x,y,label in [(700,55,'RETRIEVE'),(902,220,'REASON'),(765,285,'EXECUTE')]:
        p.append(T(x,y,label,11,t,color=A,mono=True,anchor='middle',spacing=1.5))
    return S(W,H,'\n'.join(p))


def capability_map(t):
    p=[bg(t,1000,148,16)]
    items=[('01','KNOWLEDGE','文档接入 · 混合检索 · 知识图谱'),('02','DIAGNOSIS','现场证据 · Runbook · Agent Trace'),('03','GOVERNANCE','MCP 工具 · 执行保护 · 审计')]
    for i,(n,title,desc) in enumerate(items):
        x=26+i*328
        p.append(T(x,34,n,12,t,color=t['accent'],mono=True))
        p.append(T(x,72,title,22,t,weight=700,mono=True))
        p.append(T(x,106,desc,13,t,color=t['sub']))
        p.append(f'<line x1="{x}" y1="127" x2="{x+285}" y2="127" stroke="{t["accent"]}" opacity=".4"/>')
    return S(1000,148,'\n'.join(p))


def typing(t, c):
    lines=['构建知识库 Agent，让企业知识连接实际任务。','探索 AIOps，让故障诊断有证据、有过程。','打磨 MCP 工具，让每次执行有边界、可追踪。']
    p=[bg(t,1000,92,16),T(28,56,'❯',24,t,color=t['accent'],weight=700)]
    p.append('<style>@media(prefers-reduced-motion:reduce){.cycle{display:none}.fallback{display:block}}</style>')
    p.append('<g class="fallback" style="display:none">'+T(64,56,lines[0],22,t)+'</g>')
    for i,line in enumerate(lines):
        begin=i/3; end=(i+1)/3
        times=[0,begin,begin+.08,end-.03,end,1]
        vals=['0','0','850','850','0','0']
        if i==0: times=times[1:];vals=vals[1:]
        if i==2: times=times[:-1];vals=vals[:-1]
        p.append(f'<defs><clipPath id="cycle{i}"><rect x="60" y="15" width="850" height="62"><animate attributeName="width" values="'+ ';'.join(vals)+'" keyTimes="'+';'.join(str(round(x,4)) for x in times)+'" dur="15s" repeatCount="indefinite"/></rect></clipPath></defs>')
        p.append(f'<g class="cycle" clip-path="url(#cycle{i})">'+T(64,56,line,22,t)+'</g>')
    p.append(f'<rect x="940" y="32" width="3" height="28" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')
    return S(1000,92,'\n'.join(p))


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
    A=t['accent']
    icons={
      'about':'M24 26a6 6 0 1 0 12 0a6 6 0 1 0-12 0 M20 46v-4a10 10 0 0 1 20 0v4',
      'stack':'M17 27l13-7 13 7-13 7z M17 34l13 7 13-7 M17 41l13 7 13-7',
      'projects':'M18 25l12-6 12 6v18l-12 6-12-6z M18 25l12 7 12-7 M30 32v17',
      'portfolio':'M18 24h24v23H18z M24 18h12v6 M18 32h24 M27 30v5h6v-5',
      'notes':'M18 21h10l2 3 2-3h10v26H32l-2 2-2-2H18z M30 25v24',
      'focus':'M44 34a14 14 0 1 1-14-14 M39 34a9 9 0 1 1-9-9 M30 34l14-14 M36 20h8v8',
      'principles':'M30 19l13 5v11c0 7-7 12-13 15-6-3-13-8-13-15V24z M23 34l5 5 9-10',
      'links':'M17 23h26v20H29l-8 7v-7h-4z M23 30h14 M23 36h9'
    }
    p=[f'<rect x="1" y="9" width="58" height="58" rx="14" fill="{t["card2"]}" stroke="{t["line"]}"/>',f'<path d="{icons.get(sec["key"],icons["stack"])}" fill="none" stroke="{A}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>']
    stops=['#765018','#B68A26','#8B641A'] if t['card']=='#FAF8F3' else ['#C59938','#F6D98D','#D2AE50']
    p.append('<defs><linearGradient id="titleGold" x1="0%" y1="0%" x2="100%" y2="25%">'+''.join(f'<stop offset="{offset}" stop-color="{color}"/>' for offset,color in zip(['0%','48%','100%'],stops))+'</linearGradient></defs>')
    p.append(T(80,39,sec['title'],27,t,color='url(#titleGold)',weight=700))
    p.append(T(82,61,sec['en'],10,t,color='url(#titleGold)',mono=True,spacing=3))
    p.append(f'<defs><linearGradient id="rule"><stop stop-color="{A}"/><stop offset="1" stop-color="{t["line"]}" stop-opacity=".2"/></linearGradient></defs><path d="M1 83H999" stroke="url(#rule)"/>')
    return S(1000,88,'\n'.join(p))



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


def language_panel(t):
    data=json.loads((ROOT/'language-data.json').read_text(encoding='utf-8'))
    totals={}
    for repo in data['repositories'].values():
        for lang,size in repo.items(): totals[lang]=totals.get(lang,0)+size
    ranked=sorted(totals.items(),key=lambda x:-x[1]); total=sum(totals.values())
    ranked=ranked[:5]+[('Other',sum(v for _,v in ranked[5:]))]
    colors=[t['accent'],t['accent2'],'#4BAF9C','#BC82CD','#DBA25D','#8194B3']
    p=[bg(t,1000,260,18),'<style>@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}@keyframes orbit{to{transform:rotate(360deg)}}.bar{transform-box:fill-box;transform-origin:left;animation:grow 1.8s ease-out both}.orbit{transform-origin:150px 125px;animation:orbit 28s linear infinite}@media(prefers-reduced-motion:reduce){.bar,.orbit{animation:none!important}}</style>']
    p.append(T(310,36,'CODE / LANGUAGE COMPOSITION',13,t,color=t['accent'],mono=True,weight=600))
    p.append(T(310,61,'6 个展示仓库 · GitHub 代码字节统计',13,t,color=t['sub']))
    offset=0
    for i,((lang,size),color) in enumerate(zip(ranked,colors)):
        pct=size/total*100
        p.append(f'<circle cx="150" cy="125" r="76" fill="none" stroke="{color}" stroke-width="19" pathLength="100" stroke-dasharray="{pct-.35:.4f} {100-pct+.35:.4f}" stroke-dashoffset="{-offset:.4f}" transform="rotate(-90 150 125)"/>')
        x=310+(i%2)*335;y=103+(i//2)*51
        p.append(R(x,y-10,8,8,2,color))
        p.append(T(x+18,y,lang,14,t))
        p.append(T(x+290,y,f'{pct:.1f}%',13,t,color=t['sub'],anchor='end',mono=True))
        p.append(R(x,y+12,290,3,1,t['line']))
        p.append(f'<g class="bar" style="animation-delay:{i*.12}s">'+R(x,y+12,290*pct/100,3,1,color)+'</g>')
        offset+=pct
    p.append(f'<circle class="orbit" cx="150" cy="125" r="94" fill="none" stroke="{t["accent2"]}" stroke-width="1.5" stroke-dasharray="26 564" opacity=".7"/>')
    p.append(T(150,124,f'{ranked[0][1]/total*100:.0f}%',34,t,weight=800,anchor='middle',mono=True))
    p.append(T(150,150,ranked[0][0],15,t,color=t['sub'],anchor='middle'))
    p.append(T(310,243,'快照 '+data['date']+' · 代码占比，不代表熟练度',11,t,color=t['sub']))
    return S(1000,260,'\n'.join(p))


def project(t, p_, idx):
    W, H = 1000, 150
    A, INK, SUB, LINE = t["accent"], t["ink"], t["sub"], t["line"]
    p = glass_bg(t, W, H, 16)
    p.append('<defs><clipPath id="cardclip"><rect x="1" y="1" width="998" height="148" rx="16"/></clipPath><linearGradient id="cardsheen"><stop stop-color="'+A+'" stop-opacity="0"/><stop offset=".5" stop-color="'+A+'" stop-opacity=".09"/><stop offset="1" stop-color="'+A+'" stop-opacity="0"/></linearGradient></defs>')
    p.append('<style>@keyframes sweep{0%,15%{transform:translateX(-350px)}65%,100%{transform:translateX(1100px)}}@keyframes trace{to{stroke-dashoffset:-2300}}.sheen{animation:sweep 10s ease-in-out infinite}.edge{animation:trace 24s linear infinite}@media(prefers-reduced-motion:reduce){.sheen{display:none}.edge{animation:none}}</style>')
    p.append('<g clip-path="url(#cardclip)"><rect class="sheen" x="0" y="0" width="280" height="150" fill="url(#cardsheen)"/></g>')
    p.append(f'<rect class="edge" x="1" y="1" width="998" height="148" rx="16" fill="none" stroke="{A}" stroke-width="1.3" stroke-dasharray="95 2205" opacity=".55"/>')
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


def tech_badge_grid():
    from urllib.parse import quote
    rows=['<table width="100%">']
    for i,g in enumerate(CFG['badge_groups']):
        if i%2==0:rows.append('<tr>')
        rows.append('<td valign="top" width="50%"><h4>'+esc(g['title'])+'</h4><p>')
        for label,color,logo in g['items']:
            url='https://img.shields.io/badge/'+quote(label.replace('-', '--'),safe='')+'-'+color+'?style=flat-square'
            if logo:url+='&logo='+logo+'&logoColor=white'
            rows.append('<img alt="'+esc(label)+'" src="'+esc(url)+'" height="22"> ')
        rows.append('</p></td>')
        if i%2==1:rows.append('</tr>')
    rows.append('</table>\n')
    return '\n'.join(rows)


def portfolio_gallery(english=False):
    u=CFG['username']
    labels=['Knowledge Agent','SRE Diagnosis','MCP Tooling'] if english else ['知识库 Agent','SRE 故障诊断','MCP 工具治理']
    subs=['Documents → Retrieval → Workflow','Evidence → Runbooks → Reports','Tool schemas → Gates → Audit'] if english else ['文档接入 → 混合检索 → 工作流','现场证据 → 知识检索 → 故障报告','工具协议 → 执行保护 → 审计']
    parts=['<table width="100%"><tr>']
    for i,pr in enumerate(CFG['projects'][:3]):
        repo=pr['url'].rsplit('/',1)[-1]
        demo=f'https://{u}.github.io/{repo}/'
        img=f'https://raw.githubusercontent.com/{u}/{repo}/main/docs/videos/cover.png'
        source='Source' if english else '源码'
        watch='Watch demo' if english else '观看演示'
        parts.append(f'<td width="33%" valign="top"><h4>{i+1:02d} · {labels[i]}</h4><a href="{demo}"><img src="{img}" alt="{labels[i]} demo cover" width="100%"></a><p>{esc(subs[i])}</p><p><a href="{demo}">▶ {watch}</a> · <a href="{pr["url"]}">{source} ↗</a></p></td>')
    parts.append('</tr></table>\n')
    return '\n'.join(parts)


def quick_actions(english=False):
    u=CFG['username']
    labels=['Watch demos','Read architecture','Explore repositories'] if english else ['观看项目演示','阅读系统架构','浏览全部仓库']
    urls=[f'https://{u}.github.io/enterprise-ai-agent-platform/',f'https://github.com/{u}/enterprise-ai-agent-platform/blob/main/docs/images/system_architecture.md',f'https://github.com/{u}?tab=repositories']
    return '<p align="center">'+' &nbsp; '.join(f'<a href="{url}"><img src="assets/action-{i}-'+('en' if english else 'zh')+'.svg" alt="'+label+'" height="32"></a>' for i,(label,url) in enumerate(zip(labels,urls)))+'</p>\n'


def build_action_assets():
    for lang,labels in [('zh',['观看项目演示','阅读系统架构','浏览全部仓库']),('en',['Watch demos','Read architecture','Explore repositories'])]:
        for i,label in enumerate(labels):
            content=S(210,36,'<rect x=".5" y=".5" width="209" height="35" rx="8" fill="#F0EADA" stroke="#D5C28E"/>'+T(105,24,label,13,THEMES['light'],color='#806016',weight=600,anchor='middle'))
            (ASSETS/f'action-{i}-{lang}.svg').write_text(content,encoding='utf-8')


def section_heading(key, anchor=None):
    sec=next(x for x in CFG['sections'] if x['key']==key)
    prefix=f'<a id="{anchor}"></a>\n\n' if anchor else ''
    return prefix+'<h2>'+pic('hdr-'+key,sec['title']).replace('\n','')+'</h2>\n'


def build_readme():
    u = CFG['username']
    L = []
    a = L.append
    a(f'<p align="center"><strong>简体中文</strong> &nbsp;|&nbsp; <a href="https://github.com/{u}/{u}/blob/main/README_EN.md">English</a></p>\n')
    a('<div align="center">\n')
    a(pic('banner', f'Zhifeng Jin · @{u}'))
    a(pic('typing', '构建知识库 Agent、探索 AIOps、打磨 MCP 工具'))
    a('\n**AI Agent · AIOps · Platform Engineering**\n')
    a('让知识可检索，让工具可治理，让系统可观测。\n')
    for b in CFG['top_badges']:
        a(f'![{b["label"]}](https://img.shields.io/badge/{b["label"]}-F0EADA?style=for-the-badge&logo={b["logo"]}&logoColor={b["logoColor"]})')
    a('\n[👋 关于我](#about) · [🚀 代表项目](#projects) · [🛠️ 技术能力](#stack) · [📚 技术笔记](#notes) · [🤝 交流合作](#contact)\n')
    a('</div>\n')
    a(quick_actions())
    a('### 🎬 先看作品 · Project Preview\n')
    a(portfolio_gallery())
    a(section_heading('about','about'))
    for line in CFG['bio']: a('- ' + line)
    a('\n> ✨ **我的工程兴趣**：把文档、模型、工具和基础设施连接起来，做出能解释、能部署、能继续演进的系统。\n')
    a(pic('capability', '知识检索、故障诊断、工具治理：三个核心工程方向')+'\n')
    a('### 🧭 从哪里开始看？\n')
    a('- **想了解 AI 应用开发** → 从企业知识库 Agent 入手，看连接器、Hybrid RAG、知识图谱与工作流。')
    a('- **想了解 AIOps / SRE** → 从故障诊断 Agent 入手，看 Kubernetes 现场证据、Runbook 与 Trace。')
    a('- **想了解 MCP / 工具工程** → 从 DevOps MCP Server 入手，看工具目录、执行门与审计。\n')
    a(section_heading('stack','stack'))
    a(pic('languages', '六个展示仓库的真实代码语言占比')+'\n')
    a(tech_badge_grid())
    a('上列技术覆盖当前公开项目中的应用与集成实践，具体实现见各项目源码。\n')
    a('<details>\n<summary>📐 展开技术说明与系统架构</summary>\n')
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
    a('\n</details>\n')
    a(section_heading('projects','projects'))
    a('以 **知识自动化 → 故障诊断 → 工具治理** 为主线，下面展开项目场景、系统能力与值得深入阅读的工程设计。\n')
    for i, (pr, detail) in enumerate(zip(CFG['projects'], CFG['project_details'])):
        if i == 3:
            a(section_heading('portfolio'))
            a('补充展示模型网关、全栈业务与网络认证三个方向。以下介绍仓库能力与实践主题；具体实现与许可说明以各仓库为准。\n')
        a(f'### {detail["icon"]} {i+1:02d} · [{pr["name"]}]({pr["url"]})\n')
        a(f'**{detail["tag"]}** · ' + ' / '.join(f'`{x}`' for x in pr['tech']) + '\n')
        if i < 6:
            a(f'<a href="{pr["url"]}">\n' + pic('proj-'+pr['slug'], pr['name']) + '\n</a>\n')
        a(detail['intro'] + '\n')
        a('<details>\n<summary>🔬 展开技术实现与工程细节</summary>\n')
        for line in detail['highlights']: a('- ' + line)
        a('\n</details>\n')
        a('\n> 🔧 ' + detail['focus'] + '\n')
        links=[('💻 源码',pr['url'])]+detail['links']
        a(' · '.join(f'[{label}]({url})' for label,url in links)+'\n')
        a('---\n')
    a(section_heading('notes','notes'))
    a('将项目文档作为技术笔记入口，沿着一个问题读到设计与实现：\n')
    base=f'https://github.com/{u}'
    for title,body,url in [
        ('🔍 企业知识如何进入 RAG？','从文档同步、智能分块读到混合检索、图谱与引用回答。',f'{base}/enterprise-ai-agent-platform#rag-pipeline'),
        ('🧩 Agent 如何执行多步任务？','从 Planner、工具注册与 Memory 读到工作流编排。',f'{base}/enterprise-ai-agent-platform#核心能力'),
        ('🩺 故障诊断如何组织证据？','从 LangGraph Agent 循环读到 Kubernetes 工具、Runbook 与 Incident Report。',f'{base}/enterprise-ai-sre-platform#features'),
        ('🔐 MCP 如何划分读与写？','从工具目录的风险 / 权限读到默认只读与执行保护。',f'{base}/enterprise-devops-mcp-server#mcp-tool-catalog'),
        ('📦 系统如何交付？','从环境配置与 Compose 读到 Kubernetes 和 Helm 部署入口。',f'{base}/enterprise-ai-agent-platform#部署架构')]:
        a(f'- **[{title}]({url})** — {body}')
    a(section_heading('focus'))
    a('- **检索质量**：如何组织评测样本、定位召回与排序问题，让回答更有依据。')
    a('- **执行可靠性**：如何处理超时、重试、部分失败与长任务状态，让 Agent 任务更可控。')
    a('- **可观测性**：如何把模型决策、工具调用、耗时与成本放入同一个分析上下文。')
    a('- **平台体验**：如何降低系统配置、知识接入与工具集成的使用门槛。\n')
    a(section_heading('principles'))
    a('- 🛡️ **边界明确**：权限、租户、数据访问与执行范围应在接口和实现中看得见。')
    a('- 🔎 **过程可查**：错误要能定位，工具调用要有记录，结论要有证据。')
    a('- 📦 **交付完整**：代码之外，补上配置模板、启动方式、部署入口与技术文档。')
    a('- 🧱 **持续演进**：先理清模块职责，再扩展能力；让后续阅读和修改都有路径。\n')
    a(section_heading('links','contact'))
    a('欢迎围绕 **Agent 工程、RAG、MCP、Kubernetes 诊断、平台工程** 交流。发现问题或有改进建议，可以在对应仓库提交 Issue / PR。\n')
    a(f'[🐙 GitHub](https://github.com/{u}) · [📂 所有仓库](https://github.com/{u}?tab=repositories) · [🧠 Agent Platform]({base}/enterprise-ai-agent-platform) · [🛡️ MCP Server]({base}/enterprise-devops-mcp-server)\n')
    a('---\n\n<div align="center">\n\n**'+CFG['closing']+'**\n\n如果某个项目对你有帮助，欢迎留下一个 ⭐\n\n</div>\n')
    (ROOT/'README.md').write_text('\n'.join(L)+'\n',encoding='utf-8')


def build_preview():
    import markdown
    source=(ROOT/'README.md').read_text(encoding='utf-8').replace('<div align="center">', '<div align="center" markdown="1">').replace('<details>', '<details markdown="1">').replace('<details open>', '<details open markdown="1">')
    content=markdown.markdown(source,extensions=['extra','sane_lists','md_in_html'])
    page='''<!doctype html><html lang="zh-CN" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Zhifeng Jin · Profile v5</title><style>
:root{--bg:#fff;--fg:#1f2328;--sub:#59636e;--line:#d1d9e0;--card:#f6f8fa;--link:#0969da}html[data-theme=dark]{--bg:#0d1117;--fg:#e6edf3;--sub:#9198a1;--line:#30363d;--card:#161b22;--link:#58a6ff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}.toolbar{position:sticky;top:0;background:var(--card);border-bottom:1px solid var(--line);padding:10px 24px;z-index:2;display:flex;justify-content:space-between;gap:12px}button{border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);padding:5px 12px;cursor:pointer}.readme{max-width:980px;margin:28px auto;padding:28px;border:1px solid var(--line);border-radius:6px}table{width:100%;border-collapse:collapse;table-layout:fixed}td{border:1px solid var(--line);padding:12px;vertical-align:top}td h4{margin:0 0 12px}td p{overflow-wrap:anywhere}td p{margin:0}td img{margin:3px 2px 3px 0}img{max-width:100%;vertical-align:middle}picture img{display:block;width:100%;height:auto}h2{margin-top:32px;padding-bottom:8px;border-bottom:1px solid var(--line);font-size:24px}h3{font-size:20px;margin:26px 0 14px}a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}li{margin:8px 0}p{margin:14px 0}code{background:var(--card);border-radius:5px;padding:2px 5px;font:85% Consolas,monospace}blockquote{margin:18px 0;border-left:3px solid #B29A58;padding:2px 16px;color:var(--sub);background:var(--card)}hr{border:0;border-top:1px solid var(--line);margin:30px 0}summary{cursor:pointer;color:var(--sub)}details{border:1px solid var(--line);border-radius:8px;padding:12px 16px}details[open] img{margin-top:16px}@media(max-width:650px){.readme{margin:0;border:0;padding:18px;font-size:15px}.toolbar{font-size:12px}}
</style></head><body><div class="toolbar"><span>Profile v5 · GitHub README 内容预览</span><span><button onclick="setTheme('light')">浅色</button> <button onclick="setTheme('dark')">深色</button></span></div><article class="readme">__BODY__</article><script>function setTheme(t){document.documentElement.dataset.theme=t;document.querySelectorAll('picture').forEach(p=>{let i=p.querySelector('img');if(!i.dataset.light)i.dataset.light=i.src.replace('-dark.svg','-light.svg');i.src=i.dataset.light.replace('-light.svg','-'+t+'.svg');p.querySelectorAll('source').forEach(s=>s.media='not all')})}</script></body></html>'''
    (ROOT/'preview.html').write_text(page.replace('__BODY__',content),encoding='utf-8')


def build_english():
    import copy
    en=json.loads((ROOT/'profile.en.json').read_text(encoding='utf-8'))
    u=CFG['username']; base=f'https://github.com/{u}/{u}/blob/main'
    language=f'<p align="center"><a href="https://github.com/{u}">简体中文</a> &nbsp;|&nbsp; <a href="{base}/README_EN.md">English</a></p>\n'
    titles={'about':'About Me','stack':'Tech Stack','projects':'Selected Work','portfolio':'More Projects','notes':'Technical Notes','focus':'Focus & Exploration','principles':'Engineering Principles','links':'Let’s Connect'}
    for key,t in THEMES.items():
        hero=banner(t,CFG).replace('从知识到行动，从代码到系统。','From knowledge to action.').replace('Build with context. Execute with boundaries.','Build with context. Execute with boundaries.')
        (ASSETS/f'banner-en-{key}.svg').write_text(hero,encoding='utf-8')
        for sec in CFG['sections']:
            translated=dict(sec,title=titles[sec['key']])
            (ASSETS/f'hdr-{sec["key"]}-en-{key}.svg').write_text(header(t,translated),encoding='utf-8')
        for i,(pr,d) in enumerate(zip(CFG['projects'],en['projects']),1):
            translated=dict(pr,name=d['name'],desc=d['focus'],tech=pr['tech'])
            (ASSETS/f'proj-{pr["slug"]}-en-{key}.svg').write_text(project(t,translated,i),encoding='utf-8')
    L=[language,pic('banner-en','Zhifeng Jin — AI Agent / AIOps / Platform Engineering'),'\n**AI Agent · AIOps · Platform Engineering**\n','Make knowledge searchable, tools governed, and systems observable.\n','[About](#about) · [Tech Stack](#stack) · [Projects](#projects) · [Notes](#notes) · [Connect](#contact)\n']
    a=L.append
    def heading(k,anchor=None):
        a((f'<a id="{anchor}"></a>\n\n' if anchor else '')+'<h2>'+pic('hdr-'+k+'-en',titles[k]).replace('\n','')+'</h2>\n')
    a(quick_actions(True))
    a('### 🎬 Project Preview\n')
    a(portfolio_gallery(True))
    heading('about','about')
    for line in en['about']:a('- '+line)
    a('\n> ✨ My engineering interest: connect documents, models, tools and infrastructure into systems that are understandable, deployable and maintainable.\n')
    a('### Where to start\n\n- **AI application engineering** → the knowledge Agent platform: connectors, retrieval, graphs and workflows.\n- **AIOps / SRE** → the diagnosis platform: infrastructure evidence, runbooks and execution traces.\n- **MCP engineering** → the DevOps server: tool schemas, risk classification and execution gates.\n')
    heading('stack','stack')
    original=copy.deepcopy(CFG['badge_groups'])
    try:
        for group,title in zip(CFG['badge_groups'],en['skills'][0]):group['title']=title
        a(tech_badge_grid())
    finally:CFG['badge_groups']=original
    a('These technologies reflect application and integration work across the public projects; see each repository for its actual scope.\n')
    for line in en['skills'][1]:a('- '+line)
    a('')
    heading('projects','projects')
    a('The core portfolio follows **knowledge automation → incident diagnosis → tool governance**.\n')
    for i,(pr,d) in enumerate(zip(CFG['projects'],en['projects'])):
        if i==3:
            heading('portfolio')
            a('Additional open-source practice in gateways, commerce and network authentication. Repository capabilities are described here; attribution and licensing remain with each project.\n')
        a(f'### {i+1:02d} · [{d["name"]}]({pr["url"]})\n')
        a('<a href="'+pr['url']+'">'+pic('proj-'+pr['slug']+'-en',d['name']).replace('\n','')+'</a>\n')
        a(d['intro']+'\n')
        a('<details>\n<summary>🔬 Explore technical implementation</summary>\n')
        for line in d['bullets']:a('- '+line)
        a('\n</details>\n\n> 🔧 Engineering focus: '+d['focus']+'\n')
        links=[('Source',pr['url'])]
        labels=['Demo','Architecture','Reference']
        links.extend((labels[j] if j<len(labels) else 'Documentation',url) for j,(_,url) in enumerate(CFG['project_details'][i]['links']))
        a(' · '.join(f'[{label}]({url})' for label,url in links)+'\n\n---\n')
    heading('notes','notes')
    a('Use the project documentation as a reading path from a concrete engineering question to its design:\n')
    for title,repo,fragment in [('How does enterprise knowledge enter RAG?','enterprise-ai-agent-platform','rag-pipeline'),('How are Agent tasks orchestrated?','enterprise-ai-agent-platform','核心能力'),('How is incident evidence collected?','enterprise-ai-sre-platform','features'),('How does MCP separate reads from writes?','enterprise-devops-mcp-server','mcp-tool-catalog'),('How is the platform deployed?','enterprise-ai-agent-platform','部署架构')]:
        a(f'- [{title}](https://github.com/{u}/{repo}#{fragment})')
    a('')
    heading('focus')
    for line in en['next']:a('- '+line)
    a('')
    heading('principles')
    for line in en['principles']:a('- '+line)
    a('')
    heading('links','contact')
    a('Happy to exchange ideas about **Agent engineering, RAG, MCP, Kubernetes diagnosis and platform engineering**. Issues and pull requests are welcome in the relevant repositories.\n')
    a(f'[GitHub](https://github.com/{u}) · [All repositories](https://github.com/{u}?tab=repositories)\n\n---\n\nBuild ideas into code, and make systems understandable and reliable. Thanks for your feedback and support ✨\n')
    a(language)
    (ROOT/'README_EN.md').write_text('\n'.join(L)+'\n',encoding='utf-8')


def main():
    n = build_assets()
    for key,t in THEMES.items():
        (ASSETS/f'languages-{key}.svg').write_text(language_panel(t),encoding='utf-8')
        (ASSETS/f'capability-{key}.svg').write_text(capability_map(t),encoding='utf-8')
    build_action_assets()
    build_readme()
    build_english()
    build_preview()
    print(f"OK: {n} animated SVG + README.md + preview.html")
    print(f"assets -> {ASSETS}")


if __name__ == "__main__":
    main()
