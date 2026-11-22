#!/usr/bin/env python3
"""Fetch all sub-sections of Chapter 12 from Org manual and extract text content."""

import subprocess
import re
from html.parser import HTMLParser

SECTIONS = [
    ("Paragraphs", "https://orgmode.org/manual/Paragraphs.html"),
    ("Emphasis and Monospace", "https://orgmode.org/manual/Emphasis-and-Monospace.html"),
    ("Subscripts and Superscripts", "https://orgmode.org/manual/Subscripts-and-Superscripts.html"),
    ("Special Symbols", "https://orgmode.org/manual/Special-Symbols.html"),
    ("Embedded LaTeX", "https://orgmode.org/manual/Embedded-LaTeX.html"),
    ("Literal Examples", "https://orgmode.org/manual/Literal-Examples.html"),
    ("Images and Link Previews", "https://orgmode.org/manual/Images-and-link-previews.html"),
    ("Captions", "https://orgmode.org/manual/Captions.html"),
    ("Horizontal Rules", "https://orgmode.org/manual/Horizontal-Rules.html"),
    ("Creating Footnotes", "https://orgmode.org/manual/Creating-Footnotes.html"),
]

OUTPUT_FILE = "/home/scientist/project2115315057306361858/ResearchSpace/org-mode-manual-zh/source/text/ch12-markup-raw.txt"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.skip = False
        self.in_content = False
        self.skip_tags = 0  # nesting depth for skipped tags

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ('script', 'style', 'nav', 'header', 'footer'):
            self.skip = True
            self.skip_tags += 1
        if tag == 'main' or (tag == 'div' and attrs_dict.get('id', '') == 'content'):
            self.in_content = True
        if tag in ('p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'pre', 'dt', 'dd', 'code'):
            self.result.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'header', 'footer'):
            self.skip_tags -= 1
            if self.skip_tags <= 0:
                self.skip = False
                self.skip_tags = 0
        if tag in ('p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'pre', 'dt', 'dd', 'code'):
            self.result.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.result.append(data)

    def get_text(self):
        return ''.join(self.result)


def fetch_url(url):
    """Fetch a URL using curl with 3-second connect timeout."""
    result = subprocess.run(
        ['curl', '-s', '-L', '--connect-timeout', '3', '--max-time', '30', url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  [ERROR] curl failed for {url}: {result.stderr}")
        return None
    return result.stdout


def extract_text(html_content):
    """Extract text from HTML using the TextExtractor parser."""
    parser = TextExtractor()
    parser.feed(html_content)
    text = parser.get_text()
    # Clean up excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def main():
    all_content = []
    all_content.append("=" * 80)
    all_content.append("Org Mode Manual - Chapter 12: Markup for Rich Contents")
    all_content.append("Raw text content fetched from https://orgmode.org/manual/")
    all_content.append("=" * 80)
    all_content.append("")

    for section_name, url in SECTIONS:
        print(f"Fetching: {section_name} ({url})")
        html = fetch_url(url)
        if html is None:
            all_content.append(f"[ERROR: Failed to fetch {url}]")
            all_content.append("")
            continue

        text = extract_text(html)

        if not text:
            print(f"  [WARNING] No text extracted from {url}")
            all_content.append(f"[WARNING: No content extracted from {url}]")
            all_content.append("")
            continue

        # Add section separator and content
        all_content.append("-" * 80)
        all_content.append(f"Section: {section_name}")
        all_content.append(f"URL: {url}")
        all_content.append("-" * 80)
        all_content.append("")
        all_content.append(text)
        all_content.append("")

        print(f"  Extracted {len(text)} characters")

    # Write output
    final_content = '\n'.join(all_content)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"\nDone! Total content: {len(final_content)} characters")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
