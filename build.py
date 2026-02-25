#!/usr/bin/env python3
"""
Build script for Owen Queen's personal website.

Loads modular Markdown content plus publication entries and renders
the final index.html from template.html.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
PUBLICATIONS_DIR = CONTENT_DIR / "publications"
SECTION_FILES = {
    "ABOUT": CONTENT_DIR / "about.md",
    "NEWS": CONTENT_DIR / "news.md",
}
PUBLICATION_ORDER_FILE = CONTENT_DIR / "publications_order.txt"
SELECTED_PUBLICATIONS_FILE = CONTENT_DIR / "selected_publications.txt"
NEWS_LIMIT = 8
AUTHOR_HIGHLIGHT = "Owen Queen"


def process_inline(text: str) -> str:
    """Apply minimal inline Markdown formatting."""
    def replace_links(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_links, text)
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"_([^_]+)_", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def markdown_to_html(markdown_text: str) -> str:
    """Convert a limited subset of Markdown into HTML."""
    lines = markdown_text.strip().splitlines()
    html_lines: List[str] = []
    buffer: List[str] = []
    in_list = False

    def flush_paragraph() -> None:
        nonlocal buffer
        if buffer:
            paragraph = " ".join(buffer).strip()
            if paragraph:
                html_lines.append(f"<p>{paragraph}</p>")
            buffer = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        if stripped.startswith("#"):
            flush_paragraph()
            close_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            content = stripped[level:].strip()
            level = max(1, min(level, 6))
            html_lines.append(f"<h{level}>{process_inline(content)}</h{level}>")
            continue

        if stripped.startswith(("-", "* ")):
            flush_paragraph()
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = stripped.lstrip("-*").strip()
            html_lines.append(f"<li>{process_inline(item)}</li>")
            continue

        buffer.append(process_inline(stripped))

    flush_paragraph()
    close_list()
    return "\n".join(html_lines)


def indent_html(html_fragment: str, spaces: int = 12) -> str:
    padding = " " * spaces
    lines = [line for line in html_fragment.splitlines() if line.strip()]
    return "\n".join(f"{padding}{line}" for line in lines)


def split_front_matter(text: str) -> Tuple[str, str]:
    text = text.strip()
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    meta = parts[1].strip()
    body = parts[2].strip()
    return meta, body


def split_top_level(text: str, sep: str = ",") -> List[str]:
    parts: List[str] = []
    buffer: List[str] = []
    depth = 0
    in_quote = False
    escape = False

    for char in text:
        if escape:
            buffer.append(char)
            escape = False
            continue
        if char == "\\":
            buffer.append(char)
            escape = True
            continue
        if char == "\"":
            in_quote = not in_quote
            buffer.append(char)
            continue
        if not in_quote:
            if char == "{":
                depth += 1
            elif char == "}":
                depth = max(0, depth - 1)
        if char == sep and depth == 0 and not in_quote:
            part = "".join(buffer).strip()
            if part:
                parts.append(part)
            buffer = []
            continue
        buffer.append(char)

    tail = "".join(buffer).strip()
    if tail:
        parts.append(tail)
    return parts


def clean_latex(text: str) -> str:
    if not text:
        return ""
    cleaned = text
    cleaned = re.sub(r"\\textbf\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\emph\{([^}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", cleaned)
    cleaned = cleaned.replace("~", " ")
    cleaned = cleaned.replace("{", "").replace("}", "")
    cleaned = cleaned.replace("$^*$", "*")
    cleaned = cleaned.replace("$", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def format_authors(authors_raw: str) -> str:
    if not authors_raw:
        return ""
    authors_clean = clean_latex(authors_raw)
    parts = [a.strip() for a in authors_clean.split(" and ") if a.strip()]
    formatted: List[str] = []
    for part in parts:
        if "," in part:
            last, first = [p.strip() for p in part.split(",", 1)]
            name = f"{first} {last}".strip()
        else:
            name = part
        formatted.append(name)
    return ", ".join(formatted)


def highlight_author(authors: str, name: str = AUTHOR_HIGHLIGHT) -> str:
    if not authors:
        return authors
    pattern = re.compile(rf"\\b({re.escape(name)})\\b(\\*)?")

    def replace(match: re.Match[str]) -> str:
        star = match.group(2) or ""
        return f'<span class="author-highlight">{match.group(1)}</span>{star}'

    return pattern.sub(replace, authors)


def parse_bibtex_entry(text: str) -> Tuple[Dict[str, str], str]:
    match = re.search(r"@\w+\s*\{", text)
    if not match:
        return {}, text.strip()
    start = match.start()
    brace_start = text.find("{", start)
    if brace_start == -1:
        return {}, text.strip()

    depth = 0
    end = None
    for idx in range(brace_start, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = idx
                break
    if end is None:
        return {}, text.strip()

    entry_raw = text[start : end + 1].strip()
    remainder = text[end + 1 :].strip()

    header_end = entry_raw.find("{")
    inner = entry_raw[header_end + 1 : -1].strip()
    if not inner:
        return {}, remainder

    parts = split_top_level(inner, sep=",")
    if not parts:
        return {}, remainder
    fields: Dict[str, str] = {}
    fields["__key__"] = parts[0].strip()
    for part in parts[1:]:
        if "=" not in part:
            continue
        name, value = part.split("=", 1)
        key = name.strip().lower()
        val = value.strip().rstrip(",").strip()
        if val.startswith("{") and val.endswith("}"):
            val = val[1:-1].strip()
        elif val.startswith("\"") and val.endswith("\""):
            val = val[1:-1].strip()
        fields[key] = val
    return fields, remainder


def trim_news(markdown_text: str, limit: int = NEWS_LIMIT) -> str:
    lines = markdown_text.strip().splitlines()
    kept: List[str] = []
    count = 0

    for line in lines:
        stripped = line.strip()
        is_bullet = stripped.startswith(("* ", "- "))
        if is_bullet:
            count += 1
            if count > limit:
                continue
        kept.append(line)

    return "\n".join(kept)


def render_news(markdown_text: str) -> str:
    """Convert bullet news lines into a list with highlighted dates."""
    items: List[str] = []
    for raw in markdown_text.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        if not line.startswith(("* ", "- ")):
            continue
        content = line.lstrip("*-").strip()
        date_part = ""
        text_part = content
        if " - " in content:
            date_part, text_part = content.split(" - ", 1)
        text_part = process_inline(text_part)
        items.append(
            f'        <li><span class="news-date">{date_part}</span><span class="news-text">{text_part}</span></li>'
        )
    if not items:
        return ""
    return "<ul class=\"news-list\">\n" + "\n".join(items) + "\n    </ul>"


def load_publication_order() -> List[str]:
    if not PUBLICATION_ORDER_FILE.exists():
        return []
    return [
        line.strip()
        for line in PUBLICATION_ORDER_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_publications() -> Dict[str, Dict[str, object]]:
    publications: Dict[str, Dict[str, object]] = {}
    if not PUBLICATIONS_DIR.exists():
        return publications

    for path in PUBLICATIONS_DIR.glob("*.md"):
        raw = path.read_text(encoding="utf-8")
        meta_raw, body = split_front_matter(raw)
        metadata = json.loads(meta_raw) if meta_raw else {}
        bib_fields, notes_text = parse_bibtex_entry(body)

        title = ""
        authors = ""
        venue = ""
        year = ""
        if bib_fields:
            title = clean_latex(bib_fields.get("title", ""))
            authors = format_authors(bib_fields.get("author", ""))
            venue = clean_latex(
                bib_fields.get("journal")
                or bib_fields.get("booktitle")
                or bib_fields.get("publisher")
                or bib_fields.get("institution", "")
            )
            year = clean_latex(bib_fields.get("year", ""))
        else:
            title = metadata.get("title", "")
            authors = metadata.get("authors", "")
            venue = metadata.get("venue", "")
            year = metadata.get("year", "")

        publications[path.stem] = {
            "title": title,
            "authors": highlight_author(authors),
            "venue": venue,
            "year": year,
            "links": metadata.get("links", []),
            "image": metadata.get("image", ""),
            "image_link": metadata.get("image_link", ""),
            "notes": markdown_to_html(notes_text),
        }
    return publications


def generate_publications_html(
    publications: Dict[str, Dict[str, object]],
    keys: List[str],
) -> str:
    items: List[str] = []

    for key in keys:
        pub = publications.get(key)
        if not pub:
            continue

        note_html = pub.get("notes", "")
        links = pub.get("links", [])
        image = str(pub.get("image", "") or "").strip()
        image_link = str(pub.get("image_link", "") or "").strip()
        if not image_link and links:
            image_link = links[0].get("url", "")
        entry = [
            '            <article class="publication">',
            '                <div class="pub-main">',
            f"                    <h3>{pub.get('title', '')}</h3>",
            f'                    <p class="pub-authors">{pub.get("authors", "")}</p>',
            f'                    <p class="pub-venue">{pub.get("venue", "")} · {pub.get("year", "")}</p>',
        ]

        if note_html:
            entry.append('                    <div class="pub-note">')
            entry.append(indent_html(note_html, spaces=24))
            entry.append("                    </div>")
        if links:
            entry.append('                    <div class="pub-links">')
            for link in links:
                entry.append(
                    f'                        <a href="{link["url"]}">{link["label"]}</a>'
                )
            entry.append("                    </div>")

        entry.append("                </div>")
        if image:
            img_tag = f'<img src="{image}" alt="{pub.get("title", "")} thumbnail">'
            if image_link:
                entry.append(f'                <a class="pub-thumb" href="{image_link}">{img_tag}</a>')
            else:
                entry.append(f"                <div class=\"pub-thumb\">{img_tag}</div>")
        entry.append("            </article>")
        items.append("\n".join(entry))

    return "\n".join(items)


def load_sections() -> Dict[str, str]:
    sections: Dict[str, str] = {}
    for placeholder, path in SECTION_FILES.items():
        if not path.exists():
            sections[placeholder] = ""
            continue
        raw = path.read_text(encoding="utf-8")
        if placeholder == "NEWS":
            raw = trim_news(raw)
            sections[placeholder] = render_news(raw)
        else:
            sections[placeholder] = markdown_to_html(raw)
    return sections


def build() -> None:
    sections = load_sections()
    publications = load_publications()
    order = load_publication_order() or sorted(publications.keys(), reverse=True)
    # Keep manual ordering, but include any publication files not yet listed.
    order = [key for key in order if key in publications]
    missing_from_order = sorted(
        [key for key in publications.keys() if key not in order],
        reverse=True,
    )
    order.extend(missing_from_order)

    selected_keys: List[str] = []
    if SELECTED_PUBLICATIONS_FILE.exists():
        selected_keys = [
            line.strip()
            for line in SELECTED_PUBLICATIONS_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    if not selected_keys:
        selected_keys = order

    selected_keys = [key for key in selected_keys if key in publications]

    selected_html = generate_publications_html(publications, selected_keys)
    all_html = generate_publications_html(publications, order)

    template = (ROOT / "template.html").read_text(encoding="utf-8")
    for placeholder, html in sections.items():
        template = template.replace(f"{{{{{placeholder}}}}}", html)
    template = template.replace("{{SELECTED_PUBLICATIONS}}", selected_html)

    (ROOT / "index.html").write_text(template, encoding="utf-8")

    all_template = (ROOT / "publications_template.html").read_text(encoding="utf-8")
    all_template = all_template.replace("{{PUBLICATIONS}}", all_html)
    (ROOT / "publications.html").write_text(all_template, encoding="utf-8")

    print("Built index.html and publications.html")


if __name__ == "__main__":
    build()
