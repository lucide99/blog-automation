"""Claude / OpenAI 통합 AI 클라이언트"""

import os


def get_client(config: dict):
    provider = config["ai"]["provider"]
    if provider == "claude":
        return ClaudeClient(config["ai"]["claude"])
    elif provider == "openai":
        return OpenAIClient(config["ai"]["openai"])
    else:
        raise ValueError(f"지원하지 않는 AI provider: {provider}")


class ClaudeClient:
    def __init__(self, cfg: dict):
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = cfg.get("model", "claude-sonnet-4-6")

    def chat(self, system: str, user: str, max_tokens: int = 8192) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text


class OpenAIClient:
    def __init__(self, cfg: dict):
        from openai import OpenAI

        self.client = OpenAI()
        self.model = cfg.get("model", "gpt-4o")

    def chat(self, system: str, user: str, max_tokens: int = 8192) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content
