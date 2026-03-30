# 티스토리 블로그 자동화

AI 기반 개발 공부 + 블로그 글 작성 자동화 도구.
옵시디언에서 마크다운으로 관리하고, 티스토리에는 완성된 HTML을 복사-붙여넣기만 하면 됩니다.

## 워크플로우

```
분야 지정 → AI 로드맵 생성 → 주제/제목 추천 → AI 글 작성 → HTML 변환 → 티스토리 붙여넣기
```

## 설치

```bash
pip install -r requirements.txt
```

## 설정

### 1. API 키 (.env)

`.env.example`을 복사하여 `.env`를 만들고 API 키를 입력합니다.

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

### 2. config.yaml

```yaml
ai:
  provider: claude  # claude 또는 openai

obsidian:
  vault_path: /path/to/your/vault  # 옵시디언 볼트 경로
  blog_folder: Blog                 # 볼트 내 블로그 글 폴더

github:
  repo: username/blog-images  # 이미지 호스팅용 GitHub 저장소
```

## 사용법

### 로드맵 생성

분야를 지정하면 AI가 체계적인 학습 로드맵을 만들어줍니다.

```bash
python cli.py roadmap create "Python 백엔드"
```

로드맵 조회:

```bash
python cli.py roadmap list
python cli.py roadmap show python-백엔드
```

### 주제 추천

로드맵 기반으로 다음 공부할 주제와 블로그 제목을 추천받습니다.

```bash
python cli.py topic next
python cli.py topic next -r python-백엔드 -n 5  # 로드맵 지정, 5개 추천
```

### 글 작성

AI가 블로그 글을 마크다운으로 작성합니다. 작성된 글은 `posts/`와 옵시디언 볼트 양쪽에 저장됩니다.

```bash
python cli.py write -t "FastAPI 입문" -s tutorial
python cli.py write -t "Python 데코레이터" -s til
```

스타일 옵션:
- `tutorial` - 초보자 대상 단계별 튜토리얼 (기본값)
- `til` - Today I Learned, 핵심만 간결하게

### HTML 변환

마크다운을 티스토리 호환 HTML로 변환하고 클립보드에 복사합니다.

```bash
python cli.py convert posts/2026-03-30-fastapi-입문.md
```

변환 후:
1. 클립보드에 HTML이 복사됨
2. `output/` 폴더에 미리보기 HTML 생성
3. 티스토리 글쓰기 → **HTML 모드** → 붙여넣기

### 한번에 실행

주제 선택 → 글 작성 → HTML 변환을 한번에 처리합니다.

```bash
python cli.py auto
python cli.py auto -s til -r python-백엔드
```

## 프로젝트 구조

```
blog/
├── cli.py              # CLI 진입점
├── config.yaml         # 설정
├── lib/
│   ├── ai_client.py    # Claude/OpenAI 통합 클라이언트
│   ├── roadmap.py      # 학습 로드맵 관리
│   ├── topic_recommender.py  # 주제/제목 추천
│   ├── post_writer.py  # AI 글 작성 + 옵시디언 저장
│   ├── markdown_to_html.py   # HTML 변환
│   ├── code_highlight.py     # Pygments 코드 하이라이팅
│   ├── image_handler.py      # 이미지 GitHub 업로드
│   └── clipboard.py   # 클립보드 복사
├── roadmaps/           # 학습 로드맵 (YAML)
├── posts/              # 생성된 마크다운 글
└── output/             # 변환된 HTML 미리보기
```
