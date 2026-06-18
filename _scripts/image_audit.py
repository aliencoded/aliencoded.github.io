#!/usr/bin/env python3
"""
image_audit.py — Standalone Meta Currents image auditor and fixer.

What it does (no Claude required):
  1. Scans every file in _articles/ and extracts (image, categories) pairs.
  2. Builds a "category profile" for every unique image URL — the set of topic
     tags articles that use it carry, weighted by frequency.
  3. HEAD-checks each unique URL once (concurrent), caching results to
     .image_audit_cache.json so re-runs are fast.
  4. Emits a self-contained HTML report (image_audit_report.html) at the repo
     root. Each article gets a card showing its title, categories, the live
     Unsplash thumbnail (or 'BROKEN' if it 404'd), and — if broken — the
     replacement URL the script would pick from the verified pool.
  5. With --fix, rewrites every article whose image is broken or missing,
     swapping in the best topic-matched replacement from the verified pool.

The replacement picker is deterministic-ish: it scores every verified URL
against the article's categories using Jaccard overlap on the URL's
category profile, breaks ties by reuse-count (less-used preferred for
variety), and falls back to a section-bucket default if nothing scores.

Usage:
    python3 _scripts/image_audit.py            # audit + report only
    python3 _scripts/image_audit.py --fix      # also rewrite broken articles
    python3 _scripts/image_audit.py --refresh  # ignore HTTP cache, re-check all

Open image_audit_report.html in a browser after either mode to eyeball whether
the chosen images make sense for the articles.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import html
import json
import re
import sys
import time
import urllib.request
import urllib.error
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "_articles"
CACHE_FILE = ROOT / ".image_audit_cache.json"
REPORT_FILE = ROOT / "image_audit_report.html"

# Section buckets used as a tie-break / fallback. Maps a section name (one of
# the article categories) to topic keywords that should appear in a good
# replacement URL's category profile.
SECTION_HINTS: dict[str, list[str]] = {
    "geopolitics": ["middle-east", "diplomacy", "international-relations", "war", "iran"],
    "us": ["politics", "congress", "white-house", "election"],
    "business": ["markets", "finance", "trade", "economy", "energy"],
    "tech": ["ai", "tech", "cybersecurity", "data"],
    "global": ["africa", "asia", "europe", "climate", "humanitarian"],
    "satire": ["humor", "satire"],
    "people": ["people"],
}

# Universal junk tags that should never drive image matching.
NOISE_TAGS = {"articles", "index"}

IMAGE_RE = re.compile(r"^image:\s*(\S+)\s*$", re.MULTILINE)
CATS_RE = re.compile(r"^categories:\s*\[([^\]]*)\]", re.MULTILINE)
TITLE_RE = re.compile(r'^title:\s*"([^"]*)"', re.MULTILINE)


# ---------- parsing ----------

def parse_article(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # Front matter only — split on the first '---' pair.
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 4)
    front = text[:end] if end != -1 else text
    image_m = IMAGE_RE.search(front)
    cats_m = CATS_RE.search(front)
    title_m = TITLE_RE.search(front)
    cats = []
    if cats_m:
        cats = [c.strip().strip('"').strip("'") for c in cats_m.group(1).split(",")]
        cats = [c for c in cats if c]
    return {
        "path": path,
        "title": title_m.group(1) if title_m else path.name,
        "image": image_m.group(1) if image_m else None,
        "categories": cats,
        "topic_tags": [c for c in cats if c not in NOISE_TAGS],
    }


def load_corpus() -> list[dict]:
    return [a for a in (parse_article(p) for p in sorted(ARTICLES_DIR.glob("*.md"))) if a]


# ---------- URL verification ----------

def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache: dict) -> None:
    CACHE_FILE.write_text(json.dumps(cache, indent=2, sort_keys=True))


def check_url(url: str, timeout: float = 8.0) -> tuple[int, str]:
    """Return (status_code, note). 0 means transport error."""
    req = urllib.request.Request(url, method="HEAD", headers={
        "User-Agent": "Mozilla/5.0 (compatible; MetaCurrentsImageAudit/1.0)"
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, "ok"
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)
    except urllib.error.URLError as e:
        return 0, str(e.reason)
    except Exception as e:  # noqa: BLE001
        return 0, type(e).__name__


def verify_urls(urls: list[str], cache: dict, refresh: bool, max_workers: int = 16) -> dict:
    """Returns {url: {"status": int, "note": str, "checked_at": ts}}.
    Cached entries are kept unless refresh=True or older than 7 days.
    """
    out: dict = {}
    now = time.time()
    ttl = 7 * 24 * 3600
    todo = []
    for u in urls:
        cached = cache.get(u)
        if (not refresh) and cached and now - cached.get("checked_at", 0) < ttl:
            out[u] = cached
        else:
            todo.append(u)
    if not todo:
        return out
    print(f"  Checking {len(todo)} URLs (concurrent)...", flush=True)
    with futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for url, (status, note) in zip(todo, pool.map(lambda u: check_url(u), todo)):
            out[url] = {"status": status, "note": note, "checked_at": now}
            cache[url] = out[url]
    return out


# ---------- URL category profiles ----------

def build_url_profiles(articles: list[dict]) -> dict[str, Counter]:
    """For each image URL, the multiset of topic tags from articles using it."""
    profiles: dict[str, Counter] = defaultdict(Counter)
    for a in articles:
        if not a["image"]:
            continue
        for tag in a["topic_tags"]:
            profiles[a["image"]][tag] += 1
    return profiles


def score_match(article_tags: list[str], url_profile: Counter, sections: set[str]) -> float:
    if not article_tags or not url_profile:
        return 0.0
    article_set = set(article_tags)
    profile_set = set(url_profile)
    intersect = article_set & profile_set
    if not intersect:
        # Fallback bonus if URL is heavily used by the same section.
        section_overlap = sections & profile_set
        return 0.001 * sum(url_profile[s] for s in section_overlap)
    # Weight by how prominent each shared tag is in the URL's history.
    overlap_weight = sum(url_profile[t] for t in intersect)
    union = len(article_set | profile_set)
    return overlap_weight / max(union, 1)


def pick_replacement(
    article: dict,
    verified_pool: list[str],
    profiles: dict[str, Counter],
    usage_counts: Counter,
) -> str | None:
    tags = article["topic_tags"]
    sections = {c for c in article["categories"] if c in SECTION_HINTS}
    # Expand tags with section hints so e.g. a tech article without explicit
    # tags still matches the AI/tech cluster.
    hint_tags = list(tags)
    for s in sections:
        hint_tags.extend(SECTION_HINTS[s])

    scored = []
    for url in verified_pool:
        s = score_match(hint_tags, profiles.get(url, Counter()), sections)
        if s > 0:
            # Tiebreak: prefer less-used URLs.
            scored.append((s, -usage_counts[url], url))
    if not scored:
        # Last resort: any verified URL whose profile has the same section.
        for url in verified_pool:
            prof_sections = sections & set(profiles.get(url, Counter()))
            if prof_sections:
                scored.append((0.0001, -usage_counts[url], url))
    if not scored:
        return verified_pool[0] if verified_pool else None
    scored.sort(reverse=True)
    return scored[0][2]


# ---------- report ----------

def thumb_url(url: str, w: int = 320) -> str:
    """Rewrite Unsplash URL to a smaller thumbnail (Unsplash CDN supports w=)."""
    if "?" in url:
        base, q = url.split("?", 1)
        parts = [p for p in q.split("&") if not p.startswith("w=")]
        parts.append(f"w={w}")
        return f"{base}?{'&'.join(parts)}"
    return f"{url}?w={w}&auto=format&fit=crop"


def render_report(items: list[dict]) -> str:
    rows = []
    good = sum(1 for i in items if i["verdict"] == "ok")
    fixed = sum(1 for i in items if i["verdict"] == "replaced")
    broken = sum(1 for i in items if i["verdict"] == "broken-no-replacement")
    missing = sum(1 for i in items if i["verdict"] == "missing")
    for i in items:
        v = i["verdict"]
        color = {
            "ok": "#0a7a2a",
            "replaced": "#b36b00",
            "broken-no-replacement": "#a40000",
            "missing": "#a40000",
            "mismatch": "#6b00b3",
        }[v]
        tags_html = " ".join(f'<span class="tag">{html.escape(t)}</span>' for t in i["categories"])
        original_block = ""
        if i["original_image"]:
            original_block = (
                f'<div class="img-block"><div class="lbl">original ({i["original_status"]})</div>'
                f'<img loading="lazy" src="{html.escape(thumb_url(i["original_image"]))}" alt=""></div>'
            )
        replacement_block = ""
        if i["replacement"] and i["replacement"] != i["original_image"]:
            replacement_block = (
                f'<div class="img-block"><div class="lbl">replacement</div>'
                f'<img loading="lazy" src="{html.escape(thumb_url(i["replacement"]))}" alt=""></div>'
            )
        rows.append(
            f"""
