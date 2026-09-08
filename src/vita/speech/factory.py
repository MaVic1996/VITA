import os
from pathlib import Path

from vita.speech.synthesis.piper import PiperSynthesizer
from vita.speech.transcription.whisper_cpp import WhisperCppTranscriber


def build_whisper_cpp_transcriber() -> WhisperCppTranscriber:
    executable = os.environ.get("VITA_WHISPER_EXECUTABLE")
    model = os.environ.get("VITA_WHISPER_MODEL")

    if not executable or not model:
        raise ValueError(
            "VITA_WHISPER_EXECUTABLE and VITA_WHISPER_MODEL environment variables must be set before using --audio"
        )

    return WhisperCppTranscriber(
        executable_path=Path(executable),
        model_path=Path(model),
    )


def build_piper_synthesizer() -> PiperSynthesizer:
    executable = os.environ.get("VITA_PIPER_EXECUTABLE")
    model = os.environ.get("VITA_PIPER_MODEL")

    if not executable or not model:
        raise ValueError(
            "VITA_PIPER_EXECUTABLE and VITA_PIPER_MODEL environment variables must be set before using --voice"
        )

    return PiperSynthesizer(
        executable_path=Path(executable),
        model_path=Path(model),
    )