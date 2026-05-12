# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Meta Currents** — a Jekyll-based news/content site deployed to `metacurrents.com` (see `CNAME`). Jekyll 4.4.x with **no theme gem** — the original minima theme has been fully forked into local `_sass/meta-currents/` partials. Deployed via GitHub Actions on push to `master`.

## Commands

- `bundle install` — first-time gem install (regenerates `Gemfile.lock`, not committed).
- `bundle exec jekyll serve` — local dev server at http://localhost:4000. Watches for changes (but `_config.yml` changes require a server restart).
- `bundle exec jekyll serve --drafts` — include items in `_drafts/`.
- `bundle exec jekyll build` — build into `_site/` (gitignored).
- `JEKYLL_ENV=production bundle exec jekyll build` — production build (enables Disqus + GA when configured).
- `python3 _scripts/rename-articles.py` — bulk-rename files in `_articles/` and `_videos/` to `YYYY-MM-DD-slugified-title.md` based on their `date` and `title` front matter. Run after adding/editing articles to normalize filenames.

**Ruby version:** `.ruby-version` pins `3.1.6` (matches CI). A newer Ruby (3.3/3.4 via brew) also builds fine, but CI uses 3.1.

## Deployment

`.github/workflows/jekyll.yml` builds on push to **`master`** (not `main`) using Ruby 3.1 + `JEKYLL_ENV=production`, uploads the `_site/` artifact, and deploys to GitHub Pages. The `metacurrents.com` CNAME is committed at the repo root.

## Architecture

### Four content collections (defined in `_config.yml`)

| Collection | Folder | Purpose | Default layout |
|---|---|---|---|
| `articles` | `_articles/` | News articles — the primary content type (~100 files) | `post-layout` |
| `pages` | `_pages/` | Top-level site pages (sections, about, sponsors). Output to `/pages/:title/`. | `page-card-grid-layout` or `page-layout` |
| `people` | `_people/` | Biographical pages rendered as event timelines | `person` |
| `videos` | `_videos/` | YouTube video pages with embed | `video` |

All four have `output: true`. Note `site.posts` is unused — `_posts/` and `_drafts/` contain legacy stubs.

### Routing model

