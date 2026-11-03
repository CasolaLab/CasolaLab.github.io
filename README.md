# Casola Lab website

Plain HTML/CSS/JS, no build step. GitHub Pages serves the folder as is.

`index.html` is the scroll-animated front page (`assets/scroll.css`, `assets/scroll.js`). Research, People,
Publications, News and Join are the extended subpages. `classic.html` is the earlier traditional home page, kept
but not linked.

```
index.html (scroll front page)  research.html  people.html  publications.html  join.html
assets/style.css   shared styles (colors in :root, dark mode included)
assets/site.js     nav menu, publication rendering, species italics
data/publications.js   generated, do not edit by hand
scripts_new_lab_website/update_publications.py
```

## Preview locally

```
open index.html
```

## Deploy to GitHub Pages

```
git init && git add . && git commit -m "Initial lab website"
gh repo create casolalab.github.io --public --source . --push
```

Then on GitHub go to Settings → Pages → Source "Deploy from a branch", branch `main`, folder `/`. A repo named
`<account>.github.io` is served at `https://<account>.github.io/`; any other name is served at
`https://<account>.github.io/<repo>/`. For a custom domain, add a `CNAME` file and set the DNS record.

## Updating

- **Publications**: `python3 scripts_new_lab_website/update_publications.py` regenerates `data/publications.js`
  from Europe PMC. Papers the affiliation filter misses go in `EXTRA_IDS` in the script (PMID, or PPR id for a
  preprint). The home page and research page key papers update automatically.
- **News**: add an entry to `data/news.js` (date, title, text). New papers and preprints since 2022 appear on the
  News page automatically from the publication data.
- **Homepage animation**: `assets/img/de_novo_gene_birth.gif` is drawn by
  `scripts_new_lab_website/make_de_novo_gif.py` (run with the `analysis` conda env's python). Edit captions or
  colors there and rerun.
- **Research key papers**: edit the `data-dois` list under each section of `research.html`. A DOI that is not in
  the publication data is skipped and logged in the browser console.
- **Species italics in titles**: add the genus or binomial to `GENERA` / `BINOMIALS` in `assets/site.js`.
- **People**: edit `people.html`. Put photos in `assets/img/` and replace the initials `<div class="avatar">` with
  `<img class="avatar" src="assets/img/name.jpg" alt="Name">`.
- **Navigation/footer** are repeated in each page; change all five files together.
