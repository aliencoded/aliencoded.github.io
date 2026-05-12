"""
Normalize the `categories:` front-matter line in every article so that all
values are lowercase + hyphenated. Collapses dupes after normalization,
preserving original order.

Examples:
  ["Middle East", "middle-east"]  -> ["middle-east"]
  ["Asia", "asia"]                -> ["asia"]
  "US"                            -> "us"
  "United States"                 -> "united-states"

Note: "US" and "United States" do NOT merge automatically — they normalize
to different slugs ("us" vs "united-states"). If you want them merged,
do a manual find/replace pass after running this script.

Idempotent: running twice has no further effect.
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ARTICLES_DIR = SCRIPT_DIR.parent / "_articles"


def slugify(value: str) -> str:
    value = value.strip().strip("'\"")
    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    value = value.strip("-").lower()
    return value


def normalize_inline_array(line):
    """Handle `categories: [a, b, "c d"]` (single-line array)."""
    m = re.match(r"^(\s*categories\s*:\s*\[)(.*?)(\]\s*)$", line)
    if not m:
        return None
    prefix, mid, suffix = m.groups()
    raw = [p for p in (s.strip() for s in mid.split(",")) if p]
    cleaned = [slugify(p) for p in raw]
    cleaned = [c for c in cleaned if c]

    seen = set()
    deduped = []
    for c in cleaned:
        if c not in seen:
            seen.add(c)
            deduped.append(c)
    return f"{prefix}{', '.join(deduped)}{suffix}"


def process(path, dry):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].strip() == "---":
        return False

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return False

    changed = False
    for i in range(1, end_idx):
        line = lines[i]
        new_line = normalize_inline_array(line)
        if new_line is not None and new_line != line.rstrip("\n") + "\n":
            new_line = new_line.rstrip() + "\n"
            if new_line != line:
                lines[i] = new_line
                changed = True

    if changed and not dry:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def main():
    dry = "--dry" in sys.argv
    if not ARTICLES_DIR.is_dir():
        print(f"No articles dir at {ARTICLES_DIR}", file=sys.stderr)
        sys.exit(1)

    files = sorted(ARTICLES_DIR.glob("*.md"))
    changed = 0
    for f in files:
        if process(f, dry):
            changed += 1
            print(f"  {'would update' if dry else 'updated'}: {f.name}")
    print(f"\n{len(files)} files scanned. {changed} {'would change' if dry else 'changed'}.")


if __name__ == "__main__":
    main()