- **Section pages** (`_pages/global.markdown`, `tech.markdown`, `business.markdown`, etc.) use `layout: page-card-grid-layout`, declare a `content-category`, and live at `/pages/<name>/`.
- The **home page** is `/index.markdown` at the repo root, also using `page-card-grid-layout` with `content-category: index`. There is a near-duplicate at `_pages/index.markdown` — this one is effectively dead (it'd resolve to `/pages/meta-currents/`). Treat the root file as the source of truth and leave the duplicate alone unless cleaning up.
- **Nav** is split into two rows in the header by front-matter `navGroup`. Both are in `_includes/header.html`:
  - Row 1 (primary, full size): `navGroup: section` pages — Global, US, Business, Geopolitics, Tech, Satire, People. Right-aligned, alongside the logo on the left.
  - Row 2 (muted, smaller): `navGroup: utility` pages — All Articles, YouTube, Sponsors, About. Right-aligned, separated by a hairline rule above (`$mc-rule`). Renders inside `.site-header__utility`.
  - Both lists filter on `nav: true` and sort by `pageOrder`. The default minima `header_pages` loop is removed — don't re-add it.
  - To add a nav item: set `nav: true`, a `pageOrder` integer, and `navGroup: section` (top row) or `navGroup: utility` (second row).

### How section pages filter content

`page-card-grid-layout.html` does:
```liquid
{% assign posts_filtered = site.articles
   | where_exp:"post","post.categories contains page.content-category"
   | sort: "date" | reverse %}
```
So an article appears on a section page when its `categories:` list contains that section's `content-category` value. Each article should include `articles` (for the All Articles page) plus its section(s).

The **home page** is different — it uses `_layouts/home.html` and shows ALL articles sorted by date desc, regardless of category. The legacy `index` category tag is no longer required (the `_pages/index.markdown` filter page that used it is dead, with `nav: false`).

`people-card-grid-layout.html` is the equivalent for `site.people` (no category filter — shows all people).

### `categories` is overloaded — it's both section-tags AND topic-tags

Articles use `categories` for **two distinct purposes** that aren't currently distinguished:
- **Section assignment** (has a corresponding `_pages/` filter page): `global`, `geopolitics`, `business`, `tech`, `us`, `satire`.
- **Magic flags**: `articles` (show on All Articles), `index` (show on home).
- **Topic-tags** (no filter page, never rendered): `middle-east`, `ai`, `finance`, `asia`, `europe`, `law`, `trade`, `politics`, `economy`, `international-relations`, `aviation`, `cybersecurity`, etc.

There's also inconsistent casing/punctuation in the corpus (`Asia` vs `asia`, `Middle East` vs `middle-east`, `US` vs `us`, `United States` vs `us`). When editing or adding articles, prefer the lowercase-hyphenated form. A future cleanup is to move topic-tags into Jekyll's built-in `tags:` and reserve `categories` for sections.

### Layouts cheat sheet

| Layout | Used by | What it does |
|---|---|---|
| `default` | wraps everything | Header (two-row: logo + section nav, then utility row with clock + utility nav), footer; loads `assets/js/clock.js` and `assets/js/load-more.js` |
| `home` | root `index.markdown` | Hero card on top (featured or newest article) + paged grid of the rest |
| `page-card-grid-layout` | section pages | Card grid filtered by `content-category`, wrapped in load-more |
| `people-card-grid-layout` | people page | Card grid over `site.people`, sorted by date desc |
| `page-layout` | about, sponsors | Plain content page |
| `post-layout` | individual articles | Title, date + time-ago, author, category badges, hero image with watermark, content, optional LLM-generated note (suppress with `is_llm_generated: false` in front matter) |
| `person` | individual people | Renders `events:` array from front matter as a vertical timeline |
| `video-list` | `_pages/youtube.md` | Grid of all videos with YouTube thumbnails |
| `video` | individual videos | YouTube embed + description + tags |
| `home-layout` | nothing | Old minima-style home — dead, do not use |

### Hero card

`_includes/hero-card.html` renders a featured article in a two-column layout (image left, content right; stacked on mobile). The `home` layout picks the hero with this precedence:
1. First article that has `featured: true` in front matter (sorted by date desc among featured).
2. Otherwise, the most recent article overall.

To promote an article to the hero slot, add `featured: true` to its front matter. The hero is excluded from the "Latest" grid below it so it doesn't appear twice.

### Load-more pattern

Card grids on `home` and `page-card-grid-layout` are wrapped in `.cards-with-loadmore`, which contains a `.cards-container[data-page-size="N"]` plus a `.load-more-btn`. `assets/js/load-more.js` (loaded by `default.html` with `defer`) hides cards past the page size with a `.card--hidden` class, and reveals the next batch on button click. No plugin required — pure client-side, all cards still in the rendered HTML so SEO/links are preserved. Default page size is 10 (9 on home, since the hero counts as one).

### Reading progress bar

`post-layout.html` renders a `<div class="reading-progress">` at the top of the page; `assets/js/reading-progress.js` updates its width on scroll proportional to how far into `.post-content` the reader has scrolled. Only present on article pages (the div isn't in other layouts).

### Tags & section pills

Articles' `categories` field is rendered as colored pills below the title (via `_includes/post-tags.html`). Each pill is clickable:
- **Section pill** (filled navy): the category slug matches a `_pages/` page with `navGroup: section`. Links to `/pages/<slug>/`.
- **Topic pill** (outlined slate): everything else. Links to `/tags/<slug>/`.
- **Filtered out**: the generic `articles` and `index` flags don't render.

The `/tags/<slug>/` pages are auto-generated at build time by `_plugins/tag_pages.rb`. The plugin enumerates unique non-section, non-generic categories across all articles and emits one page per unique slug, rendered through `_layouts/tag.html`. Adding a new tag = just put it in an article's `categories`; next build creates the page.

**Heads-up on data quality:** the corpus has case/format inconsistencies (e.g. `"middle-east"` AND `"Middle East"`, `"asia"` AND `"Asia"`). Each variant gets its own tag page because Liquid's `contains` and the plugin's matching are case-sensitive. A future normalization pass on `_articles/*.md` `categories:` fields (lowercase + hyphenate) would collapse those duplicates.

**Requires GitHub Actions deployment** — the plugin won't run on the legacy "Pages auto-build" path. The repo already uses Actions, so this is fine.

### Search

Adaptive client-side search.
- `/search.json` is generated at build time from `search.json` (Liquid template at repo root). Each entry has `title`, `url`, `date`, `excerpt`, `categories`.
- `_includes/search-modal.html` provides the overlay/dialog markup; pulled into `default.html` once.
- The trigger button (`.search-trigger`) sits in the header utility row next to the clock; clicking it opens the modal. `Cmd/Ctrl + K` also opens it. `Esc` or click-outside closes.
- `assets/js/search.js` fetches `/search.json` lazily on first open, seeds the modal with the 5 most recent articles, and filters live (title + excerpt + categories, case-insensitive substring) as the user types. Max 20 results displayed.
- Styling lives in `_sass/meta-currents/_search.scss`.

### SEO & feeds

- `jekyll-feed` → `/feed.xml`
- `jekyll-sitemap` → `/sitemap.xml` (automatic)
- `jekyll-seo-tag` → canonical, OpenGraph, Twitter card meta in `<head>`
- `url: https://metacurrents.com` is set in `_config.yml` for canonical URL generation.

### Sass

`assets/main.scss` imports `_sass/meta-currents.scss`, which imports the partials under `_sass/meta-currents/`:
- `_variables.scss` — brand palette (`$brand-color: #0b2c4e` navy), typography, spacing.
- `_base.scss` / `_layout.scss` / `_syntax-highlighting.scss` — inherited from minima, renamed namespace.
- Custom additions: `_cards-custom.scss`, `_search.scss`, `_site-logo.scss`, `_sponsors.scss`, `_people-timeline.scss`, `_youtube.scss`.

`$content-width: 800px` constrains `.wrapper`, which wraps both the article reading column and the home/section grids — so the home grid is also capped at 800px. Decoupling the grid wrapper from the article wrapper is a known improvement.

### Logo & branding

The brand mark is the JPEG at `assets/images/meta-currents-icon-{small,medium,large}.jpeg` — a wave/curve graphic stacked above a two-tone "metacurrents" wordmark ("meta" deep navy, "currents" slate). `_includes/logo.html` uses the medium JPEG in the top-left masthead as a single inline image (icon + wordmark together — no separate CSS wordmark). The About page uses the large JPEG. `favicon.ico` at the repo root is the favicon. The `apple-touch-icon` link uses the small JPEG.

An attempt to trace the icon into inline SVG was abandoned — the wave geometry didn't match cleanly enough. If you ever want a crisp scalable masthead, the right next step is exporting a clean SVG from the original design source (Illustrator/Figma/etc.), not having Claude trace it from the raster.

### Embeds & third-party

- `_includes/youtube.html` — privacy-flag YouTube iframe (used by `video` layout and reusable in articles).
- `_includes/stock-ticker.html`, `stock-widget.html` — TradingView mini-widgets (QQQ, SPY, BTC).
- `assets/js/clock.js` — live NY-time clock in the header.
- `_includes/google-analytics.html`, `disqus_comments.html` — only fire when `JEKYLL_ENV=production` AND the corresponding key is set in `_config.yml` (neither is configured yet).

## Things to know before editing

- **`future: true`** in `_config.yml` — articles with future dates are published immediately, not held back. (Most articles in the repo are dated 2026.)
- **Editing an article's title:** rerun `_scripts/rename-articles.py` so the filename slug stays in sync with the title.
- **Adding a new section:** create `_pages/<name>.markdown` with `layout: page-card-grid-layout`, `permalink: /pages/<name>/`, `nav: true`, `navGroup: section`, `pageOrder: <n>`, `content-category: <name>`. Then add `<name>` to the `categories` of every article that belongs there.
- **`_pages/index.markdown` is a dead duplicate** of root `index.markdown` — kept on disk with `nav: false` so it doesn't appear in the nav. Safe to delete entirely.
- **Categories are case-sensitive** in Liquid's `contains` filter. Mixed-case categories like `Asia` won't match a section filter looking for `asia`.
