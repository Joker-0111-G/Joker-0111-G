#!/usr/bin/env python3
"""Generate GitHub stats SVGs - uses gh CLI for reliable API access."""

import json, os, subprocess, sys, base64

USERNAME = "Joker-0111-G"
OUT = "assets"

LANG_COLORS = {
    "Go": "#00ADD8", "Python": "#3572A5", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#563d7c",
    "C++": "#f34b7d", "C": "#555555", "Java": "#b07219",
    "Shell": "#89e051", "MATLAB": "#e16737", "Jupyter Notebook":"#DA5B0F",
    "Wolfram Language":"#DD1100",
}

def gh(path):
    """Use gh CLI (pre-installed on GitHub Actions) to call API."""
    r = subprocess.run(["gh", "api", path, "--jq", "."], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ⚠️  gh error: {r.stderr.strip()}")
        return None
    return json.loads(r.stdout)

def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;")

def fetch_avatar(url):
    try:
        r = subprocess.run(["curl", "-sL", url], capture_output=True)
        return "data:image/png;base64," + base64.b64encode(r.stdout).decode()
    except: return None

def main():
    os.makedirs(OUT, exist_ok=True)
    print("1/5 Fetching user...")
    user = gh(f"/users/{USERNAME}")
    if not user: sys.exit(1)
    print(f"   {user['login']}, {user['public_repos']} repos")

    avatar = fetch_avatar(user.get("avatar_url",""))

    print("2/5 Fetching repos (gh api)...")
    repos = gh(f"/users/{USERNAME}/repos?per_page=100")
    if not repos: sys.exit(1)
    print(f"   Got {len(repos)} repos total")

    # Filter non-forks
    own = [r for r in repos if not r.get("fork")]
    print(f"   {len(own)} own repos")

    print("3/5 Fetching languages for each repo...")
    all_langs = {}
    for r in own:
        name = r["name"]
        print(f"   [{name}] main_lang={r.get('language','?')}", end="")
        langs = gh(r["url"] + "/languages")
        if langs and isinstance(langs, dict):
            for lang, bc in langs.items():
                all_langs[lang] = all_langs.get(lang, 0) + bc
            print(f" → {len(langs)} languages")
        else:
            print(f" → EMPTY")

    print(f"4/5 Aggregate: {len(all_langs)} languages")
    for lang, bc in sorted(all_langs.items(), key=lambda x: -x[1]):
        print(f"   {lang}: {bc}")

    # ── Stats SVG ──
    stars = sum(r.get("stargazers_count",0) for r in own)
    forks = sum(r.get("forks_count",0) for r in own)
    data = [("⭐","Stars",str(stars),"#d4a72c"),("⑂","Forks",str(forks),"#8250df"),
            ("📦","Repos",str(user["public_repos"]),"#0969da"),("👥","Followers",str(user["followers"]),"#1a7f37")]
    cw,ch = 460,300
    svg1 = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{ch}" viewBox="0 0 {cw} {ch}">
  <defs><linearGradient id="h" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#0969da"/><stop offset="50%" stop-color="#8250df"/><stop offset="100%" stop-color="#1a7f37"/></linearGradient>
    <clipPath id="c"><circle cx="52" cy="52" r="26"/></clipPath></defs>
  <rect width="{cw}" height="{ch}" rx="14" fill="#fff" stroke="#d0d7de" stroke-width="1.5"/>
  <rect x="0" y="0" width="{cw}" height="6" rx="14" fill="url(#h)"/>'''
    if avatar:
        svg1 += f'\n  <image href="{avatar}" x="26" y="26" width="52" height="52" clip-path="url(#c)"/>\n  <circle cx="52" cy="52" r="26" fill="none" stroke="#d0d7de" stroke-width="2"/>'
    else:
        svg1 += f'\n  <circle cx="52" cy="52" r="26" fill="#0969da"/>\n  <text x="52" y="59" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="20" font-weight="700" fill="#fff">{USERNAME[0].upper()}</text>'
    svg1 += f'''
  <text x="92" y="44" font-family="Segoe UI,sans-serif" font-size="20" font-weight="700" fill="#24292f">{esc(USERNAME)}</text>
  <text x="92" y="64" font-family="Segoe UI,sans-serif" font-size="13" fill="#57606a">{esc(user.get("bio","") or "Glimmer·Journey")}</text>
  <rect x="20" y="96" width="420" height="1" fill="#d0d7de"/>
  <circle cx="80" cy="200" r="42" fill="none" stroke="#eaeef2" stroke-width="8"/>'''
    ttl = stars+forks+user["public_repos"]+user["followers"]
    rc = 2*3.14159*42; ro = rc*(1-min(ttl,100)/100) if ttl<100 else 0
    svg1 += f'''
  <circle cx="80" cy="200" r="42" fill="none" stroke="url(#h)" stroke-width="8" stroke-dasharray="{rc}" stroke-dashoffset="{ro}" stroke-linecap="round" transform="rotate(-90 80 200)"/>
  <text x="80" y="198" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="22" font-weight="700" fill="#24292f">{ttl}</text>
  <text x="80" y="214" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10" fill="#57606a">Total</text>'''
    for i,(e,l,v,c) in enumerate(data):
        x,y = 140+(i%2)*145, 140+(i//2)*75
        svg1 += f'''
  <rect x="{x}" y="{y}" width="130" height="58" rx="10" fill="#fff" stroke="#d0d7de" stroke-width="1"/>
  <text x="{x+12}" y="{y+22}" font-family="Segoe UI,sans-serif" font-size="18">{e}</text>
  <text x="{x+36}" y="{y+22}" font-family="Segoe UI,sans-serif" font-size="12" fill="#57606a">{l}</text>
  <text x="{x+12}" y="{y+46}" font-family="Segoe UI,sans-serif" font-size="22" font-weight="700" fill="{c}">{v}</text>'''
    svg1 += "\n</svg>"
    with open(os.path.join(OUT,"stats.svg"),"w",encoding="utf-8") as f: f.write(svg1)
    print(f"5/5 ✅ stats.svg ({len(svg1)} bytes)")

    # ── Languages SVG ──
    total = sum(all_langs.values()) or 1
    top = sorted(all_langs.items(), key=lambda x:-x[1])[:15]
    cw2,ch2 = 340, 40+len(top)*38+16
    svg2 = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{cw2}" height="{ch2}" viewBox="0 0 {cw2} {ch2}">
  <defs><linearGradient id="lh" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#d4a72c"/><stop offset="50%" stop-color="#0969da"/><stop offset="100%" stop-color="#8250df"/></linearGradient></defs>
  <rect width="{cw2}" height="{ch2}" rx="14" fill="#fff" stroke="#d0d7de" stroke-width="1.5"/>
  <rect x="0" y="0" width="{cw2}" height="6" rx="14" fill="url(#lh)"/>
  <text x="20" y="30" font-family="Segoe UI,sans-serif" font-size="15" font-weight="700" fill="#24292f">📊 Languages</text>'''
    y = 52
    for lang, count in top:
        pct, color = count/total*100, LANG_COLORS.get(lang,"#57606a")
        bw = int(180*pct/100) or 1
        svg2 += f'''
  <rect x="20" y="{y}" width="8" height="8" rx="2" fill="{color}"/>
  <text x="34" y="{y+7}" font-family="Segoe UI,sans-serif" font-size="12" fill="#24292f">{esc(lang)}</text>
  <text x="320" y="{y+7}" text-anchor="end" font-family="Segoe UI,sans-serif" font-size="11" fill="#57606a">{pct:.1f}%</text>
  <rect x="34" y="{y+14}" width="180" height="4" rx="2" fill="#eaeef2"/>
  <rect x="34" y="{y+14}" width="{bw}" height="4" rx="2" fill="{color}"/>'''
        y += 36
    svg2 += "\n</svg>"
    with open(os.path.join(OUT,"top-langs.svg"),"w",encoding="utf-8") as f: f.write(svg2)
    print(f"5/5 ✅ top-langs.svg ({len(svg2)} bytes) - {len(top)} languages shown")

if __name__ == "__main__":
    main()
