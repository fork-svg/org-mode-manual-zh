#!/usr/bin/env python3
"""
Org 模式到 HTML 转换脚本
将 .org 文件转换为 HTML 用于 GitHub Pages
"""

import re
import sys
from pathlib import Path
from typing import List, Dict

def escape_html(text: str) -> str:
    """转义 HTML 特殊字符"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

def process_inline(text: str) -> str:
    """处理行内格式"""
    # 链接 [[url][text]] 或 [[url]]
    text = re.sub(r'\[\[([^\]]+)\]\[([^\]]+)\]\]', r'<a href="\1">\2</a>', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="\1">\1</a>', text)

    # 粗体 *text*
    text = re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', text)

    # 斜体 /text/
    text = re.sub(r'/([^/]+)/', r'<em>\1</em>', text)

    # 代码 =text= 或 ~text~
    text = re.sub(r'=([^=]+)=', r'<code>\1</code>', text)
    text = re.sub(r'~([^~]+)~', r'<code>\1</code>', text)

    # 下划线 _text_
    text = re.sub(r'_([^_]+)_', r'<u>\1</u>', text)

    # 删除线 +text+
    text = re.sub(r'\+([^\+]+)\+', r'<del>\1</del>', text)

    return text

def org_to_html(org_file: Path, title: str = None) -> str:
    """将 Org 文件转换为 HTML"""
    with open(org_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not title:
        title = org_file.stem

    html_parts = []
    html_parts.append(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(title)} - Org 模式手册</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="index.html">← 返回首页</a>
        </nav>
        <main class="content">
''')

    in_code_block = False
    in_table = False
    in_list = False
    list_items = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # 代码块
        if line.startswith('#+BEGIN_'):
            if in_table:
                html_parts.append('</table>\n')
                in_table = False
            in_code_block = True
            block_type = line[8:].split()[0] if len(line) > 8 else 'example'
            html_parts.append(f'<pre class="code-block code-{block_type.lower()}"><code>')
            i += 1
            while i < len(lines):
                code_line = lines[i].rstrip()
                if code_line.startswith('#+END_'):
                    html_parts.append('</code></pre>\n')
                    in_code_block = False
                    break
                html_parts.append(escape_html(code_line) + '\n')
                i += 1
            i += 1
            continue

        if in_code_block:
            html_parts.append(escape_html(line) + '\n')
            i += 1
            continue

        # 表格
        if line.startswith('|'):
            if not in_table:
                in_table = True
                html_parts.append('<table class="org-table">\n')

            if line.startswith('|-'):
                html_parts.append('</thead><tbody>\n')
            else:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                row = '<tr>' + ''.join(f'<td>{process_inline(cell)}</td>' for cell in cells) + '</tr>\n'
                html_parts.append(row)

            i += 1
            continue
        elif in_table:
            html_parts.append('</tbody></table>\n')
            in_table = False

        # 标题
        heading_match = re.match(r'^(\*+)\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = process_inline(heading_match.group(2))
            html_parts.append(f'<h{level}>{text}</h{level}>\n')
            i += 1
            continue

        # 无序列表
        list_match = re.match(r'^(\s*)[-+]\s+(.+)$', line)
        if list_match:
            indent = len(list_match.group(1))
            text = process_inline(list_match.group(2))

            if not in_list:
                html_parts.append('<ul>\n')
                in_list = True

            html_parts.append(f'<li>{text}</li>\n')
            i += 1
            continue
        elif in_list:
            html_parts.append('</ul>\n')
            in_list = False

        # 空行
        if not line.strip():
            html_parts.append('\n')
            i += 1
            continue

        # 普通段落
        html_parts.append(f'<p>{process_inline(line)}</p>\n')
        i += 1

    if in_table:
        html_parts.append('</tbody></table>\n')
    if in_list:
        html_parts.append('</ul>\n')

    html_parts.append('''        </main>
    </div>
</body>
</html>
''')

    return ''.join(html_parts)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: org2html.py <input.org> [output.html] [title]")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.with_suffix('.html')

    title = sys.argv[3] if len(sys.argv) >= 4 else input_file.stem

    html = org_to_html(input_file, title)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"已转换: {input_file} → {output_file}")

if __name__ == '__main__':
    main()
