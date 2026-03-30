"""이미지 감지 + GitHub 업로드 + URL 치환"""

import re
import os
from pathlib import Path

import git


def process_images(html: str, md_path: str, config: dict) -> str:
    """HTML 내 로컬 이미지를 GitHub raw URL로 치환"""
    github_cfg = config.get("github", {})
    repo_url = github_cfg.get("repo", "")
    branch = github_cfg.get("branch", "main")
    image_dir = github_cfg.get("image_dir", "images")

    if not repo_url:
        return html  # GitHub 설정이 없으면 그대로 반환

    md_dir = Path(md_path).parent
    images_found = re.findall(r'<img[^>]+src="([^"]+)"', html)

    for img_src in images_found:
        if img_src.startswith(("http://", "https://")):
            continue  # 이미 외부 URL

        local_path = md_dir / img_src
        if not local_path.exists():
            continue

        # GitHub에 업로드
        remote_path = upload_to_github(local_path, repo_url, branch, image_dir)
        if remote_path:
            raw_url = f"https://raw.githubusercontent.com/{repo_url}/{branch}/{remote_path}"
            html = html.replace(f'src="{img_src}"', f'src="{raw_url}"')

    return html


def upload_to_github(local_path: Path, repo_url: str, branch: str, image_dir: str) -> str | None:
    """이미지를 GitHub repo에 push하고 경로 반환"""
    # repo가 로컬에 clone되어 있다고 가정
    repo_local = Path.home() / ".blog-images"

    try:
        if repo_local.exists():
            repo = git.Repo(repo_local)
            repo.remotes.origin.pull()
        else:
            repo = git.Repo.clone_from(
                f"https://github.com/{repo_url}.git",
                repo_local,
            )

        # 이미지 복사
        dest_dir = repo_local / image_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / local_path.name

        import shutil
        shutil.copy2(local_path, dest)

        # commit & push
        repo.index.add([str(dest.relative_to(repo_local))])
        repo.index.commit(f"Add image: {local_path.name}")
        repo.remotes.origin.push()

        return f"{image_dir}/{local_path.name}"
    except Exception as e:
        print(f"이미지 업로드 실패: {e}")
        return None
