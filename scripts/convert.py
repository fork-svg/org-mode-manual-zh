#!/usr/bin/env python3
"""Convert the full Org Manual HTML to org-mode format, split into chapters."""

import os
import re
import html as html_mod

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SOURCE_HTML = os.path.join(BASE_DIR, "source", "org.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "translated", "org")


def decode_entities(text: str) -> str:
    """Decode HTML entities."""
    text = html_mod.unescape(text)
    # Fix common ones
    text = text.replace('&nbsp;', ' ')
    text = text.replace('\xa0', ' ')
    return text


def convert_html_to_org(html: str) -> str:
    """Convert an HTML fragment to org-mode markup."""
    # Remove nav panels
    html = re.sub(r'<p class="nav-panel">.*?</p>', '', html, flags=re.DOTALL)

    # Remove copiable links (the ¶ anchors)
    html = re.sub(r'<a class="copiable-link"[^>]*>.*?</a>', '', html, flags=re.DOTALL)

    # Remove index entry anchors
    html = re.sub(r'<a class="index-entry-id"[^>]*></a>', '', html)

    # Convert code blocks first (before other transformations)
    def convert_pre(m):
        content = m.group(1)
        # Remove inner tags
        content = re.sub(r'<[^>]+>', '', content)
        content = decode_entities(content)
        return f'\n#+BEGIN_EXAMPLE\n{content}\n#+END_EXAMPLE\n'

    html = re.sub(r'<pre[^>]*>(.*?)</pre>', convert_pre, html, flags=re.DOTALL)

    # Convert kbd
    html = re.sub(r'<kbd class="kbd"[^>]*>(.*?)</kbd>', lambda m: f'={m.group(1)}=', html, flags=re.DOTALL)
    html = re.sub(r'<kbd[^>]*>(.*?)</kbd>', lambda m: f'={m.group(1)}=', html, flags=re.DOTALL)

    # Convert code/samp/var
    html = re.sub(r'<code[^>]*>(.*?)</code>', lambda m: f'={m.group(1)}=', html, flags=re.DOTALL)
    html = re.sub(r'<samp[^>]*>(.*?)</samp>', lambda m: f'"{m.group(1)}"', html, flags=re.DOTALL)
    html = re.sub(r'<var[^>]*>(.*?)</var>', lambda m: f'_{m.group(1)}_', html, flags=re.DOTALL)

    # Convert emphasis
    html = re.sub(r'<em[^>]*>(.*?)</em>', lambda m: f'/{m.group(1)}/', html, flags=re.DOTALL)
    html = re.sub(r'<strong[^>]*>(.*?)</strong>', lambda m: f'*{m.group(1)}*', html, flags=re.DOTALL)
    html = re.sub(r'<b[^>]*>(.*?)</b>', lambda m: f'*{m.group(1)}*', html, flags=re.DOTALL)

    # Convert links
    def convert_link(m):
        href = m.group(1) or ''
        text = m.group(2) or ''
        text = re.sub(r'<[^>]+>', '', text).strip()
        if not text:
            text = href
        if href.startswith('#'):
            return f'[[{href}][{text}]]'
        return f'[[{href}][{text}]]'

    html = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', convert_link, html, flags=re.DOTALL)

    # Convert headings
    for i in range(6, 0, -1):
        def make_heading(m, level=i):
            text = m.group(1)
            text = re.sub(r'<[^>]+>', '', text).strip()
            text = decode_entities(text)
            return '\n' + '*' * level + ' ' + text + '\n'
        html = re.sub(
            rf'<h{i}[^>]*>(?:<span>)?(.*?)(?:</span>)?</h{i}>',
            make_heading,
            html, flags=re.DOTALL
        )

    # Convert tables
    def convert_table(m):
        table_html = m.group(0)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        result = []
        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            cell_texts = []
            for cell in cells:
                cell_text = re.sub(r'<[^>]+>', '', cell).strip()
                cell_text = decode_entities(cell_text)
                cell_texts.append(cell_text)
            if cell_texts:
                result.append('| ' + ' | '.join(cell_texts) + ' |')
        return '\n' + '\n'.join(result) + '\n' if result else ''

    html = re.sub(r'<table[^>]*>.*?</table>', convert_table, html, flags=re.DOTALL)

    # Convert lists
    html = re.sub(r'<li[^>]*>', '\n- ', html)
    html = re.sub(r'</?(?:ul|ol)[^>]*>', '\n', html)
    html = re.sub(r'<dt[^>]*>', '\n', html)
    html = re.sub(r'<dd[^>]*>', '\n  ', html)
    html = re.sub(r'</?(?:dl)[^>]*>', '\n', html)

    # Convert paragraphs
    html = re.sub(r'<p[^>]*>', '\n', html)
    html = re.sub(r'</p>', '\n', html)
    html = re.sub(r'<br\s*/?>', '\n', html)

    # Convert hr
    html = re.sub(r'<hr[^>]*>', '\n-----\n', html)

    # Convert definition lists
    html = re.sub(r'<dl[^>]*>', '\n', html)
    html = re.sub(r'</dl>', '\n', html)

    # Remove remaining tags
    html = re.sub(r'<[^>]+>', '', html)

    # Decode entities
    html = decode_entities(html)

    # Clean up whitespace
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html.strip()


def split_chapters(org_text: str):
    """Split the org text into chapters (by numbered H2 headings like ** 1 Introduction)."""
    chapters = []
    lines = org_text.split('\n')

    # Match chapter headings like "** 1 Introduction", "** 2 Document Structure", etc.
    # Also match appendices like "** A Hacking", "** B History..."
    chapter_pattern = re.compile(r'^\*\* (\d+|[A-Z])\s+(.+)$')

    current_chapter = {"title": "前言与目录", "content": []}
    for line in lines:
        m = chapter_pattern.match(line)
        if m and current_chapter["content"]:
            # Save previous chapter
            chapters.append(current_chapter)
            num = m.group(1)
            title = m.group(2).strip()
            current_chapter = {"title": f"{num} {title}", "content": [line]}
        else:
            current_chapter["content"].append(line)

    if current_chapter["content"]:
        chapters.append(current_chapter)

    return chapters


def slugify(title: str) -> str:
    """Convert a title to a filename slug."""
    # Remove chapter numbers
    title = re.sub(r'^\d+\s+', '', title)
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    return slug or "chapter"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Reading source HTML...")
    with open(SOURCE_HTML, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract the main content (between body tags)
    m = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
    if m:
        body = m.group(1)
    else:
        body = html_content

    print("Converting HTML to org-mode...")
    org_text = convert_html_to_org(body)

    # Add title
    org_full = "#+TITLE: Org 模式手册（中文翻译）\n"
    org_full += "#+SUBTITLE: The Org Manual - Chinese Translation\n"
    org_full += "#+LANGUAGE: zh\n"
    org_full += "#+OPTIONS: toc:t num:t\n\n"
    org_full += org_text

    # Save full version
    full_path = os.path.join(OUTPUT_DIR, "org-manual-zh.org")
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(org_full)
    print(f"Full manual saved: {full_path} ({len(org_full)} chars)")

    # Split into chapters
    chapters = split_chapters(org_text)
    print(f"\nSplitting into {len(chapters)} chapters...")

    chapter_dir = os.path.join(OUTPUT_DIR, "chapters")
    os.makedirs(chapter_dir, exist_ok=True)

    chapter_index = []
    for i, ch in enumerate(chapters):
        slug = f"{i:02d}-{slugify(ch['title'])}"
        content = '\n'.join(ch['content'])
        filename = f"{slug}.org"
        filepath = os.path.join(chapter_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        char_count = len(content)
        chapter_index.append({
            "num": i,
            "title": ch['title'],
            "filename": filename,
            "chars": char_count,
        })
        print(f"  [{i:2d}] {ch['title'][:60]}: {char_count:>7} chars")

    # Save index
    import json
    index_path = os.path.join(OUTPUT_DIR, "chapters.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(chapter_index, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {len(chapters)} chapters saved to {chapter_dir}/")


if __name__ == "__main__":
    main()
