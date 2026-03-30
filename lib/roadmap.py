"""학습 로드맵 생성/관리/진행추적"""

import json
import yaml
import click
from pathlib import Path
from datetime import datetime

from lib.ai_client import get_client

ROADMAPS_DIR = Path(__file__).parent.parent / "roadmaps"


def create_roadmap(config: dict, field: str) -> str:
    client = get_client(config)

    system = """당신은 개발 학습 로드맵 설계 전문가입니다.
사용자가 지정한 분야에 대해 체계적인 학습 로드맵을 JSON으로 생성하세요.

반드시 아래 JSON 형식만 출력하세요 (다른 텍스트 없이):
{
  "field": "분야명",
  "description": "분야 설명",
  "categories": [
    {
      "name": "대분류명",
      "topics": [
        {
          "title": "학습 주제",
          "description": "주제 설명",
          "difficulty": "beginner|intermediate|advanced",
          "suggested_tags": ["태그1", "태그2"]
        }
      ]
    }
  ]
}

각 대분류에 3-5개 주제, 총 15-25개 주제를 포함하세요.
난이도 순서대로 배치하세요."""

    user = f'"{field}" 분야의 개발 학습 로드맵을 만들어주세요.'

    response = client.chat(system, user)

    # JSON 파싱 (코드블록 제거)
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    data = json.loads(text)

    # 진행 상태 초기화
    for cat in data["categories"]:
        for topic in cat["topics"]:
            topic["status"] = "pending"
            topic["completed_at"] = None

    data["created_at"] = datetime.now().isoformat()

    # 파일명 생성
    slug = field.lower().replace(" ", "-")
    filepath = ROADMAPS_DIR / f"{slug}.yaml"
    ROADMAPS_DIR.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    click.echo(f"\n📋 로드맵: {data['field']}")
    click.echo(f"   {data['description']}")
    for cat in data["categories"]:
        click.echo(f"\n  [{cat['name']}]")
        for t in cat["topics"]:
            click.echo(f"    - {t['title']} ({t['difficulty']})")

    return str(filepath)


def list_roadmaps() -> list[str]:
    ROADMAPS_DIR.mkdir(parents=True, exist_ok=True)
    return [f.stem for f in ROADMAPS_DIR.glob("*.yaml")]


def show_roadmap(name: str):
    filepath = ROADMAPS_DIR / f"{name}.yaml"
    if not filepath.exists():
        click.echo(f"로드맵을 찾을 수 없습니다: {name}")
        return

    with open(filepath, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    total = 0
    done = 0
    click.echo(f"\n📋 {data['field']}")
    for cat in data["categories"]:
        click.echo(f"\n  [{cat['name']}]")
        for t in cat["topics"]:
            total += 1
            marker = "✅" if t["status"] == "completed" else "⬜"
            if t["status"] == "completed":
                done += 1
            click.echo(f"    {marker} {t['title']} ({t['difficulty']})")

    click.echo(f"\n  진행률: {done}/{total} ({done*100//total if total else 0}%)")


def load_roadmap(name: str) -> dict | None:
    filepath = ROADMAPS_DIR / f"{name}.yaml"
    if not filepath.exists():
        return None
    with open(filepath, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_latest_roadmap() -> tuple[str, dict] | None:
    ROADMAPS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(ROADMAPS_DIR.glob("*.yaml"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        return None
    with open(files[0], encoding="utf-8") as f:
        return files[0].stem, yaml.safe_load(f)


def get_next_pending_topics(data: dict, count: int = 3) -> list[dict]:
    """로드맵에서 다음 pending 주제들 반환"""
    pending = []
    for cat in data["categories"]:
        for topic in cat["topics"]:
            if topic["status"] == "pending":
                pending.append({**topic, "category": cat["name"]})
            if len(pending) >= count:
                return pending
    return pending


def mark_topic_completed(name: str, topic_title: str):
    filepath = ROADMAPS_DIR / f"{name}.yaml"
    with open(filepath, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for cat in data["categories"]:
        for topic in cat["topics"]:
            if topic["title"] == topic_title:
                topic["status"] = "completed"
                topic["completed_at"] = datetime.now().isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
