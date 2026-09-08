from pathlib import Path
from threading import Event
from typing import Protocol


class AudioRecorder(Protocol):
    def record(self, output_path: Path, duration: float) -> None:
        """Records audio from the microphone as a WAV file."""

    def record_until_stopped(self, output_path: Path, stop_event: Event) -> None:
        """Records audio from the microphone as a WAV file until the stop_event is set."""