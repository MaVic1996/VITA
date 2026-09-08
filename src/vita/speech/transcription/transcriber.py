from pathlib import Path
from typing import Protocol


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> str:
        """Transcribe an audio file into text."""