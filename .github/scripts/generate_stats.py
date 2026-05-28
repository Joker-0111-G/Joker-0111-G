#!/usr/bin/env python3
"""Generate beautiful GitHub stats SVG using GitHub API."""

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


def api(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetch_avatar_base64(url):
    """Fetch avatar and return base64 data URI."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            import base64
            b64 = base64.b64encode(data).decode()
            return f"data:image/png;base64,{b64}"
    except Exception:
        return None


def generate_stats_svg(user, repos, avatar_uri=None):
    total_stars = sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))
    total_forks = sum(r.get("forks_count", 0) for r in repos if not r.get("fork"))
    total_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)
    total_contributions = total_stars + total_repos + followers + total_forks

    stats_data = [
        ("⭐", "Stars", str(total_stars), "#f0c040"),
        ("🍴", "Forks", str(total_forks), "#8b5cf6"),
        ("📦", "Repos", str(total_repos), "#3b82f6"),
        ("👥", "Followers", str(followers), "#34d399"),
    ]

    card_w, card_h = 460, 300

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#161b22" />
    </linearGradient>
    <linearGradient id="hdr" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1f6feb" />
      <stop offset="50%" stop-color="#8b5cf6" />
      <stop offset="100%" stop-color="#34d399" />
    </linearGradient>
    <linearGradient id="box" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1c2128" />
      <stop offset="100%" stop-color="#151b23" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Card background -->
  <rect width="{card_w}" height="{card_h}" rx="14" fill="url(#bg)" stroke="#30363d" stroke-width="1.5" />

  <!-- Top gradient bar -->
  <rect x="0" y="0" width="{card_w}" height="6" rx="14" fill="url(#hdr)" />
  <rect x="0" y="6" width="{card_w}" height="0" fill="url(#hdr)" />

  <!-- Avatar -->
  <clipPath id="clip">
    <circle cx="52" cy="52" r="26" />
  </clipPath>'''

    if avatar_uri:
        svg += f'''
  <image href="{avatar_uri}" x="26" y="26" width="52" height="52" clip-path="url(#clip)" />
  <circle cx="52" cy="52" r="26" fill="none" stroke="#30363d" stroke-width="2" />'''
    else:
        svg += f'''
  <circle cx="52" cy="52" r="26" fill="#1f6feb" />
  <text x="52" y="59" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="20" font-weight="700" fill="#fff">{USERNAME[0].upper()}</text>'''

    svg += f'''
  <!-- Username -->
  <text x="92" y="44" font-family="Segoe UI, sans-serif" font-size="20" font-weight="700" fill="#e6edf3">{escape(USERNAME)}</text>
  <text x="92" y="64" font-family="Segoe UI, sans-serif" font-size="13" fill="#8b949e">{escape(user.get('bio', 'Glimmer·Journey') or 'Glimmer·Journey')}</text>

  <!-- Stats grid -->
  <rect x="20" y="96" width="{card_w - 40}" height="1" fill="#30363d" />

  <!-- Contribution ring -->
  <circle cx="80" cy="200" r="42" fill="none" stroke="#21262d" stroke-width="8" />'''

    # Calculate ring progress
    ring_val = min(total_contributions, 100)
    ring_circumference = 2 * 3.14159 * 42
    ring_offset = ring_circumference * (1 - ring_val / 100)

    svg += f'''
  <circle cx="80" cy="200" r="42" fill="none" stroke="url(#hdr)" stroke-width="8" stroke-dasharray="{ring_circumference}" stroke-dashoffset="{ring_offset}" stroke-linecap="round" transform="rotate(-90 80 200)" />
  <text x="80" y="198" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="22" font-weight="700" fill="#e6edf3">{total_contributions}</text>
  <text x="80" y="214" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="10" fill="#8b949e">Total</text>

  <!-- Stats items -->
'''

    x_start = 140
    y_start = 140
    col_w = 145
    row_h = 75

    for i, (emoji, label, value, color) in enumerate(stats_data):
        col = i % 2
        row = i // 2
        x = x_start + col * col_w
        y = y_start + row * row_h

        svg += f'''
  <rect x="{x}" y="{y}" width="130" height="58" rx="10" fill="url(#box)" stroke="#21262d" stroke-width="1" />
  <text x="{x + 12}" y="{y + 22}" font-family="Segoe UI, sans-serif" font-size="18">{emoji}</text>
  <text x="{x + 36}" y="{y + 22}" font-family="Segoe UI, sans-serif" font-size="12" fill="#8b949e">{label}</text>
  <text x="{x + 12}" y="{y + 46}" font-family="Segoe UI, sans-serif" font-size="22" font-weight="700" fill="{color}">{value}</text>'''

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

    card_w, card_h = 460, 42 + len(top) * 36 + 20

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{card_w}" height="{card_h}" viewBox="0 0 {card_w} {card_h}">
  <defs>
    <linearGradient id="lbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#161b22" />
    </linearGradient>
    <linearGradient id="lhdr" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f0c040" />
      <stop offset="50%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#8b5cf6" />
    </linearGradient>
  </defs>

  <rect width="{card_w}" height="{card_h}" rx="14" fill="url(#lbg)" stroke="#30363d" stroke-width="1.5" />
  <rect x="0" y="0" width="{card_w}" height="6" rx="14" fill="url(#lhdr)" />

  <text x="24" y="30" font-family="Segoe UI, sans-serif" font-size="16" font-weight="700" fill="#e6edf3">📊 Most Used Languages</text>
'''

    bar_max_w = 260
    y = 48

    for lang, count in top:
        pct = count / total * 100
        color = LANG_COLORS.get(lang, "#6e7681")
        w = int(bar_max_w * pct / 100)

        svg += f'''
  <rect x="24" y="{y}" width="10" height="10" rx="3" fill="{color}" />
  <text x="40" y="{y + 9}" font-family="Segoe UI, sans-serif" font-size="12" fill="#e6edf3">{escape(lang)}</text>
  <text x="340" y="{y + 9}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="12" fill="#8b949e">{pct:.1f}%</text>
  <rect x="350" y="{y + 1}" width="90" height="8" rx="4" fill="#21262d" />
  <rect x="350" y="{y + 1}" width="{int(90 * pct / 100)}" height="8" rx="4" fill="{color}" />'''
        y += 34

    svg += '\n</svg>'
    return svg


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching user data...")
    user = api(f"/users/{USERNAME}")

    print("Fetching avatar...")
    avatar_uri = fetch_avatar_base64(user.get("avatar_url", ""))

    print("Fetching repos...")
    repos = api(f"/users/{USERNAME}/repos?per_page=100&sort=updated")

    page = 2
    while True:
        page_repos = api(f"/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated")
        if not page_repos:
            break
        repos.extend(page_repos)
        page += 1

    print("Calculating language stats...")
    lang_data = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            repo_langs = api(repo["url"] + "/languages")
            for lang, bytes_count in repo_langs.items():
                lang_data[lang] = lang_data.get(lang, 0) + bytes_count
        except Exception:
            pass

    print(f"Found {len(repos)} repos, {len(lang_data)} languages")

    stats_svg = generate_stats_svg(user, repos, avatar_uri)
    with open(os.path.join(OUTPUT_DIR, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg)
    print(f"✅ stats.svg ({len(stats_svg)} bytes)")

    langs_svg = generate_langs_svg(lang_data)
    with open(os.path.join(OUTPUT_DIR, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(langs_svg)
    print(f"✅ top-langs.svg ({len(langs_svg)} bytes)")


if __name__ == "__main__":
    main()
