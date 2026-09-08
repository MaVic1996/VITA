from pathlib import Path
from subprocess import CompletedProcess

import pytest

from vita.speech.transcription.whisper_cpp import WhisperCppTranscriber


def build_transcriber(tmp_path) -> tuple[WhisperCppTranscriber, Path]:
    executable = tmp_path / "whisper-cli"
    model = tmp_path / "ggml-small.bin"
    audio = tmp_path / "audio.wav"

    executable.touch()
    model.touch()
    audio.touch()

    return (
        WhisperCppTranscriber(
            executable_path=executable,
            model_path=model,
        ),
        audio,
    )


def test_transcribes_audio_file(monkeypatch, tmp_path) -> None:
    transcriber, audio = build_transcriber(tmp_path)

    def fake_run(command: list[str], **kwargs) -> CompletedProcess:
        output_prefix = Path(command[command.index("-of") + 1])
        output_prefix.with_suffix(".txt").write_text(
            "Apunta una reunión mañana a las diez con Álvaro."
        )
        return CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(
        "vita.speech.transcription.whisper_cpp.subprocess.run", fake_run
    )

    assert transcriber.transcribe(audio) == (
        "Apunta una reunión mañana a las diez con Álvaro."
    )


def test_raises_when_whisper_cpp_fails(monkeypatch, tmp_path) -> None:
    transcriber, audio = build_transcriber(tmp_path)

    def fake_run(command: list[str], **kwargs) -> CompletedProcess:
        return CompletedProcess(command, 1, "", "Unable to decode audio")

    monkeypatch.setattr(
        "vita.speech.transcription.whisper_cpp.subprocess.run", fake_run
    )

    with pytest.raises(RuntimeError, match="Unable to decode audio"):
        transcriber.transcribe(audio)
