from pathlib import Path
from typing import Protocol


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str, output_path: Path) -> None:
        """Synthesizes text into audio file."""