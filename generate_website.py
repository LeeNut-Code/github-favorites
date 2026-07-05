#!/usr/bin/env python3
"""
generate_website.py - 从各月目录生成"栗子的github收藏夹"网站

使用方法:
  python generate_website.py

输出:
  website/index.html  (完整自包含的静态网站)
"""

import os
import re
import html as html_mod
from pathlib import Path

BASE_DIR = Path(__file__).parent
WEBSITE_DIR = BASE_DIR / "website"

MONTH_LABELS = {
    "202510": "2025.10",
    "202511": "2025.11",
    "202512": "2025.12",
    "202601": "2026.01",
    "202602": "2026.02",
    "202603": "2026.03",
    "202604": "2026.04",
    "202605": "2026.05",
    "202606": "2026.06",
}

MONTH_ORDER = sorted(MONTH_LABELS.keys())


def parse_bookmark_name(text):
    """从 bookmark 链接文本提取项目名和描述"""
    text = text.strip()
    # 格式: "项目名: 描述" 或 "项目名 - 描述"
    for sep in ["：", ":", " - ", " — ", "——", "–"]:
        if sep in text:
            name, desc = text.split(sep, 1)
            return name.strip(), desc.strip()
    # 尝试 URL 最后一段
    return text, ""


def extract_github_repo(url):
    """从 GitHub URL 提取 owner/repo"""
    match = re.search(r"github\.com/([^/]+/[^/#?]+)", url)
    if match:
        return match.group(1).rstrip("/")
    return None


def parse_bookmarks_html(filepath):
    """从 bookmarks.html 提取项目列表"""
    projects = []
    content = filepath.read_text("utf-8", errors="replace")
    pattern = re.compile(r'<A\s+HREF="([^"]+)"[^>]*>([^<]+)</A>', re.IGNORECASE)
    for match in pattern.finditer(content):
        url = match.group(1).strip()
        link_text = match.group(2).strip()
        if not url or not link_text:
            continue
        # 只取 github 链接
        if "github.com" in url:
            # 优先从 URL 提取 owner/repo 作为项目名
            repo_full = extract_github_repo(url)
            # 尝试拆分 link_text 为 名称:描述
            name, desc = parse_bookmark_name(link_text)
            # 如果 link_text 本身看起来就是描述（不含 : 分割）,
            # 则用 repo_full 作为名称, link_text 作为描述
            if not desc and repo_full:
                name = repo_full
                desc = link_text
            projects.append(
                {
                    "name": name or repo_full or link_text,
                    "url": url,
                    "description": desc or "",
                }
            )
    return projects


def parse_readme_categorized(filepath):
    """从 README.md 解析分类和描述"""
    projects = []
    content = filepath.read_text("utf-8", errors="replace")
    current_category = "未分类"

    lines = content.split("\n")
    for i, line in enumerate(lines):
        # 匹配分类标题: "### AI工具"
        cat_match = re.match(r"^###\s+(.+)", line)
        if cat_match:
            current_category = cat_match.group(1).strip()
            continue
        # 匹配项目: "- [name](url)\n  描述"
        proj_match = re.match(r"-\s+\[([^\]]+)\]\(([^)]+)\)", line)
        if proj_match:
            name = proj_match.group(1).strip()
            url = proj_match.group(2).strip()
            # 收集后面所有连续缩进行作为描述
            desc_lines = []
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                if next_line.strip() == "":
                    continue
                if next_line.startswith("  ") and not next_line.strip().startswith("-"):
                    desc_lines.append(next_line.strip())
                else:
                    break
            description = " ".join(desc_lines) if desc_lines else ""
            projects.append(
                {
                    "name": name,
                    "url": url,
                    "description": description,
                    "category": current_category,
                }
            )
    return projects


# ============ 分类名称统一映射 ============
CATEGORY_ALIASES = {
    "AI工具": "AI / Agent 工具",
    "AI 工具": "AI / Agent 工具",
    "AI/Agent工具": "AI / Agent 工具",
    "开发工具": "编程开发",
    "shell/终端": "Shell / 终端",
    "桌面应用": "桌面工具",
    "系统优化": "系统工具",
    "系统工具": "系统工具",
    "下载与资源": "资源收集",
    "其他资源": "资源收集",
    "awesome列表": "Awesome 列表",
    "Awesome 列表": "Awesome 列表",
    "网络/代理": "网络工具",
    "音乐音频": "媒体工具",
    "录屏截图": "桌面工具",
    "文本输入": "输入法",
    "博客社区": "社交 / 社区",
    "其他应用": "其他",
    "其他": "其他",
    "其他工具": "其他",
    "学术与写作": "学术 / 写作",
    "学术/写作": "学术 / 写作",
    "媒体与娱乐": "媒体工具",
    "应用与客户端": "桌面工具",
    "网络与代理": "网络工具",
    "Shell / 终端": "Shell / 终端",
}


# ============ 自动分类规则 ============
# ============ 手动分类覆盖（URL 到分类）============
MANUAL_CATEGORIES = {
    "https://github.com/Olcmyk/HuChenFeng": "社交 / 社区",
    "https://github.com/MashiroSaber03/Saber-Translator": "编程开发",
    "https://github.com/hhhweihan/EasyTshark": "网络工具",
    "https://github.com/lanceliao/china-holiday-calender": "桌面工具",
    "https://github.com/vsme/chinese-days": "桌面工具",
    "https://github.com/henrywhitaker3/Speedtest-Tracker": "网络工具",
    "https://github.com/Sanjeever/port_sentinel": "网络工具",
    "https://github.com/pbeenigg/LittleCrawler": "编程开发",
    "https://github.com/flutter_server_box": "系统工具",
    "https://github.com/Crosstalk-Solutions/项目游牧者": "其他",
    "https://github.com/wm94i/Work_Review": "桌面工具",
}


CATEGORY_RULES = [
    (
        "AI / Agent 工具",
        [
            "ai",
            "llm",
            "agent",
            "deepseek",
            "claude",
            "gpt",
            "chat",
            "prompt",
            "token",
            "大模型",
            "人工智能",
            "智能体",
            "ai-",
            "-ai",
            "llama",
            "ollama",
            "openai",
            "gemini",
            "codex",
            "cursor",
            "nanobot",
            "openclaw",
        ],
    ),
    (
        "编程开发",
        [
            "editor",
            "ide",
            "sdk",
            "api",
            "framework",
            "library",
            "package",
            "rust",
            "python",
            "typescript",
            "javascript",
            "npm",
            "编译器",
            "template",
            "starter",
            "boilerplate",
            "markdown",
            "记事本",
            "emacs",
            "vim",
            "vscode",
            "git",
            "pr",
            "commit",
            "blog",
            "cms",
            "font",
            "字体",
            "monospace",
            "qml",
            "ui-kit",
            "翻译",
            "translate",
            "ant-d",
            "crawler",
            "爬虫",
            "rpa",
            "web自动化",
            "日历",
            "备份",
            "fork",
            "第三方",
            "holiday",
            "节假日",
            "加密",
            "crypto",
            "shark",
            "speed",
            "速度",
            "离线",
            "survival",
            "tshark",
            "nginx",
            "端口",
            "port",
            "serverbox",
        ],
    ),
    (
        "桌面工具",
        [
            "desktop",
            "剪贴板",
            "便签",
            "粘贴",
            "clipboard",
            "note",
            "便签",
            "屏幕",
            "截图",
            "screenshot",
            "pet",
            "宠物",
            "压缩",
            "鼠标",
            "图床",
            "日历",
            "时钟",
            "颜色",
            "color",
            "picker",
            "新标签页",
            "网页.*app",
            "web-to-app",
            "pake",
            "输入流转",
            "压缩软件",
            "画中画",
        ],
    ),
    (
        "系统工具",
        [
            "系统",
            "优化",
            "清理",
            "性能",
            "管理",
            "system",
            "utility",
            "windows",
            "macos",
            "linux",
            "优化",
            "清理",
            "tool",
            "监控",
            "monitor",
            "硬件",
            "wsl",
            "distro",
            "引导",
            "grub",
            "powershell",
            "debloat",
            "emoji",
            "进程",
            "ad",
            "广告",
            "hosts",
            "换源",
            "自托管",
            "托管",
            "panel",
        ],
    ),
    (
        "媒体工具",
        [
            "player",
            "播放器",
            "music",
            "音乐",
            "video",
            "视频",
            "iptv",
            "电视",
            "media",
            "下载器",
            "download",
            "媒体",
            "jellyfin",
            "影视",
            "bilibili",
            "bili",
            "画中画",
            "rss",
            "feed",
            "pixiv",
            "直播",
            "蓝奏云",
            "一起看",
            "synctv",
        ],
    ),
    (
        "Awesome 列表",
        [
            "awesome",
            "精选",
            "资源大全",
            "合集",
            "collection",
            "list",
            "awesome-",
            "精选的",
        ],
    ),
    (
        "网络工具",
        [
            "proxy",
            "dpi",
            "vpn",
            "ssh",
            "网络",
            "代理",
            "科学上网",
            "network",
            "bypass",
            "防火墙",
            "订阅转换",
            "转发",
            "dns",
            "cloudflare",
            "cdn",
            "服务器",
        ],
    ),
    (
        "浏览器扩展",
        [
            "chrome",
            "extension",
            "插件",
            "bookmarklet",
            "微博",
            "brave",
            "浏览器",
            "superium",
        ],
    ),
    (
        "输入法",
        [
            "输入法",
            "拼音",
            "ime",
            "ibus",
        ],
    ),
    (
        "学习资源",
        [
            "教程",
            "学习",
            "课程",
            "guide",
            "tutorial",
            "book",
            "入门",
            "指南",
            "实践",
            "数学",
            "security",
            "网络安全",
            "面试",
            "求职",
        ],
    ),
    (
        "社交 / 社区",
        [
            "聊天",
            "im",
            "微信",
            "telegram",
            "端到端",
            "mixgram",
            "elementary",
        ],
    ),
]


def normalize_category(cat):
    """统一分类名称"""
    if not cat or cat == "未分类":
        return ""
    return CATEGORY_ALIASES.get(cat, cat)


def auto_categorize(project):
    """根据项目名称和描述自动推断分类（含手动覆盖）"""
    # 先查手动映射
    url = project.get("url", "")
    if url in MANUAL_CATEGORIES:
        return MANUAL_CATEGORIES[url]
    # 关键词匹配
    text = (project["name"] + " " + project.get("description", "")).lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return category
    return "未分类"


def extract_month_data(month_id):
    """提取一个月的所有项目数据"""
    month_dir = BASE_DIR / month_id
    if not month_dir.is_dir():
        return []

    readme_path = month_dir / "README.md"
    bookmarks_path = month_dir / "bookmarks.html"

    projects = []

    if readme_path.exists():
        projects = parse_readme_categorized(readme_path)
    elif bookmarks_path.exists():
        projects = parse_bookmarks_html(bookmarks_path)

    # 补充月份信息
    for p in projects:
        p["month"] = month_id
        p["monthLabel"] = MONTH_LABELS.get(month_id, month_id)
        p["category"] = normalize_category(p.get("category", "") or "")
        if not p["category"]:
            p["category"] = auto_categorize(p)

    return projects


def deduplicate(projects):
    """去重：同一 URL 只保留第一次出现的版本"""
    seen = set()
    result = []
    for p in projects:
        if p["url"] not in seen:
            seen.add(p["url"])
            result.append(p)
    return result


def collect_all_data():
    """收集所有月份数据"""
    all_projects = []
    for month_id in MONTH_ORDER:
        projects = extract_month_data(month_id)
        all_projects.extend(projects)
    return deduplicate(all_projects)


def build_html(projects):
    """生成完整网站 HTML"""
    total = len(projects)

    # 按月份分组
    monthly = {}
    for p in projects:
        monthly.setdefault(p["month"], []).append(p)

    # 收集所有分类
    all_categories_set = set()
    for p in projects:
        if p.get("category"):
            all_categories_set.add(p["category"])
    all_categories = sorted(all_categories_set)

    # 月份统计
    month_stats = []
    for m in MONTH_ORDER:
        count = len(monthly.get(m, []))
        month_stats.append({"id": m, "label": MONTH_LABELS.get(m, m), "count": count})

    # 转 JSON 嵌入 HTML
    import json

    projects_json = json.dumps(projects, ensure_ascii=False)
    month_stats_json = json.dumps(month_stats, ensure_ascii=False)
    categories_json = json.dumps(all_categories, ensure_ascii=False)

    # 获取最新月份
    latest_month = max(p["month"] for p in projects) if projects else ""

    return HTML_TEMPLATE.format(
        total=total,
        total_months=len(MONTH_ORDER),
        projects_json=projects_json,
        month_stats_json=month_stats_json,
        categories_json=categories_json,
        latest_month=latest_month,
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>栗子的GitHub收藏夹</title>
<style>
/* ============ Reset & Base ============ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
  background: var(--bg);
  color: var(--text);
  transition: background 0.3s, color 0.3s;
  min-height: 100vh;
}}

/* ============ Theme Variables ============ */
:root {{
  --bg: #FFF8F0;
  --surface: #FFFFFF;
  --surface-hover: #FFF3E0;
  --text: #2C2416;
  --text-secondary: #8B7355;
  --text-muted: #B8A88E;
  --primary: #C4943E;
  --primary-light: #E8D5A8;
  --primary-dark: #A07530;
  --border: #E8DDD0;
  --tag-bg: #F5EDE0;
  --tag-text: #8B7355;
  --card-shadow: 0 2px 8px rgba(0,0,0,0.06);
  --card-shadow-hover: 0 4px 16px rgba(0,0,0,0.10);
  --input-bg: #FFFFFF;
  --input-border: #D4C8B8;
  --header-bg: rgba(255, 248, 240, 0.92);
  --tab-active-bg: #C4943E;
  --tab-active-text: #FFFFFF;
  --tab-hover-bg: #F0E6D8;
  --badge-bg: #C4943E;
  --badge-text: #FFFFFF;
  --link-color: #2D8E4A;
  --divider: #E8DDD0;
  --stat-card-bg: #FFFDF8;
}}

[data-theme="dark"] {{
  --bg: #1A1510;
  --surface: #2A2218;
  --surface-hover: #3A3022;
  --text: #E8DCC8;
  --text-secondary: #B8A88E;
  --text-muted: #7A6A54;
  --primary: #D4A74B;
  --primary-light: #5A4A32;
  --primary-dark: #E8C87A;
  --border: #3A3228;
  --tag-bg: #3A3022;
  --tag-text: #C8B898;
  --card-shadow: 0 2px 8px rgba(0,0,0,0.2);
  --card-shadow-hover: 0 4px 16px rgba(0,0,0,0.3);
  --input-bg: #2A2218;
  --input-border: #4A3E2E;
  --header-bg: rgba(26, 21, 16, 0.92);
  --tab-hover-bg: #3A3022;
  --badge-bg: #D4A74B;
  --badge-text: #1A1510;
  --link-color: #5BBF7A;
  --divider: #3A3228;
  --stat-card-bg: #222016;
}}

/* ============ Header ============ */
.header {{
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  padding: 16px 24px;
}}
.header-inner {{
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}}
.header-left {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.header-icon {{
  font-size: 28px;
  line-height: 1;
}}
.header-title {{
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  white-space: nowrap;
}}
.header-title span {{
  color: var(--primary);
}}
.header-right {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.theme-btn {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 18px;
  color: var(--text-secondary);
  transition: all 0.2s;
  line-height: 1;
}}
.theme-btn:hover {{
  background: var(--surface-hover);
  color: var(--primary);
}}

/* ============ Stats Bar ============ */
.stats-bar {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 24px 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}}
.stat-card {{
  background: var(--stat-card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  text-align: center;
}}
.stat-number {{
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  line-height: 1.2;
}}
.stat-label {{
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}}

/* ============ Month Tabs ============ */
.tabs-wrapper {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px 0;
}}
.tabs {{
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 8px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}}
.tabs::-webkit-scrollbar {{
  height: 4px;
}}
.tabs::-webkit-scrollbar-thumb {{
  background: var(--border);
  border-radius: 2px;
}}
.tab-btn {{
  flex-shrink: 0;
  padding: 8px 18px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}}
.tab-btn:hover {{
  background: var(--tab-hover-bg);
  color: var(--text);
}}
.tab-btn.active {{
  background: var(--tab-active-bg);
  color: var(--tab-active-text);
  border-color: var(--tab-active-bg);
}}
.tab-count {{
  display: inline-block;
  margin-left: 4px;
  font-size: 11px;
  opacity: 0.7;
}}

/* ============ Filters ============ */
.filters {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}}
.search-box {{
  flex: 1;
  min-width: 200px;
  position: relative;
}}
.search-box input {{
  width: 100%;
  padding: 10px 14px 10px 38px;
  border: 1px solid var(--input-border);
  border-radius: 10px;
  background: var(--input-bg);
  color: var(--text);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}}
.search-box input:focus {{
  border-color: var(--primary);
}}
.search-box .search-icon {{
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 16px;
  pointer-events: none;
}}
.category-filter select {{
  padding: 10px 14px;
  border: 1px solid var(--input-border);
  border-radius: 10px;
  background: var(--input-bg);
  color: var(--text);
  font-size: 14px;
  outline: none;
  cursor: pointer;
  min-width: 120px;
}}
.category-filter select:focus {{
  border-color: var(--primary);
}}

/* ============ Card Grid ============ */
.grid-wrapper {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 24px 40px;
}}
.grid-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}}
.grid-count {{
  font-size: 13px;
  color: var(--text-secondary);
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}}
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.card:hover {{
  box-shadow: var(--card-shadow-hover);
  border-color: var(--primary-light);
  transform: translateY(-1px);
}}
.card-top {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}}
.card-name {{
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  text-decoration: none;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}}
.card-name:hover {{
  color: var(--link-color);
}}
.card-name .owner {{
  color: var(--text-secondary);
  font-weight: 400;
}}
.card-link {{
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}}
.card-link:hover {{
  background: #2D8E4A;
  color: white;
}}
[data-theme="dark"] .card-link:hover {{
  background: #5BBF7A;
  color: #1A1510;
}}
.card-desc {{
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}}
.card-footer {{
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 4px;
}}
.tag {{
  display: inline-block;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  background: var(--tag-bg);
  color: var(--tag-text);
}}
.tag-month {{
  background: var(--badge-bg);
  color: var(--badge-text);
}}

.empty-state {{
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}}
.empty-state .empty-icon {{
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}}
.empty-state p {{
  font-size: 15px;
}}

/* ============ Back to Top ============ */
.back-top {{
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary);
  color: var(--badge-text);
  border: none;
  cursor: pointer;
  font-size: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.3s;
  z-index: 90;
}}
.back-top.visible {{
  opacity: 1;
  transform: translateY(0);
}}
.back-top:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}}
.back-top.visible:hover {{
  transform: translateY(-2px);
}}

/* ============ Footer ============ */
.footer {{
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 13px;
  border-top: 1px solid var(--border);
}}

/* ============ Responsive ============ */
@media (max-width: 768px) {{
  .header {{ padding: 12px 16px; }}
  .header-title {{ font-size: 17px; }}
  .stats-bar {{ padding: 16px 16px 0; grid-template-columns: repeat(2, 1fr); }}
  .tabs-wrapper {{ padding: 12px 16px 0; }}
  .filters {{ padding: 8px 16px; flex-direction: column; }}
  .search-box {{ min-width: 100%; }}
  .category-filter select {{ width: 100%; }}
  .grid-wrapper {{ padding: 8px 16px 24px; }}
  .grid {{ grid-template-columns: 1fr; }}
  .stat-card {{ padding: 10px 12px; }}
  .stat-number {{ font-size: 20px; }}
}}

@media (min-width: 769px) and (max-width: 1024px) {{
  .grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
</head>
<body>

<!-- ============ HEADER ============ -->
<header class="header">
  <div class="header-inner">
    <div class="header-left">
      <span class="header-icon">🌰</span>
      <h1 class="header-title">栗子的<span>GitHub</span>收藏夹</h1>
    </div>
    <div class="header-right">
      <button class="theme-btn" id="themeToggle" title="切换主题">🌙</button>
    </div>
  </div>
</header>

<!-- ============ STATS ============ -->
<div class="stats-bar" id="statsBar"></div>

<!-- ============ TABS ============ -->
<div class="tabs-wrapper">
  <div class="tabs" id="tabs"></div>
</div>

<!-- ============ FILTERS ============ -->
<div class="filters">
  <div class="search-box">
    <span class="search-icon">🔍</span>
    <input type="text" id="searchInput" placeholder="搜索项目名称、描述..." />
  </div>
  <div class="category-filter">
    <select id="categoryFilter">
      <option value="">全部分类</option>
    </select>
  </div>
</div>

<!-- ============ GRID ============ -->
<div class="grid-wrapper">
  <div class="grid-header">
    <span class="grid-count" id="gridCount"></span>
  </div>
  <div class="grid" id="projectGrid"></div>
</div>

<!-- ============ BACK TO TOP ============ -->
<button class="back-top" id="backTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<!-- ============ FOOTER ============ -->
<footer class="footer">
  栗子的GitHub收藏夹 &middot; 共 {total} 个项目 &middot; 持续更新中 🚀
</footer>

<script>
// ============ DATA ============
const PROJECTS = {projects_json};
const MONTH_STATS = {month_stats_json};
const ALL_CATEGORIES = {categories_json};

// ============ STATE ============
let currentMonth = "{latest_month}";
let currentSearch = "";
let currentCategory = "";

// ============ RENDER STATS ============
function renderStats() {{
  const bar = document.getElementById("statsBar");
  const totalMonths = MONTH_STATS.filter(m => m.count > 0).length;
  const maxCount = Math.max(...MONTH_STATS.map(m => m.count));
  const busiest = MONTH_STATS.find(m => m.count === maxCount);
  bar.innerHTML = `
    <div class="stat-card"><div class="stat-number">${{PROJECTS.length}}</div><div class="stat-label">总项目</div></div>
    <div class="stat-card"><div class="stat-number">${{totalMonths}}</div><div class="stat-label">收藏月份</div></div>
    <div class="stat-card"><div class="stat-number">${{busiest ? busiest.count : 0}}</div><div class="stat-label">最多·${{busiest ? busiest.label : ''}}</div></div>
    <div class="stat-card"><div class="stat-number">${{ALL_CATEGORIES.length}}</div><div class="stat-label">分类数</div></div>
  `;
}}

// ============ RENDER TABS ============
function renderTabs() {{
  const container = document.getElementById("tabs");
  let html = `<button class="tab-btn ${{currentMonth === 'all' ? 'active' : ''}}" onclick="switchMonth('all')">全部 <span class="tab-count">${{PROJECTS.length}}</span></button>`;
  MONTH_STATS.forEach(m => {{
    if (m.count === 0) return;
    html += `<button class="tab-btn ${{m.id === currentMonth ? 'active' : ''}}" onclick="switchMonth('${{m.id}}')">${{m.label}} <span class="tab-count">${{m.count}}</span></button>`;
  }});
  container.innerHTML = html;
}}

function switchMonth(month) {{
  currentMonth = month;
  renderTabs();
  renderGrid();
  document.getElementById("backTop").click();
}}

// ============ RENDER CATEGORY FILTER ============
function renderCategoryFilter() {{
  const select = document.getElementById("categoryFilter");
  ALL_CATEGORIES.forEach(c => {{
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    select.appendChild(opt);
  }});
}}

// ============ RENDER CARD GRID ============
function getFilteredProjects() {{
  return PROJECTS.filter(p => {{
    if (currentMonth !== "all" && p.month !== currentMonth) return false;
    if (currentCategory && p.category !== currentCategory) return false;
    if (currentSearch) {{
      const q = currentSearch.toLowerCase();
      const searchable = (p.name + " " + p.description + " " + (p.category || "")).toLowerCase();
      if (!searchable.includes(q)) return false;
    }}
    return true;
  }});
}}

function renderGrid() {{
  const filtered = getFilteredProjects();
  const grid = document.getElementById("projectGrid");
  const count = document.getElementById("gridCount");

  count.textContent = `显示 ${{filtered.length}} / ${{PROJECTS.length}} 个项目`;

  if (filtered.length === 0) {{
    grid.innerHTML = '<div class="empty-state"><span class="empty-icon">🔍</span><p>没有找到匹配的项目 😅</p></div>';
    return;
  }}

  grid.innerHTML = filtered.map(p => {{
    const nameParts = p.name.split("/");
    const owner = nameParts.length > 1 ? nameParts[0] : "";
    const repoName = nameParts.length > 1 ? nameParts.slice(1).join("/") : p.name;

    return `
      <div class="card">
        <div class="card-top">
          <a href="${{p.url}}" target="_blank" rel="noopener" class="card-name" title="${{html(p.url)}}">
            ${{owner ? `<span class="owner">${{owner}}</span>/${{repoName}}` : p.name}}
          </a>
          <a href="${{p.url}}" target="_blank" rel="noopener" class="card-link" title="在 GitHub 中打开">↗</a>
        </div>
        ${{p.description ? `<div class="card-desc">${{html(p.description)}}</div>` : ''}}
        <div class="card-footer">
          ${{p.category ? `<span class="tag">${{html(p.category)}}</span>` : ''}}
          <span class="tag tag-month">${{p.monthLabel}}</span>
        </div>
      </div>
    `;
  }}).join("");
}}

function html(s) {{
  if (!s) return "";
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}}

// ============ EVENT LISTENERS ============
document.getElementById("searchInput").addEventListener("input", (e) => {{
  currentSearch = e.target.value;
  renderGrid();
}});

document.getElementById("categoryFilter").addEventListener("change", (e) => {{
  currentCategory = e.target.value;
  renderGrid();
}});

// ============ THEME TOGGLE ============
const themeToggle = document.getElementById("themeToggle");
themeToggle.addEventListener("click", () => {{
  const html = document.documentElement;
  const isDark = html.getAttribute("data-theme") === "dark";
  html.setAttribute("data-theme", isDark ? "light" : "dark");
  themeToggle.textContent = isDark ? "🌙" : "☀️";
  localStorage.setItem("theme", isDark ? "light" : "dark");
}});

// Restore theme
const savedTheme = localStorage.getItem("theme");
if (savedTheme === "dark") {{
  document.documentElement.setAttribute("data-theme", "dark");
  themeToggle.textContent = "☀️";
}}

// ============ BACK TO TOP VISIBILITY ============
window.addEventListener("scroll", () => {{
  const btn = document.getElementById("backTop");
  btn.classList.toggle("visible", window.scrollY > 300);
}});

// ============ INIT ============
renderStats();
renderTabs();
renderCategoryFilter();
renderGrid();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    print("🔄 正在收集数据...")
    projects = collect_all_data()
    print(f"📦 共收集到 {len(projects)} 个项目")

    if not projects:
        print("❌ 未找到任何项目，请确认各月目录结构")
        exit(1)

    print("🏗️  生成网站...")
    html = build_html(projects)

    WEBSITE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = WEBSITE_DIR / "index.html"
    output_path.write_text(html, "utf-8")
    print(f"✅ 网站已生成: {output_path}")
    print(f"   🗂️  {len(MONTH_ORDER)} 个月份")
    print(f"   📊  {len(set(p.get('category', '') for p in projects))} 个分类")
    print(f"   📄  文件大小: {len(html.encode()):,} 字节")
