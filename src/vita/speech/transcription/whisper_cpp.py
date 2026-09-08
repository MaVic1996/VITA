import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from vita.speech.transcription.transcriber import Transcriber


class WhisperCppTranscriber(Transcriber):
    def __init__(self, executable_path: Path, model_path: Path, language: str = "es") -> None:
        self.executable_path = executable_path
        self.model_path = model_path
        self.language = language

    def transcribe(self, audio_path: Path) -> str:
        self._validate_paths(audio_path)

        with TemporaryDirectory() as temp_dir:
            output_prefix = Path(temp_dir) / "transcription"
            result = subprocess.run(
                [
                    str(self.executable_path),
                    "-m",
                    str(self.model_path),
                    "-f",
                    str(audio_path),
                    "-l",
                    self.language,
                    "-otxt",
                    "-of",
                    str(output_prefix),
                    "-np",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Whisper.cpp failed with exit code {result.returncode}: {result.stderr}"
                )

            transcription_path = output_prefix.with_suffix(".txt")
            if not transcription_path.exists():
                raise RuntimeError("Whisper.cpp did not create a transcription file.")


            transcription = transcription_path.read_text().strip()

        if not transcription:
            raise RuntimeError("No speech was detected in the audio.")

        return transcription

            

    def _validate_paths(self, audio_path: Path) -> None:
        for path, label in (
            (self.executable_path, "whisper.cpp executable"),
            (self.model_path, "Whisper model"),
            (audio_path, "Audio file"),
        ):
            if not path.exists():
                raise FileNotFoundError(f"{label} not found: {path}")
