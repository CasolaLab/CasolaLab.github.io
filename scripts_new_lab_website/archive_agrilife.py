"""One-shot archive of agrilife.org/casolalab into old_agrilife_site/.

Reads the WordPress API JSON already saved there (pages.json, posts.json,
media.json), writes each page/post as HTML and plain text, downloads every
media file with curl, verifies size against Content-Length, and writes
index.md plus manifest.tsv (url, local path, bytes, sha256).

Usage: python3 archive_agrilife.py <archive_dir>
"""

import hashlib
import html
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser


class Text(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr", "ul", "ol", "table", "blockquote"}

    def __init__(self):
        super().__init__()
        self.out = []
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag == "li":
            self.out.append("- ")
        if tag == "a":
            self.href = dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag == "a" and self.href:
            self.out.append(f" <{self.href}>")
            self.href = None
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        self.out.append(d)


def to_text(h):
    p = Text()
    p.feed(h)
    t = re.sub(r"[ \t]+", " ", "".join(p.out))
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip() + "\n"


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70] or "untitled"


def head_size(url):
    r = subprocess.run(["curl", "-sIL", url], capture_output=True, text=True, check=True)
    sizes = re.findall(r"(?im)^content-length:\s*(\d+)", r.stdout)
    return int(sizes[-1]) if sizes else None


def main():
    d = sys.argv[1]
    for f in ("pages.json", "posts.json", "media.json"):
        if not os.path.exists(os.path.join(d, f)):
            sys.exit(f"error: {f} missing in {d}")
    pages = json.load(open(os.path.join(d, "pages.json")))
    posts = json.load(open(os.path.join(d, "posts.json")))
    media = json.load(open(os.path.join(d, "media.json")))
    idx = ["# Archive of agrilife.org/casolalab", "",
           f"{len(pages)} pages, {len(posts)} posts, {len(media)} files.", ""]

    for kind, items in (("pages", pages), ("posts", posts)):
        os.makedirs(os.path.join(d, kind), exist_ok=True)
        idx += [f"## {kind.capitalize()}", ""]
        for it in sorted(items, key=lambda x: x["date"], reverse=(kind == "posts")):
            title = html.unescape(it["title"]["rendered"])
            base = f"{it['date'][:10]}_{slugify(it['slug'] or title)}" if kind == "posts" else slugify(it["slug"] or title)
            body = it["content"]["rendered"]
            with open(os.path.join(d, kind, base + ".html"), "w") as f:
                f.write(f"<!doctype html><meta charset='utf-8'><title>{html.escape(title)}</title>\n"
                        f"<p>Original: <a href='{it['link']}'>{it['link']}</a> · {it['date'][:10]}</p>\n"
                        f"<h1>{html.escape(title)}</h1>\n{body}\n")
            with open(os.path.join(d, kind, base + ".txt"), "w") as f:
                f.write(f"{title}\n{it['date'][:10]}\n{it['link']}\n\n{to_text(body)}")
            idx.append(f"- {it['date'][:10]} [{title}]({kind}/{base}.txt) ({it['link']})")
        idx.append("")

    rows, problems = [], []
    idx += ["## Files", ""]
    for m in media:
        url = m["source_url"]
        rel = url.split("/casolalab/files/", 1)[-1] if "/casolalab/files/" in url else os.path.basename(url)
        local = os.path.join(d, "files", rel)
        os.makedirs(os.path.dirname(local), exist_ok=True)
        # Cloudflare serves a recompressed copy from cache; a unique query
        # string bypasses it and returns the file as originally uploaded.
        orig = url + "?archive=orig"
        expected = head_size(orig)
        subprocess.run(["curl", "-sL", "--fail", "-o", local, orig], check=True)
        got = os.path.getsize(local)
        if expected is not None and got != expected:
            problems.append(f"{url}: expected {expected} bytes, got {got}")
        api = (m.get("media_details") or {}).get("filesize")
        if api and got != api:
            problems.append(f"{url}: WordPress records {api} bytes, got {got}")
        sha = hashlib.sha256(open(local, "rb").read()).hexdigest()
        rows.append((url, os.path.join("files", rel), got, sha))
        idx.append(f"- [{rel}](files/{rel}) ({got / 1e6:.2f} MB) {html.unescape(m['title']['rendered'])}")
        print(f"{got:>10} {rel}", file=sys.stderr)

    with open(os.path.join(d, "manifest.tsv"), "w") as f:
        f.write("url\tlocal_path\tbytes\tsha256\n")
        f.writelines("\t".join(map(str, r)) + "\n" for r in rows)
    open(os.path.join(d, "index.md"), "w").write("\n".join(idx) + "\n")
    print(f"files downloaded: {len(rows)} of {len(media)}; total {sum(r[2] for r in rows) / 1e6:.1f} MB")
    print("size mismatches:", problems or "none")


if __name__ == "__main__":
    main()
