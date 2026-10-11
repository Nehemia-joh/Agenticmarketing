#!/usr/bin/env python3
"""Render a strategy Markdown document into one self-contained HTML review page, with Mermaid diagrams.

Standard library only; no network at build time. It supports the Markdown the strategy documents use:
- headings, paragraphs, bold, italic, inline code and links;
- pipe tables, nested lists (indented by two or more spaces), horizontal rules, block quotes and fenced code;
- ```mermaid fences, which become diagrams that Mermaid (pinned CDN build) draws when the page is opened.

Two HTML comments steer the layout and are invisible when the Markdown is read on its own:
- `<!-- contents -->` is replaced by a contents list built from the level-2 and level-3 headings;
- `<!-- pair -->` lays the next diagram and the next table side by side (the table stacks below on narrow screens).

Relative links are rewritten so they still resolve from the output folder. Heading anchors follow GitHub's rule, so
in-document links work in both the Markdown and the page. The page has a print style. Without an internet connection the
diagrams show their source text instead.

    python scripts/strategy/render_markdown_page.py docs/strategy/partnership-pipelines-draft.md "outputs/strategy/Silverleaf Partnership Pipelines - Draft.html"
"""
from __future__ import annotations

import argparse
import html
import os
import re
import urllib.parse
from pathlib import Path

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"

CSS = """
:root { --ink:#1d2430; --muted:#5b6575; --line:#d9dee6; --soft:#f5f7fa; --accent:#2f6db5; --win:#1f8a3b; }
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: #ffffff; color: var(--ink); font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }
main { max-width: 1120px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 1.9rem; line-height: 1.2; margin: 0.4em 0 0.5em; }
h2 { font-size: 1.45rem; margin: 2.2em 0 0.6em; padding-top: 0.6em; border-top: 2px solid var(--line); }
h3 { font-size: 1.18rem; margin: 1.8em 0 0.5em; }
h4 { font-size: 1.02rem; margin: 1.4em 0 0.4em; }
p, li { max-width: 78ch; }
a { color: var(--accent); }
code { background: var(--soft); border: 1px solid var(--line); border-radius: 4px; padding: 0 4px; font-size: 0.9em; }
hr { border: 0; border-top: 1px solid var(--line); margin: 2em 0; }
blockquote { margin: 1em 0; padding: 0.4em 1em; border-left: 4px solid var(--line); color: var(--muted); }
.table-wrap { overflow-x: auto; margin: 0.8em 0 1.2em; }
table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }
th, td { border: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: var(--soft); }
tbody tr:nth-child(even) td { background: #fbfcfd; }
.diagram { margin: 1em 0; padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: #fff; overflow-x: auto; }
.diagram pre.mermaid { margin: 0; text-align: center; font-size: 0.85rem; white-space: pre; }
.pair { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 20px; align-items: start; margin: 1em 0; }
.pair .diagram, .pair .table-wrap { margin: 0; }
nav.contents { background: var(--soft); border: 1px solid var(--line); border-radius: 8px; padding: 12px 20px; margin: 1.5em 0; }
nav.contents h2 { border: 0; margin: 0.2em 0 0.4em; padding: 0; font-size: 1.15rem; }
nav.contents ol { margin: 0; padding-left: 1.3em; }
nav.contents ol ol { padding-left: 1.1em; font-size: 0.95em; }
nav.contents li { margin: 2px 0; }
.note { color: var(--muted); font-size: 0.9rem; }
@media (max-width: 900px) { .pair { grid-template-columns: minmax(0, 1fr); } h1 { font-size: 1.55rem; } }
@media print {
  @page { margin: 14mm; }
  body { font-size: 10.5pt; }
  main { max-width: none; padding: 0; }
  a { color: inherit; text-decoration: none; }
  h2 { break-before: page; border-top: 0; }
  h2, h3, h4 { break-after: avoid; }
  .diagram, tr, .pair { break-inside: avoid; }
  .pair { grid-template-columns: minmax(0, 1fr); }
  .table-wrap { overflow: visible; }
  nav.contents { break-after: page; }
  .note.screen-only { display: none; }
}
"""


