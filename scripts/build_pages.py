#!/usr/bin/env python3
"""
构建 GitHub Pages 站点
将所有翻译的 Org 文件转换为 HTML
"""

import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from org2html import org_to_html

def build_pages():
    """构建所有页面"""
    project_dir = Path(__file__).parent.parent
    translated_dir = project_dir / 'translated' / 'zh'
    docs_dir = project_dir / 'docs'

    docs_dir.mkdir(exist_ok=True)

    # 映射章节
    chapters = {
        '00-前言.org': '前言',
        '01-简介.org': '简介',
        '02-文档结构.org': '文档结构',
        '03-表格.org': '表格',
        '04-超链接.org': '超链接',
        '05-todo项目.org': 'TODO 项目',
        '06-标签.org': '标签',
        '07-属性与列.org': '属性与列',
        '08-日期和时间.org': '日期和时间',
        '09-归档与重新归档.org': '归档与重新归档',
        '10-捕获与附件.org': '捕获与附件',
        '11-日程视图.org': '日程视图',
        '12-富文本标记.org': '富文本标记',
        '13-导出.org': '导出',
        '14-发布.org': '发布',
        '15-引用处理.org': '引用处理',
        '16-处理源代码.org': '处理源代码',
        '17-杂项.org': '杂项',
        'A-Hacking.org': '自定义 Org',
        'B-历史与致谢.org': '历史与致谢',
        'C-GFDL.org': 'GNU 自由文档许可证',
    }

    converted = 0
    for org_file, title in chapters.items():
        org_path = translated_dir / org_file
        if org_path.exists():
            html_name = org_path.stem + '.html'
            html_path = docs_dir / html_name

            html = org_to_html(org_path, title)

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)

            converted += 1
            print(f"✓ {org_file} → {html_name}")
        else:
            print(f"✗ 跳过 {org_file} (文件不存在)")

    print(f"\n共转换 {converted} 个文件")

if __name__ == '__main__':
    build_pages()
