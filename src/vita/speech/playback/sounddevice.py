import wave
from pathlib import Path
from typing import ClassVar

import numpy as np
import sounddevice as sd

from vita.speech.playback.player import AudioPlayer


class SoundDeviceAudioPlayer(AudioPlayer):
    _SAMPLE_WIDTH_TO_DTYPE: ClassVar[dict[int, type[np.generic]]] = {
        1: np.uint8,
        2: np.int16,
        4: np.int32,
    }

    def play(self, audio_path: Path) -> None:
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            with wave.open(str(audio_path), "rb") as audio_file:
                if audio_file.getcomptype() != "NONE":
                    raise ValueError("Compressed WAV files are not supported.")

                sample_width = audio_file.getsampwidth()
                dtype = self._SAMPLE_WIDTH_TO_DTYPE.get(sample_width)
                if dtype is None:
                    raise ValueError(
                        f"Unsupported WAV sample width: {sample_width} bytes."
                    )

                channels = audio_file.getnchannels()
                sample_rate = audio_file.getframerate()
                samples = np.frombuffer(
                    audio_file.readframes(audio_file.getnframes()), dtype=dtype
                )
        except wave.Error as error:
            raise ValueError(f"Invalid WAV audio file: {audio_path}") from error

        if channels > 1:
            samples = samples.reshape(-1, channels)

        sd.play(samples, samplerate=sample_rate)
        sd.wait()