def slugify(text: str, seen: dict) -> str:
    """GitHub-style anchor: lower case, drop punctuation except hyphens, spaces become hyphens, duplicates numbered."""
    plain = re.sub(r"`([^`]*)`", r"\1", text)
    plain = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", plain)
    plain = plain.replace("*", "")
    slug = re.sub(r"[^\w\- ]", "", plain.strip().lower()).replace(" ", "-")
    if slug in seen:
        seen[slug] += 1
        slug = f"{slug}-{seen[slug]}"
    else:
        seen[slug] = 0
    return slug


def make_link_fn(md_path: Path, out_path: Path):
    def fn(url: str) -> str:
        if re.match(r"^(https?:|mailto:|#)", url):
            return url
        path, _, frag = url.partition("#")
        target = (md_path.parent / urllib.parse.unquote(path)).resolve()
        rel = os.path.relpath(target, out_path.parent.resolve()).replace(os.sep, "/")
        return urllib.parse.quote(rel) + (f"#{frag}" if frag else "")
    return fn


def inline(text: str, link_fn) -> str:
    out = []
    for part in re.split(r"(`[^`]+`)", text):
        if len(part) > 1 and part.startswith("`") and part.endswith("`"):
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        s = html.escape(part, quote=False)
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                   lambda m: f'<a href="{html.escape(link_fn(html.unescape(m.group(2))))}">{m.group(1)}</a>', s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        out.append(s)
    return "".join(out)


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render_table(lines: list[str], link_fn) -> str:
    head = split_row(lines[0])
    rows = [split_row(l) for l in lines[2:]]
    out = ['<div class="table-wrap"><table><thead><tr>']
    out += [f"<th>{inline(c, link_fn)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in rows:
        r = r + [""] * (len(head) - len(r))
        out.append("<tr>" + "".join(f"<td>{inline(c, link_fn)}</td>" for c in r[:len(head)]) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


LIST_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def render_list(lines: list[str], link_fn) -> str:
    items: list[list] = []  # [indent, ordered, number, text]
    for line in lines:
        m = LIST_ITEM.match(line)
        if m:
            marker = m.group(2)
            items.append([len(m.group(1).expandtabs(4)), marker[0].isdigit(), int(marker[:-1]) if marker[0].isdigit() else 1, m.group(3)])
        elif items:
            items[-1][3] += " " + line.strip()

    def build(i: int, indent: int) -> tuple[str, int]:
        ordered, start = items[i][1], items[i][2]
        tag = "ol" if ordered else "ul"
        parts = [f'<{tag}{f" start={start}" if ordered and start != 1 else ""}>']
        while i < len(items) and items[i][0] >= indent:
            ind, _, _, text = items[i]
            li = "<li>" + inline(text, link_fn)
            i += 1
            if i < len(items) and items[i][0] > ind:
                sub, i = build(i, items[i][0])
                li += sub
            parts.append(li + "</li>")
        parts.append(f"</{tag}>")
        return "".join(parts), i

    out, i = [], 0
    while i < len(items):
        chunk, i = build(i, items[i][0])
        out.append(chunk)
    return "".join(out)


def render(md_text: str, md_path: Path, out_path: Path) -> tuple[str, str, int]:
    link_fn = make_link_fn(md_path, out_path)
    lines = md_text.splitlines()
    blocks: list[str] = []
    headings: list[tuple[int, str, str]] = []
    seen: dict = {}
    title, para = "", []
    pair_pending, pair_diagram = False, None
    diagrams = 0

    def flush_para():
        if para:
            blocks.append("<p>" + inline(" ".join(l.strip() for l in para), link_fn) + "</p>")
            para.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_para()
            lang = stripped[3:].strip().lower()
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            code = html.escape("\n".join(body))
            if lang == "mermaid":
                diagrams += 1
                block = f'<div class="diagram"><pre class="mermaid">{code}</pre></div>'
                if pair_pending:
                    pair_diagram, pair_pending = block, False
                    blocks.append("\x00PAIR\x00")
                else:
                    blocks.append(block)
            else:
                blocks.append(f"<pre><code>{code}</code></pre>")
            continue
        if stripped == "<!-- contents -->":
            flush_para()
            blocks.append("\x00TOC\x00")
            i += 1
            continue
        if stripped == "<!-- pair -->":
            flush_para()
            pair_pending = True
            i += 1
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1 and not title:
                title = re.sub(r"[*`]", "", text)
            anchor = slugify(text, seen)
            if level in (2, 3):
                headings.append((level, anchor, text))
            blocks.append(f'<h{level} id="{anchor}">{inline(text, link_fn)}</h{level}>')
            i += 1
            continue
        if re.match(r"^\s*---+\s*$", line) and not para:
            blocks.append("<hr>")
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            flush_para()
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            table = render_table(tbl, link_fn)
            if pair_diagram is not None:
                idx = blocks.index("\x00PAIR\x00")
                blocks[idx] = f'<div class="pair">{pair_diagram}{table}</div>'
                pair_diagram = None
            else:
                blocks.append(table)
            continue
        if stripped.startswith(">"):
            flush_para()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append("<blockquote><p>" + inline(" ".join(quote), link_fn) + "</p></blockquote>")
            continue
        item = LIST_ITEM.match(line)
        # As on GitHub, a bullet list may interrupt a paragraph; a numbered list only when it starts at 1.
        if item and (not para or item.group(2) in ("-", "*", "1.")):
            flush_para()
            lst = []
            while i < len(lines) and lines[i].strip() and (LIST_ITEM.match(lines[i]) or lines[i].startswith((" ", "\t"))):
                lst.append(lines[i])
                i += 1
            blocks.append(render_list(lst, link_fn))
            continue
        if not stripped:
            flush_para()
            i += 1
            continue
        para.append(line)
        i += 1
    flush_para()
    if pair_diagram is not None:  # a pair marker with no table after it: keep the diagram on its own
        blocks[blocks.index("\x00PAIR\x00")] = pair_diagram

    toc = ['<nav class="contents" aria-label="Contents"><h2>Contents</h2><ol>']
    open_sub = False
    for level, anchor, text in headings:
        if level == 2:
            if open_sub:
                toc.append("</ol></li>")
                open_sub = False
            elif len(toc) > 1:
                toc.append("</li>")
            toc.append(f'<li><a href="#{anchor}">{inline(text, link_fn)}</a>')
        else:
            if not open_sub:
                toc.append("<ol>")
                open_sub = True
            toc.append(f'<li><a href="#{anchor}">{inline(text, link_fn)}</a></li>')
    toc.append("</ol></li></ol></nav>" if open_sub else "</li></ol></nav>")
    body = "\n".join("".join(toc) if b == "\x00TOC\x00" else b for b in blocks)
    return title, body, diagrams


def page(title: str, body: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(description)}">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<p class="note screen-only">The diagrams are drawn by Mermaid, loaded from a CDN; without an internet connection each diagram shows its source text.</p>
{body}
</main>
<script src="{MERMAID_CDN}"></script>
<script>
  if (window.mermaid) {{
    mermaid.initialize({{ startOnLoad: true, theme: "neutral", securityLevel: "strict", flowchart: {{ htmlLabels: true, useMaxWidth: true, curve: "basis" }} }});
  }}
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("markdown", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--title", help="page title (default: the first level-1 heading)")
    ap.add_argument("--description", default="Silverleaf strategy document rendered for review.")
    args = ap.parse_args()
    md_path, out_path = args.markdown.resolve(), args.output.resolve()
    title, body, diagrams = render(md_path.read_text(encoding="utf-8"), md_path, out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page(args.title or title or md_path.stem, body, args.description), encoding="utf-8", newline="\n")
    print(f"Wrote {out_path} ({diagrams} diagrams)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
