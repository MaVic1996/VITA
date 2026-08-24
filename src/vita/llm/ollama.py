from typing import Any

import httpx


class OllamaClient:
    DEFAULT_MODEL = "gemma4"
    DEFAULT_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL_TIMEOUT = 70.0

    def __init__(self,
                 model: str = DEFAULT_MODEL, 
                 base_url: str = DEFAULT_BASE_URL
                 ) -> None:
        self.model = model
        self.base_url = base_url

    def chat(
        self, 
        messages: list[dict[str,str]],
        tools: list[dict[str, Any]] | None = None
        ) -> dict[str, Any]:

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        if tools is not None:
            payload["tools"] = tools

        response = httpx.post(
            f"{self.base_url}/api/chat",
            json= payload,
            timeout=self.DEFAULT_MODEL_TIMEOUT
        )
        if response.is_error:
            print(response.text)


        response.raise_for_status()

        data = response.json()

        return data["message"]