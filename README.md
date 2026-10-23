# dmphotos.ca

Dhruvil Mehta's photo portfolio, moved off Format (dhruvil.format.com) to free GitHub Pages hosting.

The page uses Format's own "Clarity" theme CSS and gallery JavaScript (masonry layout, lazy-loading, lightbox with captions, keyboard arrows and swipe), so it looks and behaves the same as the Format site. Format's analytics, tracking and "Using Format" badge were removed.

- `index.html`: the gallery (also served at `/portfolio/`, like on Format)
- `images/NN/`: each photo at several widths, plus `lightbox.jpg`
- `assets/`: theme CSS, JS, icons and the DM Sans font (free, replaces Format's Proxima Nova)
- `tools/`: scripts that rebuilt this site from the scrape on the `scrape` branch

## Adding or changing photos

The quickest way is to ask Claude. To do it by hand, add the new image to `_scrape/images/` and `_scrape/images.json` on the `scrape` branch, then rerun:

    python3 tools/images.py _scrape site/images
    python3 tools/build.py _scrape site dmphotos.ca path/to/@fontsource/dm-sans