<div class="card">
  <div class="head">
    <div class="title">{html.escape(i["title"])}</div>
    <div class="verdict" style="background:{color}">{v}</div>
  </div>
  <div class="meta">{html.escape(i["path"])}</div>
  <div class="tags">{tags_html}</div>
  <div class="imgs">
    {original_block}
    {replacement_block}
  </div>
</div>
"""
        )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Meta Currents image audit</title>
<style>
  body {{ font: 14px/1.4 -apple-system, system-ui, sans-serif; margin: 0; background:#f5f5f7; color:#111; }}
  header {{ background:#0b2c4e; color:#fff; padding:16px 24px; position:sticky; top:0; z-index:10; }}
  header h1 {{ margin:0; font-size:18px; }}
  header .stats {{ margin-top:6px; font-size:13px; opacity:.92 }}
  .stats span {{ display:inline-block; margin-right:14px }}
  main {{ padding:18px; display:grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap:14px; max-width:1600px; margin:0 auto; }}
  .card {{ background:#fff; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.07); overflow:hidden; }}
  .head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:8px; padding:10px 12px 4px; }}
  .title {{ font-weight:600; font-size:14.5px; line-height:1.3 }}
  .verdict {{ font-size:10px; color:#fff; padding:3px 7px; border-radius:3px; text-transform:uppercase; letter-spacing:.04em; white-space:nowrap; }}
  .meta {{ font-family: ui-monospace, monospace; font-size:11px; color:#666; padding:0 12px 4px; word-break:break-all; }}
  .tags {{ padding:0 12px 8px }}
  .tag {{ display:inline-block; background:#eef; color:#225; border-radius:3px; padding:1px 6px; font-size:11px; margin-right:4px; margin-bottom:2px; }}
  .imgs {{ display:flex; gap:6px; padding:0 8px 8px }}
  .img-block {{ flex:1; min-width:0 }}
  .img-block img {{ width:100%; height:160px; object-fit:cover; border-radius:4px; background:#ddd; display:block }}
  .lbl {{ font-size:10px; text-transform:uppercase; letter-spacing:.05em; color:#666; margin:2px 0 3px }}
  details {{ background:#fff; border-radius:6px; margin-bottom:10px; padding:6px 12px }}
  details summary {{ cursor:pointer; font-weight:600; padding:4px 0 }}
</style></head>
<body>
<header>
  <h1>Meta Currents — image audit</h1>
  <div class="stats">
    <span><b>{len(items)}</b> articles</span>
    <span><b>{good}</b> ok</span>
    <span><b>{fixed}</b> replaced</span>
    <span><b>{broken}</b> broken-no-replacement</span>
    <span><b>{missing}</b> missing</span>
  </div>
</header>
<main>
{"".join(rows)}
</main></body></html>
"""


