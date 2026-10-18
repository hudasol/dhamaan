"""A small Markdown to HTML converter for the repository's own documents (standard library only).

Supports what the generated documents use: headings, paragraphs, bullet and numbered lists, tables, block
quotes, fenced code, inline code, bold, italic and links. Everything else is escaped as text.
"""
from __future__ import annotations

import html, re

INLINE_CODE = re.compile(r"`([^`]+)`")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ITALIC = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")
URL = re.compile(r"(?<![\"'=>])\b(https?://[^\s<|)]+)")


def inline(text: str) -> str:
    codes = []
    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>"); return f"\x00{len(codes) - 1}\x00"
    t = INLINE_CODE.sub(keep, text)
    t = html.escape(t, quote=False)
    t = LINK.sub(lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', t)
    t = URL.sub(lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>', t)
    t = BOLD.sub(r"<strong>\1</strong>", t)
    t = ITALIC.sub(r"<em>\1</em>", t)
    return re.sub("\x00(\\d+)\x00", lambda m: codes[int(m.group(1))], t)


def to_html(md: str) -> str:
    lines = [l for l in md.split("\n") if not l.startswith("<!--")]
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip(): i += 1; continue
        if line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"): j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>"); i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            n = len(m.group(1)); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); i += 1; continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"): rows.append(lines[i]); i += 1
            cells = [[c.strip() for c in r.strip().strip("|").split(" | ")] for r in rows]
            body = [c for c in cells[1:] if not all(re.fullmatch(r"-+", x.replace(":", "")) for x in c)]
            out.append('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in cells[0]) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>")
            continue
        if line.startswith(">"):
            block = []
            while i < len(lines) and lines[i].startswith(">"): block.append(lines[i][1:].strip()); i += 1
            out.append(f"<blockquote><p>{inline(' '.join(block))}</p></blockquote>"); continue
        if re.match(r"^\s*([-*]|\d+\.)\s", line):
            ordered = bool(re.match(r"^\s*\d+\.\s", line)); items = []
            while i < len(lines) and (re.match(r"^\s*([-*]|\d+\.)\s", lines[i]) or (lines[i].startswith("  ") and items)):
                if re.match(r"^\s*([-*]|\d+\.)\s", lines[i]): items.append(re.sub(r"^\s*([-*]|\d+\.)\s", "", lines[i]))
                elif lines[i].strip(): items[-1] += " " + lines[i].strip().lstrip("> ")
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||>|```|\s*([-*]|\d+\.)\s)", lines[i]):
            para.append(lines[i].strip()); i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)
