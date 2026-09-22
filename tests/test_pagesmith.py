from pagesmith import markdown_to_html, parse_post, build
import os
import tempfile


def test_headings_and_inline():
    out = markdown_to_html("# Title\n\nHello **bold** and *italic* with `code`.")
    assert "<h1>Title</h1>" in out
    assert "<strong>bold</strong>" in out
    assert "<em>italic</em>" in out
    assert "<code>code</code>" in out


def test_lists_and_code_blocks():
    out = markdown_to_html("- a\n- b\n\n```\nx = 1\n```")
    assert "<ul>" in out and "<li>a</li>" in out
    assert "<pre><code>" in out


def test_links_and_images():
    out = markdown_to_html("[hi](https://x.com) ![alt](pic.png)")
    assert '<a href="https://x.com">hi</a>' in out
    assert '<img alt="alt" src="pic.png">' in out


def test_build_generates_pages_and_feed(tmp_path=None):
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        cdir = os.path.join(tmp, "content")
        os.makedirs(cdir)
        with open(os.path.join(cdir, "post-one.md"), "w") as f:
            f.write('---\ntitle: "Post One"\ndate: "2026-09-22"\n---\n\nHello.')
        out = os.path.join(tmp, "public")
        posts = build(cdir, out, site_title="Test")
        assert len(posts) == 1
        assert os.path.exists(os.path.join(out, "post-one.html"))
        assert os.path.exists(os.path.join(out, "index.html"))
        assert os.path.exists(os.path.join(out, "feed.xml"))
