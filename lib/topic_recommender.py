"""주제 & 블로그 제목 추천"""

import json
import click

from lib.ai_client import get_client
from lib.roadmap import get_latest_roadmap, load_roadmap, get_next_pending_topics


def recommend_next(config: dict, roadmap_name: str = None, count: int = 3, return_list: bool = False):
    # 로드맵에서 다음 주제 가져오기
    if roadmap_name:
        data = load_roadmap(roadmap_name)
        if not data:
            click.echo(f"로드맵을 찾을 수 없습니다: {roadmap_name}")
            return [] if return_list else None
    else:
        result = get_latest_roadmap()
        if not result:
            click.echo("로드맵이 없습니다. 먼저 'roadmap create'로 생성하세요.")
            return [] if return_list else None
        roadmap_name, data = result

    pending = get_next_pending_topics(data, count)
    if not pending:
        click.echo("모든 주제를 완료했습니다!")
        return [] if return_list else None

    # AI로 블로그 제목 추천
    client = get_client(config)

    system = """당신은 개발 블로그 제목 전문가입니다.
주어진 학습 주제에 대해 매력적인 블로그 제목을 추천하세요.

반드시 아래 JSON 형식만 출력하세요:
[
  {
    "topic": "원래 주제",
    "category": "카테고리",
    "title": "추천 블로그 제목",
    "tags": ["태그1", "태그2", "태그3"]
  }
]"""

    topics_text = "\n".join(
        f"- [{t['category']}] {t['title']}: {t['description']}"
        for t in pending
    )
    user = f"다음 주제들에 대해 블로그 제목을 추천해주세요:\n{topics_text}"

    response = client.chat(system, user)
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    recommendations = json.loads(text)

    # 출력
    click.echo("\n📝 추천 주제 & 블로그 제목:")
    for i, rec in enumerate(recommendations, 1):
        click.echo(f"\n  [{i}] {rec['title']}")
        click.echo(f"      카테고리: {rec['category']}")
        click.echo(f"      태그: {', '.join(rec['tags'])}")

    if return_list:
        return recommendations
    return None


def pick_topic(topics: list[dict]) -> dict:
    """사용자에게 주제 선택 받기"""
    if len(topics) == 1:
        return topics[0]

    choice = click.prompt("\n주제 번호를 선택하세요", type=int, default=1)
    idx = max(0, min(choice - 1, len(topics) - 1))
    return topics[idx]
