#!/usr/bin/env python3
"""Generate beautiful GitHub stats SVGs (white theme)."""

import json
import os
import urllib.request
import base64

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

T = {
    "bg": "#ffffff", "card": "#f6f8fa", "border": "#d0d7de",
    "title": "#24292f", "text": "#24292f", "label": "#57606a",
}


def api(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetch_avatar(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return f"data:image/png;base64,{base64.b64encode(resp.read()).decode()}"
    except Exception:
        return None


def generate_stats_svg(user, repos, avatar_uri=None):
    stars = sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))
    forks = sum(r.get("forks_count", 0) for r in repos if not r.get("fork"))
    repos_n = user.get("public_repos", 0)
    followers = user.get("followers", 0)

    data = [
        ("⭐", "Stars", str(stars), "#d4a72c"),
        ("⑂", "Forks", str(forks), "#8250df"),
        ("📦", "Repos", str(repos_n), "#0969da"),
        ("👥", "Followers", str(followers), "#1a7f37"),
    ]

    cw, ch = 460, 300

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{ch}" viewBox="0 0 {cw} {ch}">
  <defs>
    <linearGradient id="hdr" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0969da" />
      <stop offset="50%" stop-color="#8250df" />
      <stop offset="100%" stop-color="#1a7f37" />
    </linearGradient>
    <clipPath id="clip"><circle cx="52" cy="52" r="26" /></clipPath>
  </defs>

  <rect width="{cw}" height="{ch}" rx="14" fill="{T['bg']}" stroke="{T['border']}" stroke-width="1.5" />
  <rect x="0" y="0" width="{cw}" height="6" rx="14" fill="url(#hdr)" />'''

    if avatar_uri:
        svg += f'''
  <image href="{avatar_uri}" x="26" y="26" width="52" height="52" clip-path="url(#clip)" />
  <circle cx="52" cy="52" r="26" fill="none" stroke="{T['border']}" stroke-width="2" />'''
    else:
        svg += f'''
  <circle cx="52" cy="52" r="26" fill="#0969da" />
  <text x="52" y="59" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="20" font-weight="700" fill="#fff">{USERNAME[0].upper()}</text>'''

    svg += f'''
  <text x="92" y="44" font-family="Segoe UI,sans-serif" font-size="20" font-weight="700" fill="{T['title']}">{escape(USERNAME)}</text>
  <text x="92" y="64" font-family="Segoe UI,sans-serif" font-size="13" fill="{T['label']}">{escape(user.get('bio','') or 'Glimmer·Journey')}</text>
  <rect x="20" y="96" width="{cw - 40}" height="1" fill="{T['border']}" />

  <circle cx="80" cy="200" r="42" fill="none" stroke="#eaeef2" stroke-width="8" />'''

    total = stars + repos_n + followers + forks
    rv = min(total, 100)
    rc = 2 * 3.14159 * 42
    ro = rc * (1 - rv / 100)
    svg += f'''
  <circle cx="80" cy="200" r="42" fill="none" stroke="url(#hdr)" stroke-width="8" stroke-dasharray="{rc}" stroke-dashoffset="{ro}" stroke-linecap="round" transform="rotate(-90 80 200)" />
  <text x="80" y="198" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="22" font-weight="700" fill="{T['text']}">{total}</text>
  <text x="80" y="214" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10" fill="{T['label']}">Total</text>'''

    for i, (e, l, v, c) in enumerate(data):
        col, row = i % 2, i // 2
        x, y = 140 + col * 145, 140 + row * 75
        svg += f'''
  <rect x="{x}" y="{y}" width="130" height="58" rx="10" fill="#fff" stroke="{T['border']}" stroke-width="1" />
  <text x="{x + 12}" y="{y + 22}" font-family="Segoe UI,sans-serif" font-size="18">{e}</text>
  <text x="{x + 36}" y="{y + 22}" font-family="Segoe UI,sans-serif" font-size="12" fill="{T['label']}">{l}</text>
  <text x="{x + 12}" y="{y + 46}" font-family="Segoe UI,sans-serif" font-size="22" font-weight="700" fill="{c}">{v}</text>'''

    svg += '\n</svg>'
    return svg


def generate_langs_svg(langs_data):
    total = sum(langs_data.values())
    if total == 0:
        langs_data = {"Go": 1}
        total = 1

    sorted_langs = sorted(langs_data.items(), key=lambda x: x[1], reverse=True)

    # Show ALL languages (up to 15), keeping only those >= 0.5%
    top = [(l, c) for l, c in sorted_langs if c / total >= 0.005]
    if len(top) < len(sorted_langs) and len(sorted_langs) > 15:
        others = sum(c for l, c in sorted_langs[15:])
        if others / total >= 0.005:
            top = top[:14] + [("Other", others)]
    else:
        top = top[:15] if len(top) > 15 else top

    cw, ch = 340, 40 + len(top) * 38 + 16

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{ch}" viewBox="0 0 {cw} {ch}">
  <defs>
    <linearGradient id="lhdr" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#d4a72c" />
      <stop offset="50%" stop-color="#0969da" />
      <stop offset="100%" stop-color="#8250df" />
    </linearGradient>
  </defs>

  <rect width="{cw}" height="{ch}" rx="14" fill="{T['bg']}" stroke="{T['border']}" stroke-width="1.5" />
  <rect x="0" y="0" width="{cw}" height="6" rx="14" fill="url(#lhdr)" />
  <text x="20" y="30" font-family="Segoe UI,sans-serif" font-size="15" font-weight="700" fill="{T['title']}">📊 Languages</text>'''

    bar_w = 180
    y = 52

    for lang, count in top:
        pct = count / total * 100
        color = LANG_COLORS.get(lang, "#57606a")
        bw = int(bar_w * pct / 100) or 1

        svg += f'''
  <rect x="20" y="{y}" width="8" height="8" rx="2" fill="{color}" />
  <text x="34" y="{y + 7}" font-family="Segoe UI,sans-serif" font-size="12" fill="{T['text']}">{escape(lang)}</text>
  <text x="{cw - 20}" y="{y + 7}" text-anchor="end" font-family="Segoe UI,sans-serif" font-size="11" fill="{T['label']}">{pct:.1f}%</text>
  <rect x="34" y="{y + 14}" width="{bar_w}" height="4" rx="2" fill="#eaeef2" />
  <rect x="34" y="{y + 14}" width="{bw}" height="4" rx="2" fill="{color}" />'''
        y += 36

    svg += '\n</svg>'
    return svg


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Fetching user data...")
    user = api(f"/users/{USERNAME}")
    print("Fetching avatar...")
    avatar_uri = fetch_avatar(user.get("avatar_url", ""))

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

    with open(os.path.join(OUTPUT_DIR, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(generate_stats_svg(user, repos, avatar_uri))

    with open(os.path.join(OUTPUT_DIR, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(generate_langs_svg(lang_data))

    print("✅ Done")


if __name__ == "__main__":
    main()
