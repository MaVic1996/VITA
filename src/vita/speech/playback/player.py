from pathlib import Path
from typing import Protocol


class AudioPlayer(Protocol):
    def play(self, audio_path: Path) -> None:
        """Plays an audio file."""