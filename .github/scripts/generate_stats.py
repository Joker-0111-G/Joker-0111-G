#!/usr/bin/env python3
"""Generate GitHub stats SVG using GitHub API (no external dependencies)."""

import json
import os
import urllib.request

USERNAME = "Joker-0111-G"
OUTPUT_DIR = "assets"
BG_COLOR = "#0d1117"
CARD_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
ACCENT_COLOR = "#58a6ff"
LABEL_COLOR = "#8b949e"
LANG_COLORS = {
    "Go": "#00ADD8", "Python": "#3572A5", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#563d7c",
    "C++": "#f34b7d", "C": "#555555", "Java": "#b07219",
    "Shell": "#89e051", "MATLAB": "#e16737", "Jupyter Notebook": "#DA5B0F",
    "Wolfram Language": "#DD1100", "Rust": "#dea584", "Vue": "#41b883",
    "Dockerfile": "#384d54", "Makefile": "#427819",
}


def api(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_stats_svg(user, repos):
    """Generate stats card like github-readme-stats style."""
    total_stars = sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))
    total_forks = sum(r.get("forks_count", 0) for r in repos if not r.get("fork"))
    total_issues = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    items = [
        ("⭐ Stars", str(total_stars)),
        ("🍴 Forks", str(total_forks)),
        ("📦 Repos", str(total_issues)),
        ("👥 Followers", str(followers)),
        ("🔗 Following", str(following)),
    ]

    card_w, card_h = 420, 30 + len(items) * 40 + 20
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#161b22" />
      <stop offset="100%" stop-color="#0d1117" />
    </linearGradient>
  </defs>
  <rect width="{card_w}" height="{card_h}" rx="10" fill="url(#grad)" stroke="#30363d" stroke-width="1" />
  <text x="20" y="24" font-family="Segoe UI, sans-serif" font-size="16" font-weight="700" fill="{TEXT_COLOR}">{escape(USERNAME)}</text>
  <text x="20" y="24" font-family="Segoe UI, sans-serif" font-size="16" fill="{ACCENT_COLOR}">&#39;s Stats</text>
'''

    y = 55
    for label, value in items:
        svg += f'''
  <text x="25" y="{y}" font-family="Segoe UI, sans-serif" font-size="13" fill="{LABEL_COLOR}">{label}</text>
  <text x="{card_w - 25}" y="{y}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="13" font-weight="600" fill="{TEXT_COLOR}">{value}</text>'''
        y += 35

    svg += '\n</svg>'
    return svg


def generate_langs_svg(langs_data):
    """Generate top languages pie bar card."""
    total = sum(langs_data.values())
    if total == 0:
        langs_data = {"Go": 1}
        total = 1

    sorted_langs = sorted(langs_data.items(), key=lambda x: x[1], reverse=True)[:8]
    others = sum(v for k, v in sorted_langs[8:]) if len(sorted_langs) > 8 else 0
    sorted_langs = sorted_langs[:8]
    if others > 0:
        sorted_langs.append(("Other", others))

    card_w, card_h = 420, 40 + 25 * len(sorted_langs) + 40
    bar_w = 200

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}">
  <defs>
    <linearGradient id="lgrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#161b22" />
      <stop offset="100%" stop-color="#0d1117" />
    </linearGradient>
  </defs>
  <rect width="{card_w}" height="{card_h}" rx="10" fill="url(#lgrad)" stroke="#30363d" stroke-width="1" />
  <text x="20" y="24" font-family="Segoe UI, sans-serif" font-size="16" font-weight="700" fill="{TEXT_COLOR}">Most Used Languages</text>
'''

    y = 48
    for lang, count in sorted_langs:
        pct = count / total * 100
        color = LANG_COLORS.get(lang, "#6e7681")
        w = max(int(bar_w * pct / 100), 1)

        svg += f'''
  <rect x="20" y="{y}" width="10" height="10" rx="3" fill="{color}" />
  <text x="36" y="{y + 9}" font-family="Segoe UI, sans-serif" font-size="12" fill="{TEXT_COLOR}">{escape(lang)}</text>
  <text x="{card_w - 20}" y="{y + 9}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="12" fill="{TEXT_COLOR}">{pct:.1f}%</text>
  <rect x="20" y="{y + 16}" width="{bar_w}" height="6" rx="3" fill="#21262d" />
  <rect x="20" y="{y + 16}" width="{w}" height="6" rx="3" fill="{color}" />'''
        y += 32

    svg += '\n</svg>'
    return svg


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching user data...")
    user = api(f"/users/{USERNAME}")

    print("Fetching repos...")
    repos = api(f"/users/{USERNAME}/repos?per_page=100&sort=updated")

    # Fetch all repos if there are more than 100
    page = 2
    while True:
        page_repos = api(f"/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated")
        if not page_repos:
            break
        repos.extend(page_repos)
        page += 1

    # Generate language stats from all repos
    print("Calculating language stats...")
    lang_data = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        lang_url = repo.get("languages_url", "")
        if lang_url:
            try:
                repo_langs = api(repo["url"] + "/languages")
                for lang, bytes_count in repo_langs.items():
                    lang_data[lang] = lang_data.get(lang, 0) + bytes_count
            except Exception:
                pass

    print(f"Found {len(repos)} repos, {len(lang_data)} languages")

    # Generate SVGs
    stats_svg = generate_stats_svg(user, repos)
    with open(os.path.join(OUTPUT_DIR, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg)
    print(f"✅ Written stats.svg ({len(stats_svg)} bytes)")

    langs_svg = generate_langs_svg(lang_data)
    with open(os.path.join(OUTPUT_DIR, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(langs_svg)
    print(f"✅ Written top-langs.svg ({len(langs_svg)} bytes)")


if __name__ == "__main__":
    main()
