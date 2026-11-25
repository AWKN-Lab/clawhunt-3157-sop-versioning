#!/usr/bin/env python3
"""核对 #3157 交付物：5 部分、6 示例判定一致性、drawio 结构、PNG 有效性、虚构数据扫描。

只读检查，不写平台、不推 Git。任一检查失败即退出码非 0。
用法：python3 scripts/check_3157.py
§20 会运行 scripts/render_png.py 生成本地预览 diagrams/泳道图-预览.png
（.gitignore 已排除，不进交付、不进 MANIFEST）。
运行环境：Python 3.12.3，Pillow==10.2.0（见 requirements.txt）。
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def read(rel):
    with open(os.path.join(BASE, rel), encoding="utf-8") as f:
        return f.read()


# ---------- 1. 主文档 5 部分 ----------
main = read("docs/SOP-版本发布流程.md")
for part in ["版本号规则", "五个阶段", "RACI", "回滚规则", "发布通知模板"]:
    check("主文档包含「%s」" % part, part in main)
for must in ["进入条件", "退出条件", "最长停留时间", "5 个百分点", "blocker"]:
    check("主文档包含「%s」" % must, must in main)
stage_heads = ["第 1 阶段：起草", "第 2 阶段：评审", "第 3 阶段：试运行",
               "第 4 阶段：正式发布", "第 5 阶段：旧版本归档"]
idx = [main.find(h) for h in stage_heads]
check("5 个阶段小节齐全且顺序正确",
      all(i >= 0 for i in idx) and idx == sorted(idx))
for j, h in enumerate(stage_heads):
    end = idx[j + 1] if j + 1 < len(idx) else main.find("### 2.6")
    seg = main[idx[j]:end]
    check("%s含进入条件/退出条件/负责角色/所需材料/最长停留" % h,
          all(k in seg for k in ["进入条件", "退出条件", "负责角色",
                                "所需材料", "最长停留时间"]))
pilot = main[main.find("### 2.6"):main.find("## 3.")]
check("试运行转正式三条标准齐全",
      all(k in pilot for k in ["完成率", "超时率", "blocker", "5 个百分点"]))

# ---------- 2. RACI ----------
raci = read("docs/RACI.md")
rows = [ln for ln in raci.splitlines()
        if re.match(r"\| [1-5]\. ", ln)]
check("RACI 表有 5 个阶段行", len(rows) == 5, "行数=%d" % len(rows))
for r in rows:
    cells = [c.strip() for c in r.strip().strip("|").split("|")][1:]
    a_count = sum(1 for c in cells if c == "A" or c.startswith("A /"))
    check("RACI 行「%s」恰有 1 个 A" % r.split("|")[1].strip(),
          a_count == 1, "A 数=%d" % a_count)

# ---------- 3. 通知模板 ----------
tpl = read("docs/发布通知模板.md")
for must in ["变更摘要", "生效时间", "影响角色", "回滚窗口", "模板发布通知"]:
    check("通知模板包含「%s」" % must, must in tpl)
check("通知模板含已填写示例", "已填写示例" in tpl and "2.3 → 3.0" in tpl)
check("通知模板含回滚通知示例", "模板回滚通知" in tpl)

# ---------- 4. 6 示例判定一致性 ----------
ex = read("docs/变更判定示例.md")
sections = re.split(r"\n## 例 \d+：", ex)[1:]
check("示例共 6 个", len(sections) == 6, "个数=%d" % len(sections))
ENGINE = [  # (trigger keyword, rule id, expected judgment)
    ("新增步骤", "M1", "主版本"), ("调整步骤顺序", "M2", "主版本"),
    ("更换步骤的负责角色", "M3", "主版本"),
    ("SLA", "m1", "次版本"), ("表单新增必填字段", "m2", "次版本"),
    ("错别字", "m4", "次版本"),
]
for i, (sec, (kw, rule, want)) in enumerate(zip(sections, ENGINE), 1):
    check("例 %d 含触发词「%s」" % (i, kw), kw in sec)
    m = re.search(r"判定\**：\**\s*(主版本|次版本)", sec)
    got = m.group(1) if m else None
    check("例 %d 判定=%s（规则 %s）" % (i, want, rule), got == want,
          "实际=%s" % got)
    check("例 %d 引用规则 %s" % (i, rule), rule in sec)
    m2 = re.search(r"新版本 \**(\d+\.\d+)\**", sec)
    want_ver = "3.0" if want == "主版本" else "2.4"
    check("例 %d 新版本号=%s" % (i, want_ver),
          bool(m2) and m2.group(1) == want_ver,
          "实际=%s" % (m2.group(1) if m2 else None))
    check("例 %d 有推理" % i, "推理" in sec)
check("例 6 标注「文字修订」", "文字修订" in sections[5])

# ---------- 5. drawio ----------
drawio_path = os.path.join(BASE, "diagrams", "泳道图.drawio")
try:
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = list(root.iter("mxCell"))
    lanes = [c for c in cells if "swimlane" in (c.get("style") or "")]
    edges = [c for c in cells if c.get("edge") == "1"]
    verts = [c for c in cells if c.get("vertex") == "1"]
    check("drawio 为合法 XML 且含 mxGraphModel",
          root.tag == "mxfile" and root.find(".//mxGraphModel") is not None)
    check("drawio 有 6 条泳道", len(lanes) == 6, "泳道数=%d" % len(lanes))
    check("drawio 有 18 个节点", len(verts) - len(lanes) == 18,
          "节点数=%d" % (len(verts) - len(lanes)))
    check("drawio 有 27 条连线", len(edges) == 27, "连线数=%d" % len(edges))
    vals = " ".join((c.get("value") or "") for c in cells)
    for stage in ["起草", "评审", "试运行", "正式发布", "归档"]:
        check("drawio 含阶段「%s」" % stage, stage in vals)
    for role in ["SOP 编辑", "SOP 负责人", "一线执行代表",
                 "会所负责人", "知识库管理员", "运营负责人"]:
        check("drawio 含泳道「%s」" % role, role in vals)
    d5 = [c for c in cells if c.get("id") == "d5"]
    check("drawio d5 为六周最终裁定菱形且在 SOP 负责人泳道",
          len(d5) == 1 and d5[0].get("parent") == "lane2"
          and "rhombus" in (d5[0].get("style") or "")
          and "6周最终裁定" in (d5[0].get("value") or "")
          and "不得再延长" in (d5[0].get("value") or ""),
          "parent=%s" % (d5[0].get("parent") if d5 else None))
    d4 = [c for c in cells if c.get("id") == "d4"]
    check("drawio d4 为延长裁定菱形且在 SOP 负责人泳道",
          len(d4) == 1 and d4[0].get("parent") == "lane2"
          and "rhombus" in (d4[0].get("style") or "")
          and "4周不足20实例" in (d4[0].get("value") or ""),
          "parent=%s" % (d4[0].get("parent") if d4 else None))
except ET.ParseError as e:
    check("drawio 为合法 XML", False, str(e))

# ---------- 6. PNG ----------
from PIL import Image
png_path = os.path.join(BASE, "diagrams", "泳道图.png")
try:
    im = Image.open(png_path)
    im.load()
    check("PNG 可打开", True, "%s %s" % (im.size, im.mode))
    check("PNG 尺寸 1312x862", im.size == (1312, 862), "实际=%s" % (im.size,))
    check("PNG 为 draw.io 原生导出（RGBA）", im.mode == "RGBA", "实际=%s" % (im.mode,))
    check("PNG 非空且大于 10KB",
          os.path.getsize(png_path) > 10 * 1024,
          "%d 字节" % os.path.getsize(png_path))
except Exception as e:
    check("PNG 可打开", False, str(e))

# ---------- 7. drawio 与 PNG 版式一致 ----------
render_src = read("scripts/render_png.py")
drawio_txt = read("diagrams/泳道图.drawio")
for name in ["起草版本草稿", "评审草稿", "评审会签", "正式发布", "归档旧版本",
             "确认回滚", "结束", "4周不足20实例", "负责人裁定",
             "达到20实例后评估", "6周最终裁定", "不得再延长"]:
    check("节点「%s」drawio 与渲染脚本一致" % name,
          name in drawio_txt and name in render_src)
check("drawio 与渲染脚本均无旧表达「≥2周/20实例」",
      "≥2周/20实例" not in drawio_txt and "≥2周/20实例" not in render_src)
check("drawio 含 6 处 swimlane 样式",
      drawio_txt.count('style="swimlane') == 6,
      "计数=%d" % drawio_txt.count('style="swimlane'))
for label in ["满4周仍不足20实例", "按现有样本裁定", "延长 2 周",
             "满6周仍不足20实例", "未达标：返回起草修订", "放弃本次变更"]:
    check("连线标签「%s」drawio 与渲染脚本一致" % label,
          label in drawio_txt and label in render_src)

# ---------- 8. 虚构数据扫描（全仓全类型） ----------
# 覆盖全部文件类型与全部目录；只跳过 MANIFEST 自身（只含哈希）与
# .gitignore 列出的项（本地预览图、__pycache__、*.pyc）。二进制文件按
# 字节读、UTF-8 容错解码后扫描。
def _gitignore_skip(rel):
    if rel == "MANIFEST.sha256":
        return True
    try:
        rules = [ln.strip() for ln in read(".gitignore").splitlines()
                 if ln.strip() and not ln.strip().startswith("#")]
    except OSError:
        rules = []
    import fnmatch
    for rule in rules:
        if rule.endswith("/"):
            if rel.startswith(rule) or ("/" + rule) in ("/" + rel):
                return True
        elif "/" in rule:
            if rel == rule:
                return True
        elif fnmatch.fnmatch(os.path.basename(rel), rule):
            return True
    return False


bad = []
scanned = 0
phone = re.compile(r"1[3-9]\d{9}")
email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
idcard = re.compile(r"\d{17}[\dXx]")
for dirpath, dirnames, files in os.walk(BASE):
    if ".git" in dirnames:
        dirnames.remove(".git")
    for fn in files:
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, BASE)
        if _gitignore_skip(rel):
            continue
        scanned += 1
        txt = open(p, "rb").read().decode("utf-8", "ignore")
        if phone.search(txt):
            bad.append((rel, "手机号"))
        if email.search(txt):
            bad.append((rel, "邮箱"))
        if idcard.search(txt):
            bad.append((rel, "身份证号"))
check("全仓无手机号/邮箱/身份证号", not bad,
      "扫描=%d 文件 命中=%s" % (scanned, bad))

# ---------- 9. README 文件清单 ----------
readme = read("README.md")
for rel in ["docs/SOP-版本发布流程.md", "docs/RACI.md",
            "docs/发布通知模板.md", "docs/变更判定示例.md",
            "diagrams/泳道图.drawio", "diagrams/泳道图.png",
            "scripts/check_3157.py", "scripts/render_png.py"]:
    check("README 清单文件存在：%s" % rel,
          os.path.exists(os.path.join(BASE, rel)))

# ---------- 10. P0-1：试运行四条规则 ----------
s23 = main[main.find("### 2.3"):main.find("### 2.4")]
for phrase in ["至少持续 2 周", "累计达到 20 个实例后",
               "4 周仍不足 20 个实例", "P1、P2、P3 必须全部满足"]:
    check("§2.3 含试运行规则「%s」" % phrase, phrase in s23)
check("§2.3 不再有歧义表述「两者先到为准」", "两者先到为准" not in main)
check("§2.3 含六周最终裁定「不得再延长」", "不得再延长" in s23)
check("示例不再有旧表述「至少 2 周或 20 个实例」",
      "至少 2 周或 20 个实例" not in ex)

# ---------- 11. P0-2：回滚 14 天为日历日 ----------
check("主文档写明回滚 14 天为日历日", "14 天（日历日）" in main)
check("主文档回滚示例截止 2027-02-15 24:00",
      "2027-02-15 24:00" in main)
check("通知模板已填写示例截止 2027-02-15 24:00",
      "2027-02-15 24:00" in tpl)
check("通知模板不再有旧截止 2027-02-16", "2027-02-16" not in tpl)

# ---------- 13. 无法计算指标时不得判定达标 ----------
s26 = main[main.find("### 2.6"):main.find("## 3.")]
for phrase in ["任一判定指标因样本不足无法计算时，不得视为达标",
               "六周期限届满仍无法完成有效判定的，按未达标处理"]:
    check("§2.3 含「%s」" % phrase, phrase in s23)
    check("§2.6 含「%s」" % phrase, phrase in s26)

# ---------- 14. 签字权限表述消除歧义 ----------
check("主文档签字权限：A 不得授权其他角色代签",
      "A 不得授权其他角色代签" in main)
check("主文档签字权限：R 不得由 C 或 I 代签",
      "R 不得由 C（咨询）或 I（知会）代签" in main)
check("主文档签字权限：双 R 两栏均由该人本人签字",
      "两栏均由该人本人签字" in main)
check("RACI.md 签字权限与主文档一致",
      "两栏均由该人本人签字" in raci
      and "R（执行）不得由 C（咨询）或 I（知会）代签" in raci)
check("RACI.md 补入替补身份签字要求",
      "替补人员以替补身份签字" in raci)
check("主文档与 RACI.md 替补身份签字一致",
      "替补人员以替补身份签字" in main
      and "替补人员以替补身份签字" in raci)

# ---------- 15. 附录 B：五个判定点 ----------
check("附录 B 写明五个判定点", "五个判定点" in main)
check("附录 B 含六周最终裁定", "六周最终裁定" in main)
app_b = main[main.find("## 附录 B"):main.find("## 附录 C")]
check("附录 B 写明 d5 三个出口（样本裁定/返回修订/放弃）",
      "按现有样本裁定进入达标判定" in app_b
      and "返回起草修订" in app_b
      and "放弃本次变更" in app_b)

# ---------- 16. 连线拓扑：d5 三个出口 source/target ----------
TOPO = [  # (edge id, source, target, label)
    ("e24", "n7", "d5", "满6周仍不足20实例"),
    ("e25", "d5", "d3", "按现有样本裁定"),
    ("e26", "d5", "n5", "未达标：返回起草修订"),
    ("e27", "d5", "e1", "放弃本次变更"),
]
by_id = {c.get("id"): c for c in cells}
for eid, src, tgt, label in TOPO:
    c = by_id.get(eid)
    check("连线 %s：%s → %s" % (eid, src, tgt),
          c is not None and c.get("edge") == "1"
          and c.get("source") == src and c.get("target") == tgt,
          "实际=%s → %s" % ((c.get("source"), c.get("target"))
                             if c is not None else (None, None)))
    check("连线 %s 标签为「%s」" % (eid, label),
          c is not None and (c.get("value") or "") == label,
          "实际=%s" % ((c.get("value") if c is not None else None),))

# ---------- 12. RACI：评审阶段双 R 说明 ----------
check("主文档说明评审阶段双 R 分工",
      "一线执行代表参与评审和反馈" in main)
check("RACI.md 说明评审阶段双 R 分工",
      "一线执行代表参与评审和反馈" in raci)


# ---------- 17. PNG 内嵌 mxfile 与 drawio 源文件一致 ----------
import struct as _st
import urllib.parse as _up


def _mx_cells(text):
    _root = ET.fromstring(text)
    return {c.get("id"): (c.get("value") or "", c.get("source") or "", c.get("target") or "")
            for c in _root.iter("mxCell")}


_png_bytes = open(os.path.join(BASE, "diagrams/泳道图.png"), "rb").read()
_i = 8
_mx = None
while _i < len(_png_bytes):
    _ln = _st.unpack(">I", _png_bytes[_i:_i + 4])[0]
    _typ = _png_bytes[_i + 4:_i + 8].decode("latin1")
    if _typ in ("tEXt", "iTXt", "zTXt") and _png_bytes[_i + 8:_i + 8 + 7] == b"mxfile\x00":
        _mx = _png_bytes[_i + 15:_i + 8 + _ln].decode("utf-8", "replace")
        break
    _i += 12 + _ln
check("PNG 含 draw.io 内嵌 mxfile 元数据", _mx is not None)
_emb_cells = _mx_cells(_up.unquote(_mx)) if _mx else {}
_src_cells = _mx_cells(read("diagrams/泳道图.drawio"))
check("PNG 内嵌 mxfile 单元格数与 drawio 源文件一致",
      _mx is not None and len(_emb_cells) == len(_src_cells),
      "内嵌=%d 源=%d" % (len(_emb_cells), len(_src_cells)))
check("PNG 内嵌 mxfile 单元格签名（id/值/连线）与 drawio 源文件一致",
      _mx is not None and _emb_cells == _src_cells,
      "差异=%s" % ([k for k in _src_cells if _src_cells.get(k) != _emb_cells.get(k)] or "无"))

# ---------- 19. PNG 内嵌 mxfile 与 drawio 源文件几何/样式一致 ----------
def _mx_cells_full(text):
    _root = ET.fromstring(text)
    _out = {}
    for _c in _root.iter("mxCell"):
        _g = _c.find("mxGeometry")
        _geo = None
        if _g is not None:
            _geo = (_g.get("x"), _g.get("y"), _g.get("width"),
                    _g.get("height"), _g.get("relative"), _g.get("as"))
        _out[_c.get("id")] = ((_c.get("value") or ""),
                              (_c.get("source") or ""),
                              (_c.get("target") or ""),
                              (_c.get("style") or ""), _geo)
    return _out


_emb_full = _mx_cells_full(_up.unquote(_mx)) if _mx else {}
_src_full = _mx_cells_full(read("diagrams/泳道图.drawio"))
_geo_diff = [k for k in _src_full
             if _src_full[k][4] != _emb_full.get(k, (None,) * 5)[4]]
check("PNG 内嵌 mxfile 单元格几何（x/y/w/h）与 drawio 源文件一致",
      _mx is not None and not _geo_diff,
      "差异=%s" % (_geo_diff or "无"))
_style_diff = [k for k in _src_full
               if _src_full[k][3] != _emb_full.get(k, (None,) * 5)[3]]
check("PNG 内嵌 mxfile 单元格样式（style）与 drawio 源文件一致",
      _mx is not None and not _style_diff,
      "差异=%s" % (_style_diff or "无"))

# ---------- 18. README 的 PNG 字节数与实际文件一致 ----------
_png_size = os.path.getsize(os.path.join(BASE, "diagrams/泳道图.png"))
check("README 的 PNG 字节数与实际文件一致",
      ("%d 字节" % _png_size) in read("README.md"),
      "实际=%d 字节" % _png_size)

# ---------- 20. 渲染核验：预览可渲染，原生 PNG 与预览差异已记录 ----------
import subprocess as _sp

_render = _sp.run([sys.executable, os.path.join(BASE, "scripts", "render_png.py")],
                  capture_output=True, text=True, timeout=120)
_preview_path = os.path.join(BASE, "diagrams", "泳道图-预览.png")
_preview_ok = (_render.returncode == 0
               and os.path.exists(_preview_path))
_preview_size = None
_preview_mode = None
if _preview_ok:
    try:
        _pim = Image.open(_preview_path)
        _pim.load()
        _preview_size, _preview_mode = _pim.size, _pim.mode
    except Exception:
        _preview_ok = False
check("渲染预览生成成功（1400×900 RGB）",
      _preview_ok and _preview_size == (1400, 900) and _preview_mode == "RGB",
      "实际=%s %s 退出码=%d" % (_preview_size, _preview_mode,
                                _render.returncode))
# 像素逐点一致：不预期。预览是 Pillow 按同一节点/连线集重绘的示意图
# （画布 1400×900 RGB），原生 PNG 是 draw.io 图界导出（1312×862 RGBA），
# 渲染器与画布都不同。核验点是：两者都可读、尺寸与模式如宣称、差异已
# 在 README 与 evidence/render-compare-20261125.log 中写清。
try:
    _native_size, _native_mode = im.size, im.mode
except NameError:
    _native_size, _native_mode = None, None
check("渲染核验：预览与原生 PNG 尺寸/像素差异已记录且原因已说明",
      _preview_ok and _native_size == (1312, 862) and _native_mode == "RGBA"
      and "预览 1400×900 与原生 1312×862 尺寸不同" in read("README.md"),
      "预览=%s %s 原生=%s %s 像素逐点一致=否（渲染器不同，预期内）"
      % (_preview_size, _preview_mode, _native_size, _native_mode))
print("环境：Python %s，Pillow %s" % (sys.version.split()[0],
                                    __import__("PIL").__version__))

print()
if FAILURES:
    print("RESULT: FAIL (%d 项): %s" % (len(FAILURES), FAILURES))
    sys.exit(1)
print("RESULT: PASS")
