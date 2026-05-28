#!/usr/bin/env python3
"""Generate beautiful GitHub stats SVGs (white theme)."""

import json
import os
import urllib.request
import base64
import sys

USERNAME = "Joker-0111-G"
OUTPUT_DIR = "assets"

LANG_COLORS = {
    "Go": "#00ADD8", "Python": "#3572A5", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#563d7c",
    "C++": "#f34b7d", "C": "#555555", "Java": "#b07219",
    "Shell": "#89e051", "Jupyter Notebook": "#DA5B0F",
    "Wolfram Language": "#DD1100", "MATLAB": "#e16737",
    "Rust": "#dea584", "Vue": "#41b883",
}


def api(path):
    """Call GitHub API with auth token from env if available."""
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            if not body:
                return None
            return json.loads(body)
    except urllib.error.HTTPError as e:
        print(f"  ⚠️  HTTP {e.code} for {path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ⚠️  {e}", file=sys.stderr)
        return None


def api_json(path):
    """Similar to api() but returns raw JSON string for debugging."""
    return api(path)


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetch_avatar(url):
    """Fetch avatar image as base64 data URI."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "stats-script"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            b64 = base64.b64encode(resp.read()).decode()
            return f"data:image/png;base64,{b64}"
    except Exception:
        return None


def get_repos():
    """Fetch all non-fork repos with pagination."""
    repos = []
    page = 1
    while True:
        data = api(f"/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
        if not data or not isinstance(data, list):
            break
        if len(data) == 0:
            break
        repos.extend(data)
        page += 1
        if len(data) < 100:
            break
    return repos


def get_languages(repos):
    """Aggregate language bytes across all non-fork repos."""
    lang_data = {}
    count = 0
    for repo in repos:
        if repo.get("fork"):
            continue
        count += 1
        # repo["languages_url"] is the full API URL for languages
        lang_url = repo.get("languages_url", "")
        if not lang_url:
            continue
        try:
            data = api_json(repo["url"] + "/languages")
            if data and isinstance(data, dict):
                for lang, bc in data.items():
                    lang_data[lang] = lang_data.get(lang, 0) + bc
        except Exception:
            pass
    print(f"  Processed {count} repos, found {len(lang_data)} languages")
    return lang_data


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

  <rect width="{cw}" height="{ch}" rx="14" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5" />
  <rect x="0" y="0" width="{cw}" height="6" rx="14" fill="url(#hdr)" />'''

    if avatar_uri:
        svg += f'''
  <image href="{avatar_uri}" x="26" y="26" width="52" height="52" clip-path="url(#clip)" />
  <circle cx="52" cy="52" r="26" fill="none" stroke="#d0d7de" stroke-width="2" />'''
    else:
        svg += f'''
  <circle cx="52" cy="52" r="26" fill="#0969da" />
  <text x="52" y="59" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="20" font-weight="700" fill="#fff">{USERNAME[0].upper()}</text>'''

    svg += f'''
  <text x="92" y="44" font-family="Segoe UI,sans-serif" font-size="20" font-weight="700" fill="#24292f">{escape(USERNAME)}</text>
  <text x="92" y="64" font-family="Segoe UI,sans-serif" font-size="13" fill="#57606a">{escape(user.get('bio','') or 'Glimmer·Journey')}</text>
  <rect x="20" y="96" width="{cw - 40}" height="1" fill="#d0d7de" />

  <circle cx="80" cy="200" r="42" fill="none" stroke="#eaeef2" stroke-width="8" />'''

    total = stars + repos_n + followers + forks
    rv = min(total, 100)
    rc = 2 * 3.14159 * 42
    ro = rc * (1 - rv / 100) if rv < 100 else 0
    svg += f'''
  <circle cx="80" cy="200" r="42" fill="none" stroke="url(#hdr)" stroke-width="8" stroke-dasharray="{rc}" stroke-dashoffset="{ro}" stroke-linecap="round" transform="rotate(-90 80 200)" />
  <text x="80" y="198" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="22" font-weight="700" fill="#24292f">{total}</text>
  <text x="80" y="214" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10" fill="#57606a">Total</text>'''

    for i, (e, l, v, c) in enumerate(data):
        col, row = i % 2, i // 2
        x, y = 140 + col * 145, 140 + row * 75
        svg += f'''
  <rect x="{x}" y="{y}" width="130" height="58" rx="10" fill="#ffffff" stroke="#d0d7de" stroke-width="1" />
  <text x="{x + 12}" y="{y + 22}" font-family="Segoe UI,sans-serif" font-size="18">{e}</text>
  <text x="{x + 36}" y="{y + 22}" font-family="Segoe UI,sans-serif" font-size="12" fill="#57606a">{l}</text>
  <text x="{x + 12}" y="{y + 46}" font-family="Segoe UI,sans-serif" font-size="22" font-weight="700" fill="{c}">{v}</text>'''

    svg += '\n</svg>'
    return svg


def generate_langs_svg(langs_data):
    total = sum(langs_data.values())
    if total == 0:
        langs_data = {"Go": 1}
        total = 1

    sorted_langs = sorted(langs_data.items(), key=lambda x: x[1], reverse=True)
    # Include all languages with >= 0.1% share, up to 15
    top = [(l, c) for l, c in sorted_langs if c / total >= 0.001]
    if len(top) > 15:
        top = top[:15]

    cw, ch = 340, 40 + len(top) * 38 + 16

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{ch}" viewBox="0 0 {cw} {ch}">
  <defs>
    <linearGradient id="lhdr" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#d4a72c" />
      <stop offset="50%" stop-color="#0969da" />
      <stop offset="100%" stop-color="#8250df" />
    </linearGradient>
  </defs>

  <rect width="{cw}" height="{ch}" rx="14" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5" />
  <rect x="0" y="0" width="{cw}" height="6" rx="14" fill="url(#lhdr)" />
  <text x="20" y="30" font-family="Segoe UI,sans-serif" font-size="15" font-weight="700" fill="#24292f">📊 Languages</text>'''

    bar_w = 180
    y = 52

    for lang, count in top:
        pct = count / total * 100
        color = LANG_COLORS.get(lang, "#57606a")
        bw = int(bar_w * pct / 100) or 1

        svg += f'''
  <rect x="20" y="{y}" width="8" height="8" rx="2" fill="{color}" />
  <text x="34" y="{y + 7}" font-family="Segoe UI,sans-serif" font-size="12" fill="#24292f">{escape(lang)}</text>
  <text x="{cw - 20}" y="{y + 7}" text-anchor="end" font-family="Segoe UI,sans-serif" font-size="11" fill="#57606a">{pct:.1f}%</text>
  <rect x="34" y="{y + 14}" width="{bar_w}" height="4" rx="2" fill="#eaeef2" />
  <rect x="34" y="{y + 14}" width="{bw}" height="4" rx="2" fill="{color}" />'''
        y += 36

    svg += '\n</svg>'
    return svg


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching user data...")
    user = api(f"/users/{USERNAME}")
    if not user:
        print("❌ Failed to fetch user data!")
        sys.exit(1)
    print(f"  User: {user.get('login')}, repos: {user.get('public_repos')}")

    print("Fetching avatar...")
    avatar_uri = fetch_avatar(user.get("avatar_url", ""))

    print("Fetching repos...")
    repos = get_repos()
    if not repos:
        print("❌ Failed to fetch repos!")
        sys.exit(1)
    print(f"  Total: {len(repos)} repos ({sum(1 for r in repos if r.get('fork'))} forks)")

    print("Fetching language stats...")
    lang_data = get_languages(repos)
    print(f"  Languages: {dict(sorted(lang_data.items(), key=lambda x: -x[1]))}")

    # Stats SVG
    svg1 = generate_stats_svg(user, repos, avatar_uri)
    with open(os.path.join(OUTPUT_DIR, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(svg1)
    print(f"✅ stats.svg ({len(svg1)} bytes)")

    # Languages SVG
    svg2 = generate_langs_svg(lang_data)
    with open(os.path.join(OUTPUT_DIR, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(svg2)
    print(f"✅ top-langs.svg ({len(svg2)} bytes)")

    print("✅ All done!")


if __name__ == "__main__":
    main()
