# Backfill Brief — Meta Currents Article Backfill (2026-03-30 → 2026-05-12)

You are one of many parallel agents writing news articles for the Meta Currents site at `/Users/ali/alidev/aliencoded.github.io`. Each agent writes ONE article and saves it to `_articles/`.

Your specific assignment is in the prompt that called you. This document holds everything shared across all backfill agents.

---

## STYLE

- AP-style news prose, third person, mostly past tense for completed events, present perfect / continuous for ongoing.
- Attribute facts and quotes to **specific (fictional but plausible) named people, spokespeople, officials, analysts**. Use formal titles ("President Donald Trump", "Foreign Minister Abbas Araghchi", "Energy Secretary"). For made-up sources, use realistic titles ("a senior State Department official, speaking on condition of anonymity", "John Reilly, an analyst at Citi", "Layla Hassan, a Beirut-based regional analyst").
- Length target: ~750–1000 words of body. Slightly over or under is fine.
- Do NOT break character. No meta-commentary. No "this article is AI-generated." Write as if it's a real news piece for a real publication.
- Lead with the most newsworthy fact in the first paragraph. Inverted-pyramid structure.
- Mid-article quote(s) attributed to fictional but plausibly-named people.
- Don't invent verifiable real-world facts (e.g., don't claim a real US Senator voted for a specific bill on a specific date). Stick to fictional officials' actions, or describe broad political alignments without exact attributions for real people.

---

## NARRATIVE ARC (canonical timeline — agents must respect this)

The pre-existing corpus (Feb 20 – Mar 28, 2026) established these threads. Backfill agents must continue them coherently.

### Iran war (~Mar 1 onset; ceasefire mid-April)

- **Mar 29 – Apr 6:** Continued strikes both directions. Houthi escalation. U.S. casualties accumulate (~350 total by Apr 6). Saudi/UAE intercepts ongoing. Israeli strikes on Iranian nuclear/industrial sites continue.
- **Apr 1:** OPEC+ holds emergency Vienna session — announces ~1.5M bpd production hike. Brent eases from $125 peak back toward $108.
- **Apr 4–6:** NCAA Final Four (San Antonio). Apr 6 championship: **UConn defeats Michigan** (close game, late-second-half run by UConn).
- **Apr 7–11:** Islamabad talks gain momentum. Pakistan, Saudi, Egypt mediators present "framework principles." Iranian FM signals willingness to discuss conditional halt. U.S. cautious. Multiple back-channel meetings.
- **Apr 12:** **Ceasefire announced** by joint statement from Islamabad talks. Takes effect Apr 15 at 00:00 GMT.
- **Apr 13–14:** Last-minute strikes; Iran fires a final volley, intercepted; Israel hits one final nuclear site. Public anxiety.
- **Apr 15:** **Ceasefire takes effect.** Initial holding. UN observers deployed to Strait of Hormuz.
- **Apr 16–17:** Some sporadic violations (one Houthi launch, one rocket from Iraq), all condemned. Holding overall.
- **Apr 18:** **Prisoner exchange** in Doha — Iran releases ~40 detained foreigners + remains of U.S. service members; U.S./Israel release Iranian and Hezbollah-affiliated detainees. No tribunal.
- **Apr 19 – May 12:** Post-war phase. Reconstruction in Iraq/Yemen/Iran. Refugee returns. Markets stabilize. Oil settles ~$95 Brent. Political fallout in U.S. and Israel. War-cost reports. Iran's economy strain.

### AI moratorium (Sanders + AOC bill)

- **Mar 26:** Bill introduced.
- **Apr 1–6:** Hearings, lobbying. Big Tech opposes loudly. Some moderate Dems waver.
- **Apr 7:** **Senate passes** narrowly (52-48, with 3 Republicans and 2 Independents joining most Dems; 5 Dems voted no).
- **Apr 8–21:** House Ways and Means deliberation. Heavy lobbying. AOC and Sanders push, hyperscaler CEOs in DC meetings.
- **Apr 22:** **Bill dies** in House Ways and Means by 24-21 vote. Reform-side critics call for compromise alternative.
- **Apr 23 – May 12:** Aftermath — compromise efforts, state-level moratorium bills in NY/CA, AI industry victory laps tempered by acknowledging energy concerns.

### Markets / oil

- Late March: Brent at $119–125. S&P down 4.3%.
- **Apr 1:** OPEC+ production hike → Brent → $108 over week.
- **Apr 6 – Apr 15:** Choppy, volatility tied to ceasefire prospects.
- **Apr 15+:** Ceasefire holds → Brent settles to $98 by Apr 25, $92 by May 5.
- **May:** Earnings season begins; markets recover. S&P recovers most of war losses.

### NCAA

- **Apr 4 (Sat):** Semis — UConn beats Tennessee, Michigan beats Duke (Duke upset).
- **Apr 6 (Mon):** Championship — UConn defeats Michigan.

### Burkina Faso / Africa

- Continued junta consolidation. ECOWAS pressure. France-Africa tensions ongoing.

### Trump administration (US politics)

- War handling, midterm dynamics, immigration policy, AI moratorium reactions. Continued political fights but no major new scandals — keep it newsy not gossipy.

### Other ongoing threads

