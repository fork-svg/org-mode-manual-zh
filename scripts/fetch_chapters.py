#!/usr/bin/env python3
"""Fetch all chapters from the Org Manual (HTML version)."""

import os
import re
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://orgmode.org/manual"

# All chapter slugs extracted from the table of contents
CHAPTERS = [
    # Main chapters
    ("Introduction", "Introduction"),
    ("Document-Structure", "Document-Structure"),
    ("Tables", "Tables"),
    ("Hyperlinks", "Hyperlinks"),
    ("TODO-Items", "TODO-Items"),
    ("Tags", "Tags"),
    ("Properties-and-Columns", "Properties-and-Columns"),
    ("Dates-and-Times", "Dates-and-Times"),
    ("Refiling-and-Archiving", "Refiling-and-Archiving"),
    ("Capture-and-Attachments", "Capture-and-Attachments"),
    ("Agenda-Views", "Agenda-Views"),
    ("Markup", "Markup"),
    ("Exporting", "Exporting"),
    ("Publishing", "Publishing"),
    ("Citation-handling", "Citation-handling"),
    ("Working-with-Source-Code", "Working-with-Source-Code"),
    ("Miscellaneous", "Miscellaneous"),
    # Appendices
    ("Hacking", "Hacking"),
    ("History-and-Acknowledgments", "History-and-Acknowledgments"),
    ("GNU-Free-Documentation-License", "GNU-Free-Documentation-License"),
    ("Main-Index", "Main-Index"),
    ("Key-Index", "Key-Index"),
    ("Command-and-Function-Index", "Command-and-Function-Index"),
    ("Variable-Index", "Variable-Index"),
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "source")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_chapter(slug: str, name: str) -> dict:
    """Fetch a single chapter."""
    url = f"{BASE_URL}/{slug}.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return {"slug": slug, "name": name, "html": resp.text, "url": url, "ok": True}
    except Exception as e:
        return {"slug": slug, "name": name, "html": "", "url": url, "ok": False, "error": str(e)}


def extract_content(html: str) -> str:
    """Extract main content from HTML, stripping nav/header/footer."""
    # Find the main content section
    # The org manual HTML has <div id="content"> or similar
    # Try to find content between navigation elements

    # Remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

    # Try to find the main content area
    patterns = [
        r'<div\s+class="chapter-section"[^>]*>(.*?)</div>\s*<div\s+class="nav">',
        r'<div\s+id="content"[^>]*>(.*?)</div>\s*</div>\s*<div\s+class="nav">',
        r'<div\s+class="section"[^>]*>(.*?)<div\s+class="nav">',
    ]

    for pat in patterns:
        m = re.search(pat, html, re.DOTALL)
        if m:
            return m.group(1).strip()

    # Fallback: return everything between body tags
    m = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    if m:
        return m.group(1).strip()

    return html


def html_to_text(html: str) -> str:
    """Convert HTML to plain text with basic formatting."""
    # Headers
    for i in range(6, 0, -1):
        html = re.sub(
            rf'<h{i}[^>]*>(.*?)</h{i}>',
            lambda m, lvl=i: '\n' + '#' * lvl + ' ' + m.group(1).strip() + '\n',
            html, flags=re.DOTALL
        )

    # Paragraphs
    html = re.sub(r'<p[^>]*>', '\n', html)
    html = re.sub(r'</p>', '\n', html)

    # Line breaks
    html = re.sub(r'<br\s*/?>', '\n', html)

    # Bold/strong
    html = re.sub(r'<(?:b|strong)[^>]*>(.*?)</(?:b|strong)>', r'*\1*', html, flags=re.DOTALL)

    # Italic/em
    html = re.sub(r'<(?:i|em)[^>]*>(.*?)</(?:i|em)>', r'/\1/', html, flags=re.DOTALL)

    # Code
    html = re.sub(r'<code[^>]*>(.*?)</code>', r'=\1=', html, flags=re.DOTALL)

    # Pre blocks
    html = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n#+BEGIN_EXAMPLE\n\1\n#+END_EXAMPLE\n', html, flags=re.DOTALL)

    # Links
    html = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[[\1][\2]]', html, flags=re.DOTALL)

    # Lists
    html = re.sub(r'<li[^>]*>', '\n- ', html)
    html = re.sub(r'</?(?:ul|ol)[^>]*>', '\n', html)

    # Definition lists
    html = re.sub(r'<dt[^>]*>', '\n', html)
    html = re.sub(r'<dd[^>]*>', '\n  ', html)

    # Tables
    html = re.sub(r'<tr[^>]*>', '\n|', html)
    html = re.sub(r'<t[dh][^>]*>', ' ', html)
    html = re.sub(r'</tr[^>]*>', '|', html)

    # Remove remaining HTML tags
    html = re.sub(r'<[^>]+>', '', html)

    # Clean up whitespace
    html = re.sub(r'&amp;', '&', html)
    html = re.sub(r'&lt;', '<', html)
    html = re.sub(r'&gt;', '>', html)
    html = re.sub(r'&quot;', '"', html)
    html = re.sub(r'&#39;', "'", html)
    html = re.sub(r'&nbsp;', ' ', html)

    # Clean up multiple blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html.strip()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Fetching {len(CHAPTERS)} chapters from {BASE_URL}...")
    print()

    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_chapter, slug, name): slug for slug, name in CHAPTERS}
        for future in as_completed(futures):
            result = future.result()
            slug = result["slug"]
            results[slug] = result
            status = "OK" if result["ok"] else f"FAIL: {result.get('error', '')}"
            print(f"  {'✓' if result['ok'] else '✗'} {result['name']}: {status}")

    print(f"\nFetched {sum(1 for r in results.values() if r['ok'])}/{len(CHAPTERS)} chapters")

    # Save raw HTML
    for slug, result in results.items():
        if result["ok"]:
            html_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(result["html"])

    # Convert and save as text
    text_dir = os.path.join(OUTPUT_DIR, "text")
    os.makedirs(text_dir, exist_ok=True)

    for slug, result in results.items():
        if result["ok"]:
            content = extract_content(result["html"])
            text = html_to_text(content)
            text_path = os.path.join(text_dir, f"{slug}.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  Converted: {slug} ({len(text)} chars)")

    # Save chapter index
    index_path = os.path.join(OUTPUT_DIR, "chapters.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump([
            {"slug": slug, "name": name, "fetched": results[slug]["ok"]}
            for slug, name in CHAPTERS
        ], f, indent=2, ensure_ascii=False)

    print(f"\nDone! Files saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
