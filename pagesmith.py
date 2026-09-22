"""Pagesmith core: markdown subset -> HTML, site builder, RSS. Stdlib only."""
from __future__ import annotations
import html
import os
import re
from datetime import datetime

# ---------------------------------------------------------------- markdown

def _inline(text: str) -> str:
    text = html.escape(text)
    # images, then links
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def markdown_to_html(md: str) -> str:
    out: list[str] = []
    in_code = False
    in_list: str | None = None  # "ul" | "ol"
    para: list[str] = []

    def flush_para():
        if para:
            out.append("<p>" + " ".join(_inline(" ".join(para))) + "</p>")
            para.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            flush_para(); close_list()
            out.append("<pre><code>" if not in_code else "</code></pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(raw))
            continue
        if not line.strip():
            flush_para(); close_list()
            continue
        if line.startswith("### "):
            flush_para(); close_list()
            out.append(f"<h3>{_inline(line[4:])}</h3>"); continue
        if line.startswith("## "):
            flush_para(); close_list()
            out.append(f"<h2>{_inline(line[3:])}</h2>"); continue
        if line.startswith("# "):
            flush_para(); close_list()
            out.append(f"<h1>{_inline(line[2:])}</h1>"); continue
        if line.startswith("> "):
            flush_para(); close_list()
            out.append(f"<blockquote>{_inline(line[2:])}</blockquote>"); continue
        if re.match(r"^(\*\*\*|---|___)$", line.strip()):
            flush_para(); close_list()
            out.append("<hr>"); continue
        m = re.match(r"^(\d+)\.\s+(.*)", line)
        if m:
            flush_para()
            if in_list != "ol":
                close_list(); out.append("<ol>"); in_list = "ol"
            out.append(f"<li>{_inline(m.group(2))}</li>"); continue
        if re.match(r"^[-*]\s+", line):
            flush_para()
            if in_list != "ul":
                close_list(); out.append("<ul>"); in_list = "ul"
            out.append(f"<li>{_inline(line[2:])}</li>"); continue
        if "|" in line and re.match(r"^\|?[\s:\-|]+\|?$", line):
            # table separator row — skip (header already emitted as para)
            continue
        para.append(line.strip())
    flush_para(); close_list()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


# ---------------------------------------------------------------- posts

def parse_post(path: str) -> dict:
    with open(path) as f:
        text = f.read()
    meta: dict = {}
    body = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip().strip('"')
            body = text[end + 3:].strip()
    slug = os.path.splitext(os.path.basename(path))[0]
    meta.setdefault("title", slug.replace("-", " ").title())
    meta.setdefault("date", "")
    meta["slug"] = slug
    meta["html"] = markdown_to_html(body)
    meta["excerpt"] = re.sub(r"<[^>]+>", "", meta["html"])[:160]
    return meta


THEME_CSS = """
body{font-family:system-ui,-apple-system,sans-serif;max-width:680px;margin:0 auto;
padding:2rem 1.25rem;line-height:1.7;color:#1a1a1a;background:#fff}
a{color:#0b5fff}pre{background:#f4f4f5;padding:1rem;border-radius:8px;overflow:auto}
code{font-family:ui-monospace,monospace;font-size:.9em}
blockquote{border-left:3px solid #ddd;margin:1em 0;padding:.2em 1em;color:#555}
.post-meta{color:#888;font-size:.9em}hr{border:none;border-top:1px solid #eee}
""".strip()


def _page(title: str, body: str, css: str, reload: bool = False) -> str:
    refresh = '<meta http-equiv="refresh" content="2">' if reload else ""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>{refresh}<style>{css}</style>
</head><body>{body}</body></html>"""


def build(content_dir: str, out_dir: str, site_title: str = "My Blog",
          custom_css: str | None = None) -> list[dict]:
    css = custom_css or THEME_CSS
    os.makedirs(out_dir, exist_ok=True)
    posts = []
    for name in sorted(os.listdir(content_dir)):
        if name.endswith(".md"):
            post = parse_post(os.path.join(content_dir, name))
            posts.append(post)
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)

    for post in posts:
        body = (f'<p><a href="index.html">&larr; home</a></p>'
                f"<h1>{html.escape(post['title'])}</h1>"
                f"<p class='post-meta'>{html.escape(post['date'])}</p>"
                f"{post['html']}")
        with open(os.path.join(out_dir, post["slug"] + ".html"), "w") as f:
            f.write(_page(post["title"], body, css))

    items = "\n".join(
        f"<li><a href='{p['slug']}.html'>{html.escape(p['title'])}</a> "
        f"<span class='post-meta'>{html.escape(p['date'])}</span><br>"
        f"<span class='post-meta'>{html.escape(p['excerpt'])}…</span></li>"
        for p in posts)
    index_body = f"<h1>{html.escape(site_title)}</h1><ul>{items}</ul>"
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(_page(site_title, index_body, css))

    rss_items = "\n".join(
        f"<item><title>{html.escape(p['title'])}</title>"
        f"<link>{p['slug']}.html</link>"
        f"<description>{html.escape(p['excerpt'])}</description></item>"
        for p in posts)
    rss = (f'<?xml version="1.0"?><rss version="2.0"><channel>'
           f"<title>{html.escape(site_title)}</title>{rss_items}"
           f"</channel></rss>")
    with open(os.path.join(out_dir, "feed.xml"), "w") as f:
        f.write(rss)
    return posts
