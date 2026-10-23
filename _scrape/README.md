# dhruvil.format.com offline mirror (scraped 2026-10-23)

Theme: Format "Clarity" (theme_version 77), gallery layout "vertical", single page.

- `pages/index/` — home page (`/`). `raw.html` (server HTML), `rendered.html` (DOM after lazy-load at 1440px),
  `rendered-390.html` (mobile DOM), `screenshot-{1440,390}-{full,viewport}.png`, `lightbox-{1440,390}.png`,
  `lightbox-rendered.html` (DOM with the lightbox open on the first image).
- `pages/portfolio/` — `/portfolio`, the same gallery under its own URL (the site has only one page; sitemap lists only `/`).
- `assets/<host>/<path>` — every CSS/JS/icon referenced, plus every font file referenced from CSS (`hosted_fonts.css`
  pulls in Format's whole font catalog; the theme actually uses **Proxima Nova Regular/Bold** and **Input Mono Narrow Regular**).
- `images/` — 41 gallery images at the largest size Format serves (X3XL originals, ~2974px long edge) plus the cover image.
  `images.json` has order, caption, alt text, dominant colour, crop region, pixel size and source URL.
- `site-data.json` — `_4ORMAT_DATA` (page/theme/site config incl. typography and colours) and every inline script verbatim.
- `urls.txt` — original URL -> local path. `fonts-used.json` — every font-family string seen in CSS.
- `sitemap.xml`, `robots.txt` — as served.
