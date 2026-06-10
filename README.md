# 🌰 栗子的 GitHub 收藏夹

个人 GitHub 开源项目收藏展示站，按月归档收藏的优质开源项目。

## 目录结构

```
github_favorites/
├── website/               ← 生成的静态网站（双击 index.html 即可浏览）
│   └── index.html
├── generate_website.py    ← 网站数据生成脚本
├── 202510/                ← 各月收藏数据
│   └── bookmarks.html
├── 202511/
│   └── bookmarks.html
├── 202512/
│   └── bookmarks.html
├── 202601/
│   └── bookmarks.html
├── 202602/
│   └── bookmarks.html
├── 202603/
│   └── bookmarks.html
├── 202604/
│   ├── bookmarks.html
│   └── README.md          ← 含分类和中文描述的月度清单
├── 202605/
│   ├── bookmarks.html
│   └── README.md
├── extract_favorites.py   ← 收藏提取工具
├── extract_monthly.py     ← 按月拆分工具
├── .gitignore
└── README.md
```

## 快速使用

1. **浏览收藏**：直接打开 `website/index.html`
2. **更新数据**：添加新月份目录后运行：
   ```bash
   python3 generate_website.py
   ```
3. **部署到网络**：将 `website/` 目录上传到 GitHub Pages / Cloudflare Pages / Vercel 等静态托管平台

## 数据概览

| 月份 | 项目数 |
|------|-------|
| 2025.10 | 20 |
| 2025.11 | 19 |
| 2025.12 | 40 |
| 2026.01 | 23 |
| 2026.02 | 26 |
| 2026.03 | 47 |
| 2026.04 | 40 |
| 2026.05 | 59 |
| **总计** | **274** |

涵盖分类：AI / Agent 工具、编程开发、系统工具、桌面工具、网络工具、媒体工具、Awesome 列表、输入法、浏览器扩展、学习资源等 15 个类别。

## 更新流程

1. 通过浏览器收藏新的 GitHub 项目
2. 导出书签到 `书签_年月日.html`
3. 运行 `extract_favorites.py` 提取收藏
4. 运行 `extract_monthly.py` 按月拆分到对应目录
5. 可选：在月度目录下编写 `README.md` 添加详细分类和描述
6. 运行 `python3 generate_website.py` 更新网站

## 技术栈

- **前端**：纯 HTML + CSS + JavaScript（单页应用，零依赖）
- **数据处理**：Python 3（数据提取、自动分类、网站生成）
- **部署**：支持任何静态托管（GitHub Pages / Cloudflare Pages / Vercel）
