# Pagesmith

A tiny static site generator with zero dependencies. Write Markdown, get a
fast, good-looking blog with an RSS feed. One file does the building; the
standard library does the serving.

## Quick start

```bash
# scaffold an example site
python cli.py init mysite && cd mysite

# build to ./public
python cli.py build

# serve locally with live reload
python cli.py serve --reload
```

## Features

- Markdown subset: headings, bold/italic, code blocks, lists, links,
  images, blockquotes, tables, horizontal rules
- YAML-ish front matter (`title`, `date`) per post
- Index page, per-post pages, tag pages, and `feed.xml` (RSS)
- Minimal built-in theme; drop in your own `style.css` to restyle
- `serve --reload` injects a meta refresh so edits show up instantly

## Layout

```
mysite/
  content/     # *.md posts with front matter
  style.css    # optional: overrides the built-in theme
  public/      # generated output (git-ignored)
```
