# Turkish / English page split

The site used to serve both languages on the same URL and hide one with
JavaScript (`tr-only` / `en-only` classes). These scripts split every page
into a single-language page:

- Turkish pages keep their URLs (`/blog/<slug>/`, `/hakkimda/`, `/tr/`, …).
- English pages live under `/en/` with English slugs (`/en/blog/<slug>/`, `/en/about/`, …).
- Each pair links to the other with `hreflang`; the TR/EN buttons go to the paired page.
- Posts without a real English translation stay Turkish-only (no `/en/` page).

`pages.py` is the map: Turkish path → English path, title and description.

## The migration was a one-off

`build.py` reads the old bilingual pages, so it was run once:

```sh
python3 tools/i18n/build.py      # split pages, write /en/
python3 tools/i18n/sitemap.py    # sitemap.xml + llms.txt
```

Don't re-run it on the already-split pages.

## Adding pages from now on

- Write the Turkish and English versions as two separate files, with no `tr-only` / `en-only` markup.
- In each page's `<head>`: a `canonical` pointing to itself, plus `hreflang="tr"`, `hreflang="en"` and
  `hreflang="x-default"` (pointing to the Turkish page) links to the pair.
- Add the pair to `sitemap.xml` (both URLs, each with the same three `xhtml:link` alternates).
- Turkish-only page: link `hreflang="tr"` and `x-default` to itself and leave out `hreflang="en"`.
