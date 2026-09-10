# Blockbuster Injury

A duplicate of [accidentreporthelp.com](https://www.accidentreporthelp.com), rebranded to
**Blockbuster Injury**. Same structure, same layout, same copy — new name, new logo, new palette.

Plain static HTML/CSS/JS. No build step, no dependencies.

## Running it

Any static file server works. The pages use directory-index URLs (`/cities/miami/index.html`
served at `/cities/miami`), which Vercel, Netlify, Cloudflare Pages, GitHub Pages and S3 all
handle out of the box.

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

## Layout

```
index.html                  home
cities/                     26 city landing pages
location/                   7 state landing pages
privacy-policy/  terms-and-conditions/  thank-you/  search/
404.html  robots.txt  sitemap.xml
assets/                     all CSS, JS, fonts and images (self-hosted)
tools/build_site.py         the script that generated this from the source site
```

39 pages, 174 assets. Everything is served from this repo — no Webflow CDN, no external
stylesheets, no remote fonts.

## What changed from the source site

**Name.** Every occurrence of "Accident Report Help" / "AccidentReportHelp" is now
"Blockbuster Injury" / "BlockbusterInjury" — page copy, titles, meta descriptions, JSON-LD
and alt text. Links and canonicals point at `blockbusterinjury.com`; the contact address is
now `info@blockbusterinjury.com`.

**Logo.** `assets/logo.svg` is the official badge. Its canvas carried ~35% empty padding,
which left a gap in the navbar, so the root `viewBox` was tightened to the artwork bounds —
framing only, the paths are untouched.

The badge is wide (~2.18:1), so in the header slot it caps at 100px × 46px — the same box the
source site used, which keeps the navbar at its original height. That makes the wordmark read
small. To give it more presence, raise `.brand { max-width }` in `assets/brand.css`; the
navbar grows to match.

`assets/favicon.svg` (and the `favicon.png` / `webclip.png` rendered from it) is a square
"BB" monogram in the same navy and gold — the wide badge doesn't reduce legibly to 32px.
Replace it if you have a square mark.

**Palette.** The source site is mint green (`#52db82`) with red CTAs. This one is navy and
gold, taken from the logo:

| Role | Was | Now |
| --- | --- | --- |
| Primary CTA | `#cc2f31` red | `#f7b91b` gold |
| Accent / glows | `#52db82` mint | `#16264d` navy |
| Dark sections, navbar | `#111827` | `#101a33` / `#1e3260` navy |
| Secondary | `#fdc951` | `#f7b91b` gold |

Colour tokens were substituted in place across the stylesheets, so spacing, type and layout
are untouched. `assets/brand.css` loads last and carries the handful of adjustments the
palette swap needed — mainly navy button text, because white on gold is unreadable.

**Footer watermark removed.** The source site had a large faint wordmark image above the
footer; it is dropped sitewide and its image files are gone.

**Supporting firm.** The Lindner Law Group attribution is now **Blockbuster Injury**, at
30 N Gould St #10835, Sheridan, WY 82801 — in the footer, the contact block, and the terms
page.

**Blog removed.** The blog index, its 33 posts and the `/blog-categories/tips` category page
are gone, along with the "Blogs & Insights" navbar link and the footer "Resources" column that
pointed at them. The 165 images and stylesheets used only by those pages were deleted too, and
the sitemap now lists 39 URLs instead of 74.

**Nothing else.** Copy, section order, images, animations and page structure are unchanged.

## Before going live

- **Lead form** — the request form is still the LeadConnector/GoHighLevel embed from the
  source site (`api.leadconnectorhq.com/widget/form/EqHi8HteSUOiv4xVUs7R`). Submissions land
  in the *original* account until you swap the form ID.
- **Analytics** — Google Tag Manager container `GTM-5KC8L6MN` is likewise the source site's.
  Swap it for the Blockbuster Injury container or traffic mixes into the old property.
- **Phone number** — `+1 (888) 927-2641` was carried over from the source site unchanged.
  Change it if the new brand uses a different number.
- **`/search`** — Webflow's site search was a hosted feature and has no static equivalent.
  The page renders but returns no results; wire it to a search service or drop the page.

## Regenerating

`tools/build_site.py` documents exactly how the mirror was produced: it downloads the source
pages and assets, rewrites every CDN URL to a local path, strips subresource-integrity
hashes, applies the brand and colour substitutions, and writes the tree. It's kept for
provenance and for re-syncing if the source site changes — it expects the scraped `pages/`
and `assets/` directories alongside it.
