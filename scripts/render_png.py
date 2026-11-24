#!/usr/bin/env python3
"""Render a local preview PNG from the same layout as diagrams/泳道图.drawio.

The repo PNG (diagrams/泳道图.png) is the native draw.io export (2026-11-25,
1312x862 RGBA). This script only produces a local preview at
"diagrams/泳道图-预览.png" and never overwrites the native export.
The drawio file is canonical (opens in draw.io).
See README.md for the disclosure.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "diagrams", "泳道图-预览.png")

FONT_DIR = "/usr/share/fonts/opentype/noto"
F_REG = os.path.join(FONT_DIR, "NotoSansCJK-Regular.ttc")
F_BOLD = os.path.join(FONT_DIR, "NotoSansCJK-Bold.ttc")

W, H = 1400, 900
LANE_FILL = "#DAE8FC"
LANE_LINE = "#6C8EBF"
LANE_TITLE = "#1F4E79"
NODE_FILL = "#FFFFFF"
NODE_LINE = "#333333"
DEC_FILL = "#FFF2CC"
DEC_LINE = "#D6B656"
RB_FILL = "#F8CECC"
RB_LINE = "#B85450"
END_FILL = "#D5E8D4"
END_LINE = "#82B366"
EDGE = "#333333"
TEXT = "#000000"

LANES = [
    ("SOP 编辑", 20), ("SOP 负责人", 240), ("一线执行代表", 460),
    ("会所负责人", 680), ("知识库管理员", 900), ("运营负责人", 1120),
]
LANE_W, LANE_Y, LANE_H, TITLE_H = 210, 20, 860, 30

# (id, x, y, w, h, kind, [lines]) — absolute coords, identical to the drawio file.
NODES = [
    ("n1", 40, 70, 170, 54, "box", ["起草版本草稿"]),
    ("n2", 260, 200, 170, 54, "box", ["评审草稿"]),
    ("n3", 480, 200, 170, 54, "box", ["评审会签"]),
    ("n4", 1140, 200, 170, 54, "box", ["影响评估", "（被咨询）"]),
    ("d1", 280, 320, 130, 80, "diamond", ["评审通过？"]),
    ("n5", 40, 320, 170, 54, "box", ["按评审意见修订"]),
    ("d2", 280, 450, 130, 80, "diamond", ["是否主版本？"]),
    ("n6", 700, 444, 170, 66, "box", ["试运行", "（至少2周；", "达到20实例后评估）"]),
    ("n7", 480, 560, 170, 54, "box", ["试运行反馈"]),
    ("d3", 700, 580, 130, 80, "diamond", ["试运行达标？"]),
    ("d4", 280, 580, 130, 80, "diamond", ["4周不足20实例", "负责人裁定"]),
    ("d5", 280, 790, 130, 80, "diamond", ["6周最终裁定", "不得再延长"]),
    ("n8", 920, 450, 170, 54, "box", ["正式发布"]),
    ("n9", 1140, 450, 170, 54, "box", ["签收发布通知"]),
    ("n10", 920, 580, 170, 54, "box", ["归档旧版本"]),
    ("n11", 260, 700, 170, 54, "rbox", ["确认回滚"]),
    ("n12", 920, 700, 170, 54, "rbox", ["执行回滚", "恢复旧版本"]),
    ("e1", 960, 810, 90, 40, "ellipse", ["结束"]),
]
GEO = {n[0]: n for n in NODES}

def anchor(nid, side):
    _, x, y, w, h, _, _ = GEO[nid]
    return {"l": (x, y + h // 2), "r": (x + w, y + h // 2),
            "t": (x + w // 2, y), "b": (x + w // 2, y + h)}[side]

# (points, label, label_xy or None) — points include start/end anchors.
EDGES = [
    ([anchor("n1", "r"), anchor("n2", "l")], "", None),
    ([anchor("n2", "r"), anchor("n3", "l")], "", None),
    ([anchor("n2", "t"), (345, 150), (1225, 150), anchor("n4", "t")], "征询", (785, 138)),
    ([anchor("n3", "b"), (565, 290), (345, 290), anchor("d1", "t")], "", None),
    ([anchor("d1", "l"), anchor("n5", "r")], "否", (245, 338)),
    ([anchor("n5", "t"), (125, 170), (260, 170), anchor("n2", "l")], "重新提交评审", (150, 158)),
    ([anchor("d1", "b"), anchor("d2", "t")], "是", (355, 415)),
    ([anchor("d2", "b"), (345, 545), (1005, 545), anchor("n8", "b")], "否：次版本跳过试运行", (600, 533)),
    ([anchor("d2", "r"), anchor("n6", "l")], "是：主版本", (480, 478)),
    ([anchor("n6", "l"), (565, 477), anchor("n7", "t")], "反馈", (600, 465)),
    ([anchor("n6", "b"), anchor("d3", "t")], "", None),
    ([anchor("n7", "r"), (700, 587), anchor("d3", "l")], "", None),
    ([anchor("d3", "b"), (765, 770), (125, 770), anchor("n5", "b")], "否：回起草修订", (430, 758)),
    ([anchor("d3", "r"), (880, 620), (880, 477), anchor("n8", "l")], "是", (888, 540)),
    ([anchor("n8", "r"), anchor("n9", "l")], "发出发布通知", (1115, 432)),
    ([anchor("n8", "b"), anchor("n10", "t")], "", None),
    ([anchor("n10", "r"), (1130, 607), (1130, 830), anchor("e1", "r")], "", None),
    ([anchor("n10", "b"), (1005, 670), (345, 670), anchor("n11", "t")], "发布后14天内触发回滚条件", (620, 658)),
    ([anchor("n11", "r"), anchor("n12", "l")], "", None),
    ([anchor("n12", "b"), anchor("e1", "t")], "", None),
    ([anchor("n7", "b"), (565, 650), (345, 650), anchor("d4", "b")], "满4周仍不足20实例", (510, 638)),
    ([anchor("d4", "r"), anchor("d3", "l")], "按现有样本裁定", (555, 625)),
    ([anchor("d4", "l"), (240, 620), (240, 435), (700, 435), anchor("n6", "l")], "延长 2 周", (470, 420)),
    ([anchor("n7", "b"), (565, 650), (440, 650), (440, 780), (345, 780), anchor("d5", "t")], "满6周仍不足20实例", (392, 768)),
    ([anchor("d5", "r"), (700, 830), anchor("d3", "l")], "按现有样本裁定", (555, 818)),
    ([anchor("d5", "l"), (180, 830), (180, 374)], "未达标：返回起草修订", (195, 600)),
    ([(410, 834), (700, 834), (700, 850), (960, 850), (960, 830)], "放弃本次变更", (680, 838)),
]


def font(size, bold=False):
    return ImageFont.truetype(F_BOLD if bold else F_REG, size)


def ortho(pts):
    """Expand a 2-point edge into an orthogonal elbow route."""
    if len(pts) != 2:
        return pts
    (x1, y1), (x2, y2) = pts
    if x1 == x2 or y1 == y2:
        return pts
    mx = (x1 + x2) // 2
    return [(x1, y1), (mx, y1), (mx, y2), (x2, y2)]


def draw_arrow(d, pts, width=2):
    pts = ortho(pts)
    d.line(pts, fill=EDGE, width=width, joint="curve")
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = max(1, (dx * dx + dy * dy) ** 0.5)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    tip = (x2, y2)
    b1 = (x2 - 12 * ux + 5 * px, y2 - 12 * uy + 5 * py)
    b2 = (x2 - 12 * ux - 5 * px, y2 - 12 * uy - 5 * py)
    d.polygon([tip, b1, b2], fill=EDGE)


def draw_text_block(d, cx, cy, lines, size=15, bold=False):
    f = font(size, bold)
    lh = size + 6
    total = lh * len(lines) - 6
    y = cy - total // 2
    for line in lines:
        w = d.textlength(line, font=f)
        d.text((cx - w / 2, y), line, font=f, fill=TEXT)
        y += lh


def main():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    # lanes
    for name, x in LANES:
        d.rectangle([x, LANE_Y, x + LANE_W, LANE_Y + LANE_H],
                    fill=LANE_FILL, outline=LANE_LINE, width=2)
        d.rectangle([x, LANE_Y, x + LANE_W, LANE_Y + TITLE_H],
                    fill=LANE_LINE)
        f = font(16, True)
        w = d.textlength(name, font=f)
        d.text((x + LANE_W // 2 - w / 2, LANE_Y + 7), name, font=f,
               fill="white")
    # edges first (under nodes)
    for pts, label, lab_xy in EDGES:
        draw_arrow(d, pts)
    # nodes
    for _, x, y, w, h, kind, lines in NODES:
        if kind == "box":
            fill, line = NODE_FILL, NODE_LINE
            d.rounded_rectangle([x, y, x + w, y + h], radius=8,
                                fill=fill, outline=line, width=2)
        elif kind == "rbox":
            d.rounded_rectangle([x, y, x + w, y + h], radius=8,
                                fill=RB_FILL, outline=RB_LINE, width=2)
        elif kind == "diamond":
            cx, cy = x + w // 2, y + h // 2
            d.polygon([(cx, y), (x + w, cy), (cx, y + h), (x, cy)],
                      fill=DEC_FILL, outline=DEC_LINE, width=2)
        elif kind == "ellipse":
            d.ellipse([x, y, x + w, y + h], fill=END_FILL,
                      outline=END_LINE, width=2)
        draw_text_block(d, x + w // 2, y + h // 2, lines, size=15)
    # edge labels with white backing
    fl = font(13)
    for pts, label, lab_xy in EDGES:
        if not label or not lab_xy:
            continue
        lx, ly = lab_xy
        w = d.textlength(label, font=fl)
        d.rectangle([lx - w / 2 - 3, ly - 2, lx + w / 2 + 3, ly + 15],
                    fill="white")
        d.text((lx - w / 2, ly), label, font=fl, fill=TEXT)
    img.save(OUT, "PNG")
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
