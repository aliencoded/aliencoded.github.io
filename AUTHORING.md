# Editorial notes

Quick reference for adding/editing articles. For architecture and code details see `CLAUDE.md`.

## Article location

Articles live in `_articles/` as Markdown files named `YYYY-MM-DD-slugified-title.md`. After editing the `title:` in front matter, run `python3 _scripts/rename-articles.py` to keep filenames in sync.

## Front-matter checklist

```yaml
---
layout: post-layout
title: "Your headline here"
date: 2026-02-20 12:00:00 -0500
lastUpdated: 2026-02-20 12:00:00 -0500
author: [MetaCurrents Staff]
categories: [articles, <section>, <topic-tag>, ...]
image: https://...
excerpt: "1–2 sentence summary used on cards and OpenGraph."
# featured: true        # uncomment to pin this article as the home-page hero
# is_llm_generated: false  # uncomment to suppress the LLM-generated note at the bottom
---
```

## Promoting an article to the home hero

The home page (`/`) shows one article as a large hero card above the grid. The default pick is the most recent article overall. To override, add `featured: true` to the article's front matter — that article will become the hero regardless of date.

If multiple articles have `featured: true`, the newest of those wins.

## Categories vs. tags

The `categories` list is doing two jobs in this codebase:
- **Section tags** — `global`, `geopolitics`, `business`, `tech`, `us`, `satire`. These match section pages and determine where the article appears in the nav.
- **The `articles` flag** — every article needs `articles` so it shows up on the All Articles page.
- **Topic tags** — `middle-east`, `ai`, `finance`, etc. Currently stored in `categories` but no UI renders them yet.

Keep categories **lowercase** and **hyphenated** (e.g. `middle-east`, not `Middle East` or `middleEast`). Liquid's `contains` filter is case-sensitive, so a mismatched case will silently fail to appear on its section page.
