---
title: "Python FastAPI 입문"
date: 2026-03-30
category: "Python 백엔드"
tags: [FastAPI, Python, REST API]
style: tutorial
---

# Python FastAPI 입문 - 첫 API 서버 만들기

FastAPI는 Python으로 API를 빠르게 만들 수 있는 웹 프레임워크입니다.

## 설치

```bash
pip install fastapi uvicorn
```

## 첫 번째 API 만들기

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

## 서버 실행

```bash
uvicorn main:app --reload
```

실행하면 `http://127.0.0.1:8000`에서 API가 동작합니다.

## 자동 문서화

FastAPI는 자동으로 API 문서를 생성합니다:

| 경로 | 설명 |
|------|------|
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |

> FastAPI의 가장 큰 장점은 타입 힌트만으로 자동 검증과 문서화가 된다는 점입니다.

## 마무리

이번 글에서는 FastAPI의 기본적인 사용법을 알아보았습니다. 다음에는 데이터베이스 연동을 다뤄보겠습니다.
