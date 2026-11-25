# SOP 模板版本号规则与发布流程文档

ClawHunt 问题单 S6-SOPR-014 的交付物。截止 2027-01-11。投标价 $94.50（90%）。

## 交付物清单

| 文件 | 内容 | 对应验收标准 |
|---|---|---|
| `docs/SOP-版本发布流程.md` | 主文档：版本号规则、5 个阶段的进入与退出条件、RACI 表、回滚规则、通知模板 | AC1（5 部分齐全） |
| `docs/RACI.md` | 独立版 RACI 表：6 个角色 × 5 个阶段 | AC1（RACI 表） |
| `docs/发布通知模板.md` | 发布通知空白模板 + 已填写示例 + 回滚通知示例 | AC1（通知模板） |
| `docs/变更判定示例.md` | 6 个变更示例，逐一判定主版本 / 次版本并附推理 | AC2 |
| `diagrams/泳道图.drawio` | 泳道图源文件（drawio 格式，6 泳道） | AC3 |
| `diagrams/泳道图.png` | 泳道图 PNG（draw.io 原生导出，1312×862） | AC3 |
| `scripts/check_3157.py` | 核对脚本：5 部分、6 示例判定一致性、drawio 结构、PNG 有效性、虚构数据扫描 | 核对用 |
| `scripts/render_png.py` | PNG 预览渲染脚本（Pillow，按 drawio 同一版式绘制；只出预览，不覆盖原生导出） | 渲染用 |
| `requirements.txt` | 运行环境版本固定：Pillow==10.2.0（Python 3.12.3） | 环境用 |
| `ACCEPTANCE-EVIDENCE.md` | 仓根验收证据：按 AC1/AC2/AC3 逐项映射文件路径 + 逐字关键输出 + 已知限制 | 验收证据 |
| `evidence/` | 核对记录、脚本输出、变异自证日志、渲染核验日志 | 核对用 |

## 验收标准对照

1. **文档包含版本号规则、5 个阶段的进入与退出条件、RACI 表、回滚规则、通知模板 5 部分** —— 见 `docs/SOP-版本发布流程.md` 第 1–5 节；每阶段均写明进入条件、退出条件、负责角色、所需材料、最长停留时间。
2. **6 个变更示例并逐一判定主版本或次版本，判定结果与规则一致** —— 见 `docs/变更判定示例.md`：例 1–3 主版本（M1/M2/M3），例 4–6 次版本（m1/m2/m4，其中例 6 标注「文字修订」），每例均写出推理并引用规则编号。
3. **泳道图源文件（drawio）与导出的 PNG 都已提交** —— 见 `diagrams/泳道图.drawio` 与 `diagrams/泳道图.png`。

## 数据说明

全部示例均为虚构数据，不含真实个人信息、企业信息与客户名称；文中角色均为岗位角色名，不指向任何具体个人。依赖 S3-SOP（SOP 引擎与工作台）处以接口桩 / mock 为准，见主文档附录 C。

## 如何核对

```bash
python3 scripts/check_3157.py
```

运行环境：Python 3.12.3，Pillow==10.2.0（见 `requirements.txt`；本机实测 `python3 -c "import PIL; print(PIL.__version__)"` → 10.2.0）。

核对内容：主文档 5 部分齐全、每阶段进入/退出条件齐全、6 示例判定与规则一致、drawio 为合法 XML 且含 6 条泳道与 5 个阶段、PNG 有效非空、全仓全类型无手机号/邮箱等真实个人信息痕迹、PNG 内嵌 mxfile 与 drawio 源文件几何（x/y/w/h）与样式一致、渲染预览可生成。输出见 `evidence/check-output.txt`，逐字关键输出见仓根 `ACCEPTANCE-EVIDENCE.md`。

变异自证：见 `evidence/mutation-proof-20261125.log`——正常跑全过、故意改坏一处示例判定后脚本报 FAIL 且非零退出、恢复后与改前一致。

PNG 导出说明：`diagrams/泳道图.png` 是 draw.io 原生导出（2026-11-25，app.diagrams.net，1312×862 RGBA，158707 字节；流程见 `evidence/核对记录.md`）。`scripts/render_png.py`（Pillow）只生成本地预览 `diagrams/泳道图-预览.png`，不覆盖原生导出。预览 1400×900 与原生 1312×862 尺寸不同，像素不逐点一致：预览是 Pillow 按同一节点/连线集重绘的示意图（画布固定 1400×900 RGB），原生 PNG 是 draw.io 图界导出（1312×862 RGBA）；两者一致性以节点名/标签/几何/样式的文本比对为准（核对脚本 §7、§17、§19），渲染核验数值见 `evidence/render-compare-20261125.log`。核对脚本会校验两者版式一致（节点名、泳道数、连线数）并校验 PNG 为 RGBA（原生导出特征）。

## 文件区分：核心交付与辅助证据

`MANIFEST.sha256` 覆盖全部 16 个文件（不含 `MANIFEST.sha256` 自身与 `.gitignore`）：

- 核心交付文件（9 个）：`README.md`、`diagrams/泳道图.drawio`、`diagrams/泳道图.png`、`docs/` 下 4 份文档、`scripts/` 下 2 个脚本。
- 仓根验收证据（1 个）：`ACCEPTANCE-EVIDENCE.md`。
- 环境固定（1 个）：`requirements.txt`。
- 辅助证据文件（5 个）：`evidence/` 下的核对输出、核对记录、改稿回执、变异自证日志、渲染核验日志。

核心交付文件是买方验收的对象；辅助证据文件是复算这些结论的原始记录。两类文件都受 MANIFEST 哈希保护，改动任一文件都会使 `sha256sum -c MANIFEST.sha256` 报错。

## 仓库说明

目标公开仓：AWKN-Lab/clawhunt-3157-sop-versioning，main 分支。本交付从零新建，与 wave1 分支 `review/clawhunt-wave1-3157-3162-20261123` 与 PR #2 无关，未动用其任何内容。
