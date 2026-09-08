import subprocess
from pathlib import Path

from vita.speech.synthesis.synthesizer import SpeechSynthesizer


class PiperSynthesizer(SpeechSynthesizer):
    def __init__(self, executable_path: Path, model_path: Path) -> None:
        self.executable_path = executable_path
        self.model_path = model_path

    def synthesize(self, text: str, output_path: Path) -> None:
        if not text.strip():
            raise ValueError("Text to synthesize cannot be empty.")

        self._validate_paths()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [
                str(self.executable_path),
                "--model",
                str(self.model_path),
                "--output_file",
                str(output_path),
            ],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Piper failed with exit code {result.returncode}: {result.stderr}"
            )

        if not output_path.exists():
            raise RuntimeError("Piper did not create an audio file.")

    def _validate_paths(self) -> None:
        for path, label in (
            (self.executable_path, "Piper executable"),
            (self.model_path, "Piper model"),
        ):
            if not path.exists():
                raise FileNotFoundError(f"{label} not found: {path}")
    
