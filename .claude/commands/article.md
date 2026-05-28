---
description: One-shot generate 10 Meta Currents articles dated today, distributed across sections
---

Generate **10 new articles** for Meta Currents in one pass, all dated today. Do not ask the user for topics — pick them yourself. Do not stop partway. Do not commit or push.

Optional steering from the user (themes, regions to emphasize, sections to skip): `$ARGUMENTS`

## Distribution across the 10

Hit this section mix unless `$ARGUMENTS` overrides it:

| Section | Count |
|---|---|
| `global` | 2 |
| `us` | 2 |
| `business` | 2 |
| `geopolitics` | 1 |
| `tech` | 2 |
| `satire` | 1 |

Within each section, pick distinct topics — no two articles should cover the same beat (e.g. don't write two AI regulation pieces).

## Per-article output

For each of the 10, write one file:

```
_articles/YYYY-MM-DD-<slugified-title>.md
```

- `YYYY-MM-DD` is today.
- Slug: title lowercased, non-alphanumerics → `-`, collapsed, trimmed.
- Titles must be distinct enough that slugs don't collide. If two slugs would match, rename.

### Front matter (exact shape, in this order)

```yaml
---
layout: post-layout
title: "<Title in Title Case, double-quoted>"
date: YYYY-MM-DD HH:MM:SS -0500
lastUpdated: YYYY-MM-DD HH:MM:SS -0500
author: [MetaCurrents Staff]
categories: [articles, <section>, index, <topic-tag>, <topic-tag>]
image: <Unsplash URL — see below>
excerpt: "<One sentence, ~25 words. Double-quoted.>"
---
```

- `HH:MM:SS`: spread the 10 timestamps across the workday — roughly 07:00 to 18:00 — so they sort naturally on the home page. Do not give all 10 the same time.
- `categories`: always `articles` + `index` + the section. Add 1–3 lowercase-hyphenated topic tags (e.g. `middle-east`, `ai`, `finance`, `trade`, `aviation`, `cybersecurity`, `international-relations`, `energy`, `markets`). Never mixed-case, never spaces. Satire pieces also include `humor`.
- `image`: a real Unsplash URL in the format used across `_articles/`: `https://images.unsplash.com/photo-<id>?q=80&w=<w>&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=<ixid>`. **Do not invent IDs. Do not use IDs from training data.** You cannot tell which Unsplash IDs are live — invented IDs that look syntactically right 404 constantly. Mandatory process:
  1. **Reuse an ID already present in `_articles/`.** Build the pool first: `grep -h "^image:" _articles/*.md | sort -u`. Pick one whose subject roughly matches your article's section/topic.
  2. **Verify every URL after writing files, every time.** Run: `grep -h "^image:" _articles/<your-new-files> | awk '{print $2}' | xargs -I{} curl -o /dev/null -s -w "%{http_code} {}\n" "{}"`. Any non-200 → swap with another ID from the pool and re-verify. Do not report the batch complete until every URL returns 200.

### Body

- News articles: 4–8 paragraphs, ~600–1200 words, neutral wire-service tone.
- Satire piece: 5–10 short paragraphs, ~400–700 words, absurdist deadpan.
- Plain markdown paragraphs, blank lines between them. No `<p>` wrappers.
- No invented quotes attributed to real named people. Use unnamed officials/analysts/spokespeople, or clearly fictional names for satire.
- No body links, no inline images, no closing meta-commentary ("stay tuned", "in conclusion").

## Sourcing rule (important)

You do not have live news access. Do **not** invent specific recent events with named officials, casualty counts, vote totals, ticker prices, named legislation, etc. Write at an **analytical / structural level** — trends, pressures, frameworks, shifts — the way the existing corpus does. Satire is exempt.

If `$ARGUMENTS` includes source material (pasted text, links), use it to ground the relevant pieces.

## Style anchors

Before drafting, read one of each to calibrate voice:
- News: `_articles/2026-02-20-iran-us-israel-trade-words.md`
- Analysis: `_articles/2026-02-20-ai-regulation-frameworks-gain-traction-in-eu-and-united-states.md`
- Satire: `_articles/2026-02-26-syria-solves-everything-announces-strategic-war-on-mascara.md`

## Process

1. Read the three style anchors above.
2. Plan all 10 titles + sections + timestamps upfront so distribution and slugs are unique. Keep this list in a TaskCreate task list.
3. Write all 10 files. Use parallel Write calls where possible.
4. After all 10 are written, output a single summary table to the user:
   - File path · section · title · one-line excerpt
5. Do **not** commit, stage, or push. The user reviews and commits.

Begin.