# ---------- file rewrite ----------

def replace_image_in_file(path: Path, new_url: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 4)
    if end == -1:
        return False
    front, rest = text[:end], text[end:]
    if IMAGE_RE.search(front):
        new_front = IMAGE_RE.sub(f"image: {new_url}", front, count=1)
    else:
        # Insert before the closing front matter delimiter (which we stripped).
        new_front = front.rstrip() + f"\nimage: {new_url}\n"
    path.write_text(new_front + rest, encoding="utf-8")
    return True


# ---------- driver ----------

def main() -> int:
    parser = argparse.ArgumentParser(description="Audit & fix Meta Currents article images.")
    parser.add_argument("--fix", action="store_true", help="Rewrite articles with broken/missing images.")
    parser.add_argument("--refresh", action="store_true", help="Re-check every URL, ignore cache.")
    parser.add_argument("--limit", type=int, default=0, help="Stop after N articles (debug).")
    parser.add_argument("--report-only-changes", action="store_true",
                        help="Only include articles in the report whose verdict is not 'ok'.")
    parser.add_argument("--flag-mismatches", action="store_true",
                        help="Treat articles whose image profile barely overlaps their topic tags as 'mismatch'.")
    parser.add_argument("--mismatch-threshold", type=float, default=0.0,
                        help="Score below this counts as a mismatch. 0 = no overlap at all.")
    args = parser.parse_args()

    print("Loading corpus...")
    articles = load_corpus()
    if args.limit:
        articles = articles[: args.limit]
    print(f"  {len(articles)} articles parsed")

    profiles = build_url_profiles(articles)
    usage_counts = Counter(a["image"] for a in articles if a["image"])
    unique_urls = sorted(usage_counts)
    print(f"  {len(unique_urls)} unique image URLs in corpus")

    cache = load_cache()
    print("Verifying URLs...")
    statuses = verify_urls(unique_urls, cache, refresh=args.refresh)
    save_cache(cache)

    good_urls = {u for u, s in statuses.items() if s["status"] == 200}
    print(f"  {len(good_urls)}/{len(unique_urls)} URLs return 200")

    verified_pool = sorted(good_urls)
    items = []
    rewrites = 0
    for a in articles:
        original = a["image"]
        original_status = "200" if original in good_urls else (
            f"HTTP {statuses[original]['status']}" if original in statuses else "missing"
        )
        verdict = "ok"
        replacement = None
        if not original:
            verdict = "missing"
            replacement = pick_replacement(a, verified_pool, profiles, usage_counts)
            if replacement is None:
                verdict = "broken-no-replacement"
        elif original not in good_urls:
            replacement = pick_replacement(a, verified_pool, profiles, usage_counts)
            if replacement and replacement != original:
                verdict = "replaced"
            else:
                verdict = "broken-no-replacement"

        # Mismatch scan: even if HTTP 200, the image's history may not match.
        mismatch_score = None
        if args.flag_mismatches and verdict == "ok" and original:
            hint_tags = list(a["topic_tags"])
            sections = {c for c in a["categories"] if c in SECTION_HINTS}
            for s in sections:
                hint_tags.extend(SECTION_HINTS[s])
            mismatch_score = score_match(hint_tags, profiles.get(original, Counter()), sections)
            if mismatch_score <= args.mismatch_threshold:
                replacement = pick_replacement(a, verified_pool, profiles, usage_counts)
                if replacement and replacement != original:
                    verdict = "mismatch"

        if args.fix and replacement and verdict in ("replaced", "missing", "mismatch"):
            if replace_image_in_file(a["path"], replacement):
                rewrites += 1

        items.append({
            "title": a["title"],
            "path": str(a["path"].relative_to(ROOT)),
            "categories": a["categories"],
            "original_image": original,
            "original_status": original_status,
            "replacement": replacement,
            "verdict": verdict,
        })

    if args.report_only_changes:
        items = [i for i in items if i["verdict"] != "ok"]

    REPORT_FILE.write_text(render_report(items), encoding="utf-8")
    print(f"Report written: {REPORT_FILE.relative_to(ROOT)}")
    if args.fix:
        print(f"Rewrote {rewrites} article files")

    # Console summary.
    counts = Counter(i["verdict"] for i in items)
    print("Verdict summary:", dict(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
