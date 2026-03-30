"""마크다운 → 티스토리 호환 HTML 변환"""

import re
import markdown
from pathlib import Path

from lib.code_highlight import highlight_code_blocks
from lib.image_handler import process_images

OUTPUT_DIR = Path(__file__).parent.parent / "output"
TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "tistory.html"


def convert_to_html(config: dict, filepath: str) -> tuple[str, str]:
    """마크다운 파일을 티스토리 HTML로 변환

    Returns:
        (html_body, output_path) - 본문 HTML과 미리보기 파일 경로
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # frontmatter 제거
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    # 옵시디언 위키링크 이미지 → 표준 마크다운 변환
    content = re.sub(r'!\[\[(.+?)\]\]', r'![\1](\1)', content)

    # 마크다운 → HTML 변환
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "nl2br",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {"use_pygments": False},  # 직접 처리할 것
        },
    )
    html_body = md.convert(content)

    # 코드 하이라이팅 적용
    html_body = highlight_code_blocks(html_body)

    # 이미지 처리
    html_body = process_images(html_body, filepath, config)

    # 미리보기 HTML 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_name = Path(filepath).stem + ".html"
    output_path = OUTPUT_DIR / output_name

    preview_html = generate_preview(html_body)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(preview_html)

    return html_body, str(output_path)


def generate_preview(body: str) -> str:
    """미리보기용 전체 HTML 생성"""
    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH, encoding="utf-8") as f:
            template = f.read()
        return template.replace("{{content}}", body)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>미리보기</title>
    <style>
        body {{
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.8;
            color: #333;
        }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; }}
        th {{ background: #f5f5f5; }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 0;
            padding: 10px 20px;
            color: #666;
            background: #f9f9f9;
        }}
        img {{ max-width: 100%; }}
    </style>
</head>
<body>
{body}
</body>
</html>"""
