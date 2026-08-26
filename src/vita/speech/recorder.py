from pathlib import Path
from typing import Protocol


class AudioRecorder(Protocol):
    def record(self, output_path: Path, duration: float) -> None:
        """Records audio from the microphone as a WAV file."""