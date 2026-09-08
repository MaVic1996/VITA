from pathlib import Path
from subprocess import CompletedProcess

import pytest

from vita.speech.synthesis.piper import PiperSynthesizer


def build_synthesizer(tmp_path) -> tuple[PiperSynthesizer, Path]:
    executable = tmp_path / "piper"
    model = tmp_path / "voice.onnx"
    executable.touch()
    model.touch()

    return PiperSynthesizer(executable_path=executable, model_path=model), executable


def test_synthesizes_text_to_wav(monkeypatch, tmp_path) -> None:
    synthesizer, executable = build_synthesizer(tmp_path)
    output_path = tmp_path / "audio" / "response.wav"
    calls: dict[str, object] = {}

    def fake_run(command: list[str], **kwargs) -> CompletedProcess:
        calls["command"] = command
        calls.update(kwargs)
        Path(command[command.index("--output_file") + 1]).touch()
        return CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("vita.speech.synthesis.piper.subprocess.run", fake_run)

    synthesizer.synthesize("Hola, Víctor.", output_path)

    assert calls == {
        "command": [
            str(executable),
            "--model",
            str(tmp_path / "voice.onnx"),
            "--output_file",
            str(output_path),
        ],
        "input": "Hola, Víctor.",
        "capture_output": True,
        "text": True,
        "check": False,
    }
    assert output_path.exists()


def test_rejects_empty_text(tmp_path) -> None:
    synthesizer, _ = build_synthesizer(tmp_path)

    with pytest.raises(ValueError, match="cannot be empty"):
        synthesizer.synthesize("  ", tmp_path / "response.wav")
