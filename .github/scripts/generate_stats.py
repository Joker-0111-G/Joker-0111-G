#!/usr/bin/env python3
"""Generate GitHub stats SVGs in github-readme-stats style."""

import json
import os
import urllib.request

USERNAME = "Joker-0111-G"
OUTPUT_DIR = "assets"

LANG_COLORS = {
    "Go": "#00ADD8", "Python": "#3572A5", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#563d7c",
    "C++": "#f34b7d", "C": "#555555", "Java": "#b07219",
    "Shell": "#89e051", "Jupyter Notebook": "#DA5B0F",
    "Wolfram Language": "#DD1100", "MATLAB": "#e16737",
    "Rust": "#dea584", "Vue": "#41b883", "Dockerfile": "#384d54",
    "Makefile": "#427819",
}

# github-readme-stats blue-green theme colors
THEME = {
    "bg": "#0d1117",
    "card": "#161b22",
    "border": "#30363d",
    "title": "#00b3ff",       # blue-green title
    "text": "#c9d1d9",
    "label": "#8b949e",
    "icon": "#00b3ff",
    "ring_bg": "#1f2937",
    "ring_fg": "#00b3ff",
}


def api(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_stats_svg(user, repos):
    total_stars = sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))
    total_forks = sum(r.get("forks_count", 0) for r in repos if not r.get("fork"))
    total_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    stats = [
        ("📦", "Repos", str(total_repos)),
        ("⭐", "Stars", str(total_stars)),
        ("⑂", "Forks", str(total_forks)),
        ("👥", "Followers", str(followers)),
        ("❤️", "Following", str(following)),
    ]

    card_w = 450
    card_h = 40 + len(stats) * 48 + 30

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{THEME['card']}" />
      <stop offset="100%" stop-color="{THEME['bg']}" />
    </linearGradient>
    <linearGradient id="hdr" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{THEME['icon']}" />
      <stop offset="100%" stop-color="#8b5cf6" />
    </linearGradient>
  </defs>

  <!-- Card background -->
  <rect width="{card_w}" height="{card_h}" rx="8" fill="url(#bg)" stroke="{THEME['border']}" stroke-width="1" />

  <!-- Top gradient strip -->
  <rect x="0" y="0" width="{card_w}" height="4" rx="8" fill="url(#hdr)" />

  <!-- Header: GitHub icon + username -->
  <svg x="20" y="18" width="16" height="16" viewBox="0 0 16 16" fill="{THEME['icon']}">
    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
  </svg>
  <text x="44" y="30" font-family="Segoe UI, sans-serif" font-size="14" font-weight="600" fill="{THEME['title']}">{escape(USERNAME)}&#39;s GitHub Stats</text>

  <!-- Stats list -->
  <rect x="20" y="44" width="{card_w - 40}" height="1" fill="{THEME['border']}" />'''

    y = 68
    for emoji, label, value in stats:
        svg += f'''
  <text x="28" y="{y}" font-family="Segoe UI, sans-serif" font-size="15">{emoji}</text>
  <text x="52" y="{y}" font-family="Segoe UI, sans-serif" font-size="14" fill="{THEME['label']}">{label}</text>
  <text x="{card_w - 28}" y="{y}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="14" font-weight="600" fill="{THEME['text']}">{value}</text>'''
        y += 48

    svg += '''
</svg>'''
    return svg


def generate_langs_svg(langs_data):
    total = sum(langs_data.values())
    if total == 0:
        langs_data = {"Go": 1}
        total = 1

    sorted_langs = sorted(langs_data.items(), key=lambda x: x[1], reverse=True)
    top = sorted_langs[:6]
    others = sum(v for k, v in sorted_langs[6:]) if len(sorted_langs) > 6 else 0
    if others > 0:
        top.append(("Other", others))

    # Compact layout: dot + name + % + thin bar
    card_w = 450
    card_h = 50 + len(top) * 34 + 10

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}">
  <defs>
    <linearGradient id="lbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{THEME['card']}" />
      <stop offset="100%" stop-color="{THEME['bg']}" />
    </linearGradient>
    <linearGradient id="lhdr" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{THEME['icon']}" />
      <stop offset="100%" stop-color="#8b5cf6" />
    </linearGradient>
  </defs>

  <rect width="{card_w}" height="{card_h}" rx="8" fill="url(#lbg)" stroke="{THEME['border']}" stroke-width="1" />
  <rect x="0" y="0" width="{card_w}" height="4" rx="8" fill="url(#lhdr)" />

  <text x="20" y="30" font-family="Segoe UI, sans-serif" font-size="14" font-weight="600" fill="{THEME['title']}">📊 Top Languages</text>

  <rect x="20" y="44" width="{card_w - 40}" height="1" fill="{THEME['border']}" />'''

    bar_full_w = 250
    y = 68

    for lang, count in top:
        pct = count / total * 100
        color = LANG_COLORS.get(lang, "#6e7681")
        bar_w = int(bar_full_w * pct / 100)

        svg += f'''
  <circle cx="32" cy="{y - 4}" r="5" fill="{color}" />
  <text x="46" y="{y}" font-family="Segoe UI, sans-serif" font-size="13" fill="{THEME['text']}">{escape(lang)}</text>
  <text x="{card_w - 20}" y="{y}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="13" fill="{THEME['text']}">{pct:.1f}%</text>
  <rect x="46" y="{y + 5}" width="{bar_full_w}" height="5" rx="3" fill="{THEME['ring_bg']}" />
  <rect x="46" y="{y + 5}" width="{bar_w}" height="5" rx="3" fill="{color}" />'''
        y += 32

    svg += '\n</svg>'
    return svg


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching user data...")
    user = api(f"/users/{USERNAME}")

    print("Fetching repos...")
    repos = api(f"/users/{USERNAME}/repos?per_page=100&sort=updated")
    page = 2
    while True:
        pr = api(f"/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated")
        if not pr:
            break
        repos.extend(pr)
        page += 1

    print("Calculating language stats...")
    lang_data = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            rl = api(repo["url"] + "/languages")
            for lang, bc in rl.items():
                lang_data[lang] = lang_data.get(lang, 0) + bc
        except Exception:
            pass

    print(f"Found {len(repos)} repos, {len(lang_data)} languages")

    stats_svg = generate_stats_svg(user, repos)
    with open(os.path.join(OUTPUT_DIR, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg)
    print(f"✅ stats.svg ({len(stats_svg)} bytes)")

    langs_svg = generate_langs_svg(lang_data)
    with open(os.path.join(OUTPUT_DIR, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(langs_svg)
    print(f"✅ top-langs.svg ({len(langs_svg)} bytes)")


if __name__ == "__main__":
    main()
