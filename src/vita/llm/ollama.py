import httpx


class OllamaClient:
    DEFAULT_MODEL = "gemma3:4b"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self,
                 model: str = DEFAULT_MODEL, 
                 base_url: str = DEFAULT_BASE_URL
                 ) -> None:
        self.model = model
        self.base_url = base_url
        self.messages: list[dict[str, str]] = []

    def chat(self, message: str) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": self.messages,
                "stream": False,
            },
            timeout=70.0
        )
        response.raise_for_status()

        data = response.json()
        assistant_message = data["message"]["content"]
        self.messages.append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )

        return assistant_message