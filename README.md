<div align="center">

# 🔎 CathayRestore

**TXT 文本层写回工具 · 让双层 PDF 真正"搜得到"**

*开箱即用 · 双击即开 · 纯本地 · 不联网 · 不改动原件*

[![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![platform](https://img.shields.io/badge/platform-Windows%2010%2B-brightgreen)]()
[![python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![GitHub release](https://img.shields.io/github/v/release/zzhjim02/CathayRestore)]()

**把 OCR 识别出来的 TXT，按「第 N 页」写回对应 PDF** —— 生成竖排、透明、可搜索的文字层，
替换掉旧的双层 PDF 里那层错位的文字。

</div>

---

## 🔗 Cathay 人文研究工具链

<div align="center">

| 步骤 | 工具 | 功能 | 状态 |
|:----:|:----|:----|:----:|
| ① | [**CathayOCR** →](https://github.com/zzhjim02/CathayOCR) | 📄 多引擎 GPU 加速古籍 PDF 批处理 OCR | ✅ v1.2.4 |
| ② | **⭐ CathayRestore（你在这里）** | 🔎 **把 OCR 的 TXT 按页写回 PDF（竖排/透明/可搜索）** | 🆕 **v1.0.0** |
| ③ | [**CathaySimplify** →](https://github.com/zzhjim02/CathaySimplify) | 🔄 TXT 繁简体批量双向转换 · 编码智能适配 | ✅ v1.0.0 |
| ④ | [**CathayReader** →](https://github.com/zzhjim02/CathayReader) | 📖 PDF/TXT 双栏同步古籍校勘阅读器 | ✅ v1.0.0 |
| ⑤ | [**CathayShelf** →](https://github.com/zzhjim02/CathayShelf) | 🗂️ 图书著录建夹 · 后缀替换 · 繁简转换+编码规范化 | ✅ v0.4.3 |

</div>

**五步完成古籍数字化：** `CathayOCR` 批量识别 → `CathayRestore` 修好文本层 → `CathaySimplify` 繁简统一 → `CathayReader` 双栏校勘 → `CathayShelf` 著录归架

> 📌 **这是本仓库（CathayRestore）** — 工作流第 2 步，负责让扫描件"可检索"。
> 本来它是 [CathayOCR](https://github.com/zzhjim02/CathayOCR) 安装包里的小工具（`TXT写回工具\`），现在**独立成一个软件**，不必再依赖 CathayOCR 的便携目录。

---

## 📖 目录

- [这个仓库是什么？](#-这个仓库是什么)
- [它解决什么问题？](#-它解决什么问题)
- [核心特性](#-核心特性)
- [一分钟快速上手](#-一分钟快速上手)
- [文件配对规则](#-文件配对规则)
- [下载](#-下载)
- [系统要求](#-系统要求)
- [从源码运行 / 自己打包](#-从源码运行--自己打包)
- [文件结构](#-文件结构)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)
- [许可](#-许可)

---

## ❓ 这个仓库是什么？

> ⚠️ **重要提示：GitHub 上的这个仓库只包含 Python 源码（.py），不含打包好的 exe。**
>
> 需要直接用的话，请到下方 [下载](#-下载) 区域取安装包。

**一句话：** 你有一批 OCR 出来的 `XXX_result.txt`，也有一批对应的 PDF；PDF 里自带的那层文字（旧 OCR 层）错字多、位置歪、还搜不全。这个工具把 TXT 里的文字**重新写回 PDF**——竖排、透明、位置对得上，并且 Ctrl+F 能搜到。

### 谁需要它？

| 角色 | 场景 |
|:-----|:-----|
| 📚 **古籍研究者** | 双层 PDF 搜不到字、复制出来是乱码，要重建文字层 |
| 🏛️ **图书馆 / 档案馆** | 检索系统里挂的 PDF 得"能搜"，旧 OCR 层不可用 |
| 🧾 **二次 OCR 的用户** | 用更好的模型重识别后，把新文本写回原 PDF，保留原图 |
| 🤝 **和 Cathay 工具链一起用** | CathayOCR 出了 TXT + 双层 PDF，发现图层不理想 → 用它重写 |

---

## 🎯 它解决什么问题？

双层 PDF（图像 + 不可见文字层）本该"看着像扫描件、搜起来像电子书"。但现实中经常出问题：

| 毛病 | 表现 |
|:-----|:-----|
| ❌ 搜不到 | Ctrl+F 输入正文里的词，一个都搜不到 |
| ❌ 复制乱码 | 选中文字复制出来是另一段内容 |
| ❌ 位置错位 | 高亮框飘到页面外 |
| ❌ 竖排古籍 | 文字横着写进去了，长句被页面右边界裁掉、缺字 |

**CathayRestore 的做法**：把 OCR 的 TXT 按页切开 → **物理删掉 PDF 原有的全部文字块**（保留图像层，像素级无损）→ 按识别语言写回一层**竖排（rotate=270）、完全透明、可搜索**的 CJK 文字层 → 输出 `XXX_..._fixed.pdf`，**绝不覆盖原件**。

---

## ✨ 核心特性

| 特性 | 说明 |
|:-----|:-----|
| 📄 **按页写回** | 自动解析 TXT 里的 `第N页` 分页标记，逐页对应写回 |
| 🈶 **竖排古籍友好** | 每行一列、列序右→左（rotate=270），一行文字不再被页面边界裁掉 |
| 👻 **完全透明** | 文字层 `fill/stroke opacity = 0`，只对搜索和选择可见，不影响观感 |
| 🖼️ **图像层无损** | 只删文字块（`BT…ET`），图像与矢量图形原样保留（实测像素级一致） |
| 🔒 **不覆盖原件** | 输出为 `原名_后缀.pdf`，默认后缀 `_fixed`，可自定义 |
| 🔗 **三条配对规则** | 自动把 TXT 和 PDF 配上对（见下），其它后缀产物自动忽略 |
| 🧵 **多核并行** | 1~16 线程，默认 `min(4, CPU 核数)` |
| 🖱️ **拖放 + 挑选** | 文件/文件夹拖进窗口，列表可勾选：只处理选中的，也可全选/全不选 |
| 📂 **递归扫描** | 文件夹递归找配对，子目录一并处理 |
| 🔍 **可验证** | 处理后可直接用阅读器的 Ctrl+F 搜索验证；文本内容与 TXT 一致 |

---

## 🚀 一分钟快速上手

```
1. 解压安装包 → 双击【CathayRestore】（或 写回.bat）
2. 点【选择文件夹】或把文件夹/文件直接拖进窗口（支持递归）
3. 工具自动扫描配对，列表显示：TXT ｜ PDF ｜ 状态
4. （可选）改输出后缀、并发线程数；勾选要处理的行
5. 点【开始处理选中项】→ 进度条走完，输出 XXX_fixed.pdf 与原件同目录
6. 点【打开输出目录】查看结果
```

> 💡 **建议**：第一次先拿一两本试，用 PDF 阅读器 Ctrl+F 搜一个正文词确认能搜到，再批量跑。
> 处理过程**不修改原件**，跑坏了删掉 `_fixed.pdf` 重来即可。

---

## 🔗 文件配对规则

工具在**同一目录**里按下表把 TXT 和 PDF 配上对（只认这三条，其它后缀如 `_【繁转简】` 一律忽略）：

| TXT | ↔ | PDF |
|:----|:-:|:----|
| `XXX_result.txt` | ↔ | `XXX_layered.pdf` |
| `XXX_PD6AIFOCR.txt` | ↔ | `XXX_PD6AIFOCR_opt.pdf` |
| `XXX_PD6AIFOCR.txt` | ↔ | `XXX_PD6AIFOCR.pdf` |

- 文件名前缀必须完全一致；同一本可同时存在多套产物
- `_result.txt ↔ _layered.pdf` 是 [CathayOCR](https://github.com/zzhjim02/CathayOCR) 的原生产物
- `_PD6AIFOCR.*` 是 [CathayShelf](https://github.com/zzhjim02/CathayShelf) 选项卡一（后缀替换）规范化后的产物

---

## 📦 下载

> 安装包内含 **便携 Python 运行时 + PyMuPDF**，解压即用，无需任何安装步骤。

### 🚀 最新版 v1.0.0

| 下载方式 | 链接 |
|:-------|:-----|
| 📥 **中国移动云盘**（推荐） | [点击下载](<待填：中国移动云盘分享链接>) |
| 📥 **百度网盘**（备用，密码 2026） | [点击下载](<待填：百度网盘分享链接>) |
| 🐙 **GitHub Releases** | [CathayRestore v1.0.0](https://github.com/zzhjim02/CathayRestore/releases/tag/v1.0.0) |

**包内包含：**

| 文件 | 说明 |
|:-----|:-----|
| `CathayRestore.exe` | **单文件版**，约 67 MB，双击即用（推荐） |
| `写回.bat` + `runtime\` | **便携版**，自带 Python，约 89 MB；脚本式启动，改代码后立即生效 |
| `app.ico` / `CathayRestore.lnk` | 图标与快捷方式 |
| `打包EXE.bat` | 一键重新打包成单文件 exe |

---

## 🖥️ 系统要求

| 项目 | 最低配置 | 推荐配置 |
|:----|:--------|:--------|
| **操作系统** | Windows 10 x64 | Windows 10 / 11 x64 |
| **CPU** | x64 双核 | 4 核以上（可并行） |
| **内存** | 2 GB | 8 GB+（大页数 PDF 更吃内存） |
| **磁盘** | 100 MB（不含你的书） | SSD |
| **运行时** | **无需安装任何东西** | **无需安装任何东西** |
| **网络** | **全程不联网** | — |

---

## 🛠️ 从源码运行 / 自己打包

```bash
# 1. 装依赖
pip install pymupdf            # 核心
pip install tkinterdnd2        # 可选：拖放支持

# 2. 图形界面
python gui.py

# 3. 命令行（单本）
python restore.py <txt 文件> <pdf 文件> [输出后缀]

# 4. 环境体检（写 _selftest.txt）
python gui.py --selftest
```

**打包成单文件 exe：**

```bash
# 直接双击 打包EXE.bat，或手动执行：
pyinstaller --noconfirm --clean --onefile --windowed --name CathayRestore ^
  --icon app.ico --add-data "app.ico;." ^
  --collect-all tkinterdnd2 --hidden-import fitz gui.py
```

---

## 📁 文件结构

```
CathayRestore-DEV/
├── gui.py                # 图形界面（拖放、配对列表、并行处理）
├── restore.py            # 引擎：解析分页 → 删旧文字层 → 写竖排透明文字层
├── 写回.bat              # 启动器（优先用 runtime\，回退系统 Python）
├── 打包EXE.bat           # 一键打包单文件 exe
├── app.ico               # 图标
├── requirements.txt      # 依赖
├── 发布流程.md            # 发版清单（构建 → 校验 → 上传网盘 → 填链接）
└── README.md             # 本文件
```

---

## ❓ 常见问题

<details>
<summary><b>会改坏我的 PDF 吗？</b></summary>

不会：① 输出为新文件（默认 `_fixed.pdf`），**绝不覆盖原件**；② 只删除 PDF 里的**文字块**，图像层与矢量图形**像素级保留**（已做逐像素对比验证）；③ 不满意直接删掉输出文件重跑。
</details>

<details>
<summary><b>写回后为什么"看着没变化"？</b></summary>

因为文字层是**完全透明**的 —— 这是刻意设计。它的作用只在搜索与选择：用 PDF 阅读器 Ctrl+F 搜一个正文词，能高亮命中就对了。
</details>

<details>
<summary><b>支持竖排古籍吗？</b></summary>

支持，而且是重点。写回时按 `rotate=270` 从框顶向下竖排，长句完整落在页面内，不再被右边界裁掉而搜不到。
</details>

<details>
<summary><b>TXT 里没有「第N页」标记怎么办？</b></summary>

请先用 [CathayOCR](https://github.com/zzhjim02/CathayOCR) 产出的 `_result.txt`（含页码分隔），或 [CathayShelf](https://github.com/zzhjim02/CathayShelf) 规范过的 `_PD6AIFOCR.txt`。没有分页标记就没法按页对齐。
</details>

<details>
<summary><b>能处理几百本吗？</b></summary>

能。把文件夹拖进来递归扫描，按 CPU 核数设并发（默认 4），几百本十几分钟量级。处理时注意磁盘空间：输出文件与原件同大小。
</details>

<details>
<summary><b>和 CathayOCR 里的"TXT写回工具"什么区别？</b></summary>

功能一致，**独立成了一个软件**：自带运行时、独立图标与界面，不必依赖 CathayOCR 的便携 Python 目录；界面重做（拖放、选行、并发可调），并与 Cathay 其它工具风格统一。
</details>

---

## 📝 更新日志

### v1.0.0（2026-09-19）
- 🎉 **从 CathayOCR 安装包的 `TXT写回工具\` 独立成软件**：自带运行时、独立 exe 与图标。
- 🖱️ 界面重做：拖入文件/文件夹、递归扫描、配对列表、**选行处理**、全选/全不选、输出后缀、并发线程数、打开输出目录。
- 🧵 引擎保持原行为：`第N页` 解析、删旧文字层（`BT…ET`）、竖排透明文字层（rotate=270）、三条配对规则、不覆盖原件、输出后缀默认 `_fixed`。
- ✅ 实测：配对（含子目录递归）、旧层清除、文本可搜索（`中华人民共和国`/`图书馆` 命中）、图像层逐像素一致、干扰产物（`_【繁转简】.txt`）正确忽略、只处理选中行不误重置其它行。
- ➕ 新增 `--selftest` 环境体检；异常自动写 `_error.log`。

---

## ⚖️ 许可

本项目遵循 **[GPL-3.0 License](LICENSE)**。

<div align="center">

**Cathay 人文研究工具链**

| 🔗 项目 | 📝 仓库 | 🎯 职责 |
|:-------|:--------|:--------|
| CathayOCR | [github.com/zzhjim02/CathayOCR](https://github.com/zzhjim02/CathayOCR) | 多引擎 GPU 加速 PDF 批量 OCR |
| **CathayRestore** | **github.com/zzhjim02/CathayRestore** | **TXT 文本层写回 PDF（可搜索）** |
| CathaySimplify | [github.com/zzhjim02/CathaySimplify](https://github.com/zzhjim02/CathaySimplify) | TXT 繁简体批量双向转换 |
| CathayReader | [github.com/zzhjim02/CathayReader](https://github.com/zzhjim02/CathayReader) | PDF/TXT 双栏同步校勘阅读器 |
| CathayShelf | [github.com/zzhjim02/CathayShelf](https://github.com/zzhjim02/CathayShelf) | 图书著录建夹 · 后缀替换 · 繁简/编码 |

⭐ **扫描件要能搜，才算数字化完成。**

</div>
