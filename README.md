# Org 模式手册（中文翻译）

> The Org Manual - Chinese Translation

[Org 模式](https://orgmode.org/) 是 GNU Emacs 中强大的笔记记录、TODO 列表管理和项目规划工具。本仓库提供官方手册的中文翻译。

---

## 📖 简介

本翻译基于 Org 9.8 版本的官方英文手册 [The Org Manual](https://orgmode.org/manual/)。

Org 模式是一个纯文本的大纲工具，用于：

- 📝 笔记记录
- ✅ TODO 列表管理
- 📅 日程安排
- 📊 表格处理
- 🔗 超链接管理
- 📤 导出为 HTML、LaTeX、PDF 等格式
- 💻 代码块执行

---

## 📚 目录

### 章节

| 章节 | 标题 | 状态 |
|:----:|------|:----:|
| 1 | [简介](translated/zh/01-简介.org) | ✅ 已翻译 |
| 2 | [文档结构](translated/zh/02-文档结构.org) | ✅ 已翻译 |
| 3 | [表格](translated/org/chapters/03-tables.org) | 🔲 待翻译 |
| 4 | [超链接](translated/org/chapters/04-hyperlinks.org) | 🔲 待翻译 |
| 5 | [TODO 项目](translated/org/chapters/05-todo-items.org) | 🔲 待翻译 |
| 6 | [标签](translated/org/chapters/06-tags.org) | 🔲 待翻译 |
| 7 | [属性和列](translated/org/chapters/07-properties-and-columns.org) | 🔲 待翻译 |
| 8 | [日期和时间](translated/org/chapters/08-dates-and-times.org) | 🔲 待翻译 |
| 9 | [归档和重新归档](translated/org/chapters/09-refiling-and-archiving.org) | 🔲 待翻译 |
| 10 | [捕获和附件](translated/org/chapters/10-capture-and-attachments.org) | 🔲 待翻译 |
| 11 | [日程视图](translated/org/chapters/11-agenda-views.org) | 🔲 待翻译 |
| 12 | [富文本标记](translated/org/chapters/12-markup.org) | 🔲 待翻译 |
| 13 | [导出](translated/org/chapters/13-exporting.org) | 🔲 待翻译 |
| 14 | [发布](translated/org/chapters/14-publishing.org) | 🔲 待翻译 |
| 15 | [引用处理](translated/org/chapters/15-citation-handling.org) | 🔲 待翻译 |
| 16 | [处理源代码](translated/org/chapters/16-working-with-source-code.org) | 🔲 待翻译 |
| 17 | [杂项](translated/org/chapters/17-miscellaneous.org) | 🔲 待翻译 |

### 附录

- A. Hacking（自定义 Org）
- B. 历史和致谢
- C. GNU 自由文档许可证

---

## 🗂️ 项目结构

```
org-mode-manual-zh/
├── README.md                    # 本文件
├── translated/
│   ├── zh/                      # 中文翻译
│   │   ├── 00-前言.org
│   │   ├── 01-简介.org
│   │   ├── 02-文档结构.org
│   │   └── ...
│   └── org/                     # 原始英文（Org 格式）
│       ├── org-manual-zh.org    # 完整手册
│       └── chapters/            # 分割后的章节
├── scripts/
│   ├── fetch_chapters.py        # 抓取英文原版
│   ├── convert.py               # HTML → Org 转换
│   └── translate.py             # 翻译辅助脚本
└── source/
    └── org.html                 # 原始 HTML 手册
```

---

## 🤝 贡献

欢迎参与翻译和改进！

### 翻译指南

1. 保持技术术语的准确性
2. 命令和快捷键使用等宽字体标记
3. 示例代码保持英文（代码中的注释可翻译）
4. 保持 Org 格式标记不变

### 如何贡献

1. Fork 本仓库
2. 选择要翻译的章节（参见 `translated/org/chapters/`）
3. 翻译完成后放到 `translated/zh/` 目录
4. 提交 Pull Request

---

## 📦 使用

### 在线阅读

在 GitHub 上直接查看 `.org` 文件，或克隆到本地使用 Emacs 打开。

### 本地阅读

```bash
git clone https://github.com/fork-svg/org-mode-manual-zh.git
cd org-mode-manual-zh
```

使用 Emacs 打开任意 `.org` 文件即可阅读。

### 导出为其他格式

使用 Emacs 的 `org-export` 功能：

- `C-c C-e h h`：导出为 HTML
- `C-c C-e l p`：导出为 PDF（需要 LaTeX）
- `C-c C-e m m`：导出为 Markdown

---

## 🔗 相关链接

- [Org 模式官方网站](https://orgmode.org/)
- [官方英文手册](https://orgmode.org/manual/)
- [Org 模式快速入门](https://orgmode.org/worg/org-tutorials/org4beginners.html)
- [Worg - Org 模式社区资源](https://orgmode.org/worg/)

---

## 📄 许可证

本翻译遵循 [GNU 自由文档许可证 (GFDL)](https://www.gnu.org/licenses/fdl.html) 1.3 版或更高版本，与原始手册保持一致。

原始手册版权所有 © 2004–2026 Free Software Foundation, Inc.

---

<div align="center">

**让 Org 模式成为您的效率利器！** 🚀

</div>
