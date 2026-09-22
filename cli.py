#!/usr/bin/env python3
"""CLI for Pagesmith."""
import argparse
import functools
import http.server
import os
import sys

from pagesmith import build, _page, THEME_CSS


def cmd_init(args):
    os.makedirs(os.path.join(args.name, "content"), exist_ok=True)
    sample = os.path.join(args.name, "content", "hello-world.md")
    if not os.path.exists(sample):
        with open(sample, "w") as f:
            f.write('---\ntitle: "Hello, World"\ndate: "2026-09-22"\n---\n\n'
                    '# Hello, World\n\nThis is my first Pagesmith post. '
                    'Edit me in `content/` and run `python cli.py build`.\n')
    print(f"created {args.name}/ with an example post")


def cmd_build(args):
    css = None
    if os.path.exists("style.css"):
        with open("style.css") as f:
            css = f.read()
    posts = build(args.content, args.out, site_title=args.title, custom_css=css)
    print(f"built {len(posts)} posts -> {args.out}/")


def cmd_serve(args):
    if args.reload:
        # rebuild on every request via a rebuilding handler
        import pagesmith as ps

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                css = None
                if os.path.exists("style.css"):
                    with open("style.css") as f:
                        css = f.read()
                # rebuild quietly, then patch pages with refresh tag
                for name in os.listdir(args.out):
                    path = os.path.join(args.out, name)
                    if name.endswith(".html") and os.path.isfile(path):
                        with open(path) as f:
                            html = f.read()
                        if 'http-equiv="refresh"' not in html:
                            html = html.replace(
                                "</title>",
                                '</title><meta http-equiv="refresh" content="2">', 1)
                            with open(path, "w") as f:
                                f.write(html)
                return super().do_GET()

        ps.build(args.content, args.out, site_title=args.title,
                 custom_css=open("style.css").read() if os.path.exists("style.css") else None)
        handler = functools.partial(Handler, directory=args.out)
    else:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                    directory=args.out)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"serving {args.out}/ at http://127.0.0.1:{args.port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


def main():
    p = argparse.ArgumentParser(prog="pagesmith")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="scaffold a new site")
    i.add_argument("name")
    i.set_defaults(fn=cmd_init)

    b = sub.add_parser("build", help="build the site")
    b.add_argument("--content", default="content")
    b.add_argument("--out", default="public")
    b.add_argument("--title", default="My Blog")
    b.set_defaults(fn=cmd_build)

    s = sub.add_parser("serve", help="serve locally")
    s.add_argument("--content", default="content")
    s.add_argument("--out", default="public")
    s.add_argument("--title", default="My Blog")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--reload", action="store_true")
    s.set_defaults(fn=cmd_serve)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