- Climate / spring weather events (tornadoes, flooding).
- Tech earnings (Apple, Microsoft, NVIDIA in April reports).
- Sports beyond NCAA: MLB regular season starts Apr 2, NBA playoffs starting late April.

---

## SLOT DEFINITIONS

Each day's 8–10 articles are assigned slot numbers. Your slot determines what your article covers and what time it publishes. Slots are stable across the 44 days so the site has predictable rhythm.

| Slot | Time slot | Primary beat |
|---|---|---|
| 1 | 09:00–09:30 | Markets / oil / global business roundup |
| 2 | 10:00–10:30 | **FEATURED** lead news of the day (during war: Iran/Israel beat; post-ceasefire: reconstruction or top political story) |
| 3 | 11:00–11:30 | Diplomacy / international relations |
| 4 | 12:00–12:30 | US politics / Congress / White House |
| 5 | 13:00–13:30 | Humanitarian / refugees / civilian impact (during war) OR climate/weather/health (post-war) |
| 6 | 14:00–14:30 | Sports (NCAA → MLB → NBA) |
| 7 | 15:00–15:30 | Tech / AI / business sector |
| 8 | 16:00–16:30 | Africa / Europe / Asia / non-MidEast global |
| 9 | 17:00 | Satire piece (Sundays + some weekdays; ~2/week) |

If your prompt says "slot N, date YYYY-MM-DD", combine that with the narrative arc for that date to find a fitting topic. If your date doesn't need slot 9, your prompt won't request slot 9.

---

## FRONT MATTER TEMPLATE

```yaml
---
layout: post-layout
title: "<your headline>"
date: YYYY-MM-DD HH:MM:00 -0500
lastUpdated: YYYY-MM-DD HH:MM:00 -0500
author: [MetaCurrents Staff]
categories: [articles, <section>, <topic-tag-1>, <topic-tag-2>, ..., index]
image: <url from _data/image_bank.yml>
excerpt: "<1-2 sentences, 180-260 chars>"
---
```

**For the FEATURED slot (slot 2) only**, also add: `featured: true` on a new line before `---`.

**Sections** (one of): `geopolitics`, `us`, `business`, `tech`, `satire`, `global`, `people`. Match to slot:
- Slot 1 → `business`
- Slot 2 → `geopolitics` during war; `geopolitics` or `us` post-war
- Slot 3 → `geopolitics`
- Slot 4 → `us`
- Slot 5 → `global`
- Slot 6 → `us`
- Slot 7 → `tech` or `business`
- Slot 8 → `global`
- Slot 9 → `satire`

**Topic tags** should be lowercase + hyphenated (e.g., `middle-east`, `markets`, `ncaa`, `ai`). Include 3–5 tags. Always include `articles` (first) and `index` (last) per existing convention.

**Categories** must be lowercase. Never use spaces. "Middle East" → `middle-east`. "United States" → `us`. (The site has section pages for global/us/business/geopolitics/tech/satire/people; everything else becomes a topic tag.)

---

## IMAGE — CRITICAL RULES

Read `_data/image_bank.yml`. It's a YAML file with clusters, each cluster contains a list of verified Unsplash URLs.

**Rule 1:** Use ONLY URLs from `_data/image_bank.yml`. Do not invent, modify, or generate a new URL.

**Rule 2:** Pick the cluster that best matches your article's primary topic:
- Iran war military → `middle_east_war`
- Diplomacy / peace talks → `diplomacy`
- Oil / OPEC / energy → `oil_energy`
- Markets / stocks / finance → `markets_finance`
- Shipping / supply chain / ports → `shipping_supply`
- NCAA / basketball → `basketball_sports`
- AI / data centers / tech → `ai_tech`
- Refugees / displacement / humanitarian → `refugees_humanitarian`
- Africa news → `africa`
- Aviation / airports → `aviation`
- US politics / Congress → `us_politics`
- Climate / weather / storms → `climate_weather`
- Asia non-MidEast → `asia`
- Satire / military / pentagon → `satire_military`

**Rule 3:** Within your chosen cluster, pick any URL — variety across articles is fine. **Copy the URL exactly as it appears, including the `?q=80&w=1600&auto=format&fit=crop` query string.**

If your article topic doesn't fit any cluster well, default to `middle_east_war` during the war window, `us_politics` post-war.

---

## FILENAME

Slugify your title: lowercase, replace non-alphanumeric with hyphens, collapse runs.

Save to `_articles/YYYY-MM-DD-<slug>.md`.

Use the date from your prompt assignment, not the time slot — all of a day's articles share the same date prefix.

---

## REPORT BACK (under 80 words)

- Filename created
- Body word count (use the Bash tool: `awk '/^---$/{n++; next} n>=2 {print}' "FILE" | wc -w`)
- Image URL used + cluster name it came from
- 1 sentence on what the article covers

---

## WHAT NOT TO DO

- Don't fetch images (you can't reach Unsplash anyway; use the bank).
- Don't invent new URLs.
- Don't add disclaimers, "this article" meta-text, or LLM disclosures.
- Don't reference real-world events past your article's date (no foreshadowing real news).
- Don't write the same opening sentence pattern as a typical existing article — vary the lede.
- Don't include the words "in conclusion", "in summary", or similar essay-style closers. End with a news-style forward-looking line ("Officials said additional steps would be announced...").
