from pathlib import Path
from threading import Event
from typing import Protocol


class AudioRecorder(Protocol):
    def record(self, output_path: Path, duration: float) -> None:
        """Records audio from the microphone as a WAV file."""

    def record_until_stopped(self, output_path: Path, stop_event: Event) -> None:
        """Records audio from the microphone as a WAV file until the stop_event is set."""

    def record_until_silence(
        self,
        output_path: Path,
        *,
        silence_duration: float = 2.5,
        max_duration: float = 20.0,
        rms_threshold: float = 500.0,
    ) -> None:
        """Records speech until silence is detected."""