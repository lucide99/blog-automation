"""AI 블로그 글 작성"""

import click
from pathlib import Path
from datetime import datetime

from lib.ai_client import get_client

POSTS_DIR = Path(__file__).parent.parent / "posts"

STYLE_PROMPTS = {
    "tutorial": """튜토리얼/설명체 스타일로 작성하세요:
- 초보자도 따라할 수 있게 단계별로 설명
- 코드 예제는 반드시 포함하고, 각 코드에 설명 추가
- 실행 결과도 포함
- "왜" 이렇게 하는지 이유를 설명
- 마무리에 요약과 다음 단계 안내""",

    "til": """TIL(Today I Learned) 스타일로 작성하세요:
- 핵심 내용만 간결하게
- 코드 위주로, 불필요한 설명은 생략
- 배운 점, 주의할 점 위주
- 참고 자료 링크 형식으로 마무리""",
}


def write_post(config: dict, topic: str, style: str, metadata: dict = None) -> str:
    client = get_client(config)

    style_guide = STYLE_PROMPTS.get(style, STYLE_PROMPTS["tutorial"])
    tags = metadata.get("tags", []) if metadata else []
    category = metadata.get("category", "") if metadata else ""

    system = f"""당신은 경험이 풍부한 개발 블로거입니다.
한국어로 개발 블로그 글을 마크다운 형식으로 작성하세요.

{style_guide}

작성 규칙:
- 마크다운 형식으로 작성 (# 제목, ## 소제목, ```코드블록``` 등)
- 코드 블록에는 반드시 언어 지정 (```python, ```javascript 등)
- 이미지가 필요한 부분은 ![설명](image_placeholder.png)으로 표시
- 글 시작에 짧은 도입부 포함
- 적절한 길이로 작성 (너무 짧지도, 길지도 않게)"""

    user = f"주제: {topic}"
    if category:
        user += f"\n카테고리: {category}"
    if tags:
        user += f"\n태그: {', '.join(tags)}"

    click.echo(f"글 작성 중: {topic}...")
    content = client.chat(system, user)

    # frontmatter 추가
    date = datetime.now().strftime("%Y-%m-%d")
    slug = topic.lower().replace(" ", "-")[:50]
    filename = f"{date}-{slug}.md"

    frontmatter = f"""---
title: "{topic}"
date: {date}
category: "{category}"
tags: {tags}
style: {style}
---

"""

    full_content = frontmatter + content

    # 로컬 posts/ 에 저장
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = POSTS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    # 옵시디언 볼트에도 저장
    obsidian_path = save_to_obsidian(config, filename, full_content)
    if obsidian_path:
        click.echo(f"옵시디언 저장: {obsidian_path}")

    return str(filepath)


def save_to_obsidian(config: dict, filename: str, content: str) -> str | None:
    obsidian_cfg = config.get("obsidian", {})
    vault_path = obsidian_cfg.get("vault_path", "")
    if not vault_path:
        return None

    vault = Path(vault_path).expanduser()
    blog_folder = vault / obsidian_cfg.get("blog_folder", "Blog")
    blog_folder.mkdir(parents=True, exist_ok=True)

    dest = blog_folder / filename
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)

    return str(dest)
