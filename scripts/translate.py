#!/usr/bin/env python3
"""
Translate Org Manual chapters from English to Chinese using free translation APIs.
Supports resuming interrupted translations.
"""

import os
import re
import json
import time
import hashlib
import requests
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "translated", "org", "chapters")
ZH_DIR = os.path.join(BASE_DIR, "translated", "zh", "chapters")
PROGRESS_FILE = os.path.join(BASE_DIR, "translated", "zh", "progress.json")

# Translation API settings
MYMEMORY_API = "https://api.mymemory.translated.net/get"
CHUNK_SIZE = 450  # MyMemory limit is 500 chars, use 450 for safety


def translate_chunk(text: str, source: str = "en", target: str = "zh") -> str:
    """Translate a chunk of text using MyMemory API."""
    if not text.strip():
        return text

    params = {
        "q": text,
        "langpair": f"{source}|{target}",
        "de": "org-manual-translate@example.com",  # Required by API
    }

    try:
        resp = requests.get(MYMEMORY_API, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("responseStatus") == 200:
            translated = data["responseData"]["translatedText"]
            # MyMemory sometimes returns uppercase for short strings
            if text.islower() and translated.isupper():
                translated = translated.lower()
            return translated
        else:
            # Check for rate limiting
            if data.get("responseStatus") == 429:
                time.sleep(5)
                return translate_chunk(text, source, target)
            return f"[翻译失败] {text}"
    except Exception as e:
        return f"[翻译错误: {e}] {text}"


def translate_text(text: str, max_chunk: int = CHUNK_SIZE) -> str:
    """Translate text, splitting into chunks if necessary."""
    if len(text) <= max_chunk:
        result = translate_chunk(text)
        time.sleep(0.5)  # Rate limiting
        return result

    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    translated_parts = []

    for para in paragraphs:
        if not para.strip():
            translated_parts.append('')
            continue

        if len(para) <= max_chunk:
            translated_parts.append(translate_chunk(para))
            time.sleep(0.5)
        else:
            # Split long paragraph by sentences
            sentences = re.split(r'(?<=[.!?])\s+', para)
            current_chunk = ""
            for sent in sentences:
                if len(current_chunk) + len(sent) + 1 > max_chunk:
                    if current_chunk:
                        translated_parts.append(translate_chunk(current_chunk))
                        time.sleep(0.5)
                    current_chunk = sent
                else:
                    current_chunk = f"{current_chunk} {sent}".strip()
            if current_chunk:
                translated_parts.append(translate_chunk(current_chunk))
                time.sleep(0.5)

    return '\n\n'.join(translated_parts)


def translate_org_line(line: str) -> str:
    """Translate a single org-mode line, preserving markup."""
    # Skip empty lines
    if not line.strip():
        return line

    # Skip org metadata
    if line.startswith('#+'):
        return line

    # Skip pure markup lines
    if line.strip() in ['- ', '|', '-----']:
        return line

    # Handle headings - preserve stars
    heading_match = re.match(r'^(\*+)\s+(.+)$', line)
    if heading_match:
        stars = heading_match.group(1)
        content = heading_match.group(2)
        translated = translate_chunk(content)
        time.sleep(0.3)
        return f"{stars} {translated}"

    # Handle list items
    list_match = re.match(r'^(\s*-\s+)(.+)$', line)
    if list_match:
        prefix = list_match.group(1)
        content = list_match.group(2)
        translated = translate_chunk(content)
        time.sleep(0.3)
        return f"{prefix}{translated}"

    # Handle table rows
    if line.startswith('|') and line.endswith('|'):
        # Translate each cell
        cells = line.split('|')[1:-1]
        translated_cells = []
        for cell in cells:
            cell = cell.strip()
            if cell:
                translated = translate_chunk(cell)
                time.sleep(0.2)
                translated_cells.append(f" {translated} ")
            else:
                translated_cells.append(' ')
        return '|' + '|'.join(translated_cells) + '|'

    # Handle example/code blocks - don't translate
    if line.startswith('#+BEGIN_') or line.startswith('#+END_'):
        return line

    # Regular text - translate
    # Preserve inline markup by extracting it first
    # Simple approach: translate the whole line
    return translate_chunk(line)


def translate_chapter(input_path: str, output_path: str, in_block: bool = False) -> None:
    """Translate a chapter file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    translated_lines = []
    in_example_block = False

    for line in lines:
        line = line.rstrip('\n')

        # Track example blocks - don't translate content inside
        if line.startswith('#+BEGIN_EXAMPLE') or line.startswith('#+BEGIN_SRC'):
            in_example_block = True
            translated_lines.append(line)
            continue
        elif line.startswith('#+END_EXAMPLE') or line.startswith('#+END_SRC'):
            in_example_block = False
            translated_lines.append(line)
            continue

        if in_example_block:
            translated_lines.append(line)
            continue

        # Translate the line
        translated = translate_org_line(line)
        translated_lines.append(translated)

    # Save translated file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(translated_lines))


def load_progress() -> dict:
    """Load translation progress."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "current": None}


def save_progress(progress: dict) -> None:
    """Save translation progress."""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def main():
    os.makedirs(ZH_DIR, exist_ok=True)

    # Load progress
    progress = load_progress()
    completed = set(progress.get("completed", []))

    # Get list of chapters
    chapters = sorted([f for f in os.listdir(CHAPTERS_DIR) if f.endswith('.org')])

    print(f"Found {len(chapters)} chapters, {len(completed)} already translated")
    print()

    for chapter_file in chapters:
        if chapter_file in completed:
            print(f"  ✓ {chapter_file} (already done)")
            continue

        input_path = os.path.join(CHAPTERS_DIR, chapter_file)
        output_path = os.path.join(ZH_DIR, chapter_file)

        print(f"  → Translating {chapter_file}...")
        progress["current"] = chapter_file
        save_progress(progress)

        # Get file size for estimation
        with open(input_path, 'r') as f:
            content = f.read()
        char_count = len(content)
        line_count = len(content.split('\n'))

        print(f"    {char_count} chars, ~{line_count} lines")

        # Translate (for now, just copy with header modified)
        # Full translation would take too long for demo
        try:
            translate_chapter(input_path, output_path)
            completed.add(chapter_file)
            progress["completed"] = list(completed)
            save_progress(progress)
            print(f"    ✓ Saved to {output_path}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            break

    print(f"\nTranslation complete! {len(completed)}/{len(chapters)} chapters done.")


def quick_translate():
    """Quick translation - just translate the first chapter as demo."""
    os.makedirs(ZH_DIR, exist_ok=True)

    # Translate only the introduction chapter
    input_file = "01-1-introduction.org"
    input_path = os.path.join(CHAPTERS_DIR, input_file)
    output_path = os.path.join(ZH_DIR, input_file)

    if not os.path.exists(input_path):
        # Find the introduction chapter
        chapters = sorted(os.listdir(CHAPTERS_DIR))
        for ch in chapters:
            if 'introduction' in ch.lower():
                input_file = ch
                input_path = os.path.join(CHAPTERS_DIR, ch)
                output_path = os.path.join(ZH_DIR, ch)
                break

    print(f"Translating {input_file}...")
    print("This may take a few minutes due to API rate limits...")

    translate_chapter(input_path, output_path)
    print(f"Done! Saved to {output_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_translate()
    else:
        main()
