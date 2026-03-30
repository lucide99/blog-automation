#!/usr/bin/env python3
"""티스토리 블로그 자동화 CLI"""

import click
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@click.group()
@click.pass_context
def cli(ctx):
    """AI 기반 개발 블로그 자동화 도구"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config()


# --- roadmap commands ---
@cli.group()
def roadmap():
    """학습 로드맵 관리"""
    pass


@roadmap.command("create")
@click.argument("field")
@click.pass_context
def roadmap_create(ctx, field):
    """분야를 지정하여 학습 로드맵 생성"""
    from lib.roadmap import create_roadmap

    config = ctx.obj["config"]
    result = create_roadmap(config, field)
    click.echo(f"로드맵 생성 완료: {result}")


@roadmap.command("list")
def roadmap_list():
    """저장된 로드맵 목록 조회"""
    from lib.roadmap import list_roadmaps

    for rm in list_roadmaps():
        click.echo(f"  - {rm}")


@roadmap.command("show")
@click.argument("name")
def roadmap_show(name):
    """로드맵 상세 조회"""
    from lib.roadmap import show_roadmap

    show_roadmap(name)


# --- topic commands ---
@cli.group()
def topic():
    """주제 추천"""
    pass


@topic.command("next")
@click.option("--roadmap", "-r", default=None, help="로드맵 이름")
@click.option("--count", "-n", default=3, help="추천 개수")
@click.pass_context
def topic_next(ctx, roadmap, count):
    """다음 공부할 주제 및 블로그 제목 추천"""
    from lib.topic_recommender import recommend_next

    config = ctx.obj["config"]
    recommend_next(config, roadmap_name=roadmap, count=count)


# --- write commands ---
@cli.command("write")
@click.option("--topic", "-t", required=True, help="글 주제")
@click.option("--style", "-s", default=None, help="글 스타일 (tutorial/til)")
@click.pass_context
def write(ctx, topic, style):
    """AI가 블로그 글 작성"""
    from lib.post_writer import write_post

    config = ctx.obj["config"]
    style = style or config["post"]["default_style"]
    result = write_post(config, topic, style)
    click.echo(f"글 작성 완료: {result}")


# --- convert commands ---
@cli.command("convert")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--no-copy", is_flag=True, help="클립보드 복사 안 함")
@click.pass_context
def convert(ctx, filepath, no_copy):
    """마크다운 파일을 티스토리 HTML로 변환"""
    from lib.markdown_to_html import convert_to_html
    from lib.clipboard import copy_to_clipboard

    config = ctx.obj["config"]
    html, output_path = convert_to_html(config, filepath)

    if not no_copy:
        copy_to_clipboard(html)
        click.echo("클립보드에 HTML이 복사되었습니다!")

    click.echo(f"미리보기: {output_path}")


# --- auto command ---
@cli.command("auto")
@click.option("--roadmap", "-r", default=None, help="로드맵 이름")
@click.option("--style", "-s", default=None, help="글 스타일")
@click.pass_context
def auto(ctx, roadmap, style):
    """주제 선택 → 글 작성 → HTML 변환을 한번에 실행"""
    from lib.topic_recommender import recommend_next, pick_topic
    from lib.post_writer import write_post
    from lib.markdown_to_html import convert_to_html
    from lib.clipboard import copy_to_clipboard

    config = ctx.obj["config"]
    style = style or config["post"]["default_style"]

    # 1. 주제 추천 및 선택
    topics = recommend_next(config, roadmap_name=roadmap, count=3, return_list=True)
    selected = pick_topic(topics)
    click.echo(f"\n선택된 주제: {selected['title']}")

    # 2. 글 작성
    md_path = write_post(config, selected["title"], style, metadata=selected)
    click.echo(f"글 작성 완료: {md_path}")

    # 3. HTML 변환
    html, output_path = convert_to_html(config, md_path)
    copy_to_clipboard(html)
    click.echo(f"클립보드에 HTML 복사 완료!")
    click.echo(f"미리보기: {output_path}")


if __name__ == "__main__":
    cli()
