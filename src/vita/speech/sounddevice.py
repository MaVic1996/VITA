import wave
from pathlib import Path

import sounddevice as sd

from vita.speech.recorder import AudioRecorder


class SoundDeviceRecorder(AudioRecorder):
    SAMPLE_RATE = 16_000
    CHANNELS = 1
    SAMPLE_WIDTH_BYTES = 2

    def record(self, output_path: Path, duration: float) -> None:
        if duration <= 0:
            raise ValueError("Duration must be a positive number.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        frames = int(duration * self.SAMPLE_RATE)
        recording = sd.rec(
            frames,
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype="int16",
        )
        sd.wait()

        with wave.open(str(output_path), "wb") as audio_file:
            audio_file.setnchannels(self.CHANNELS)
            audio_file.setsampwidth(self.SAMPLE_WIDTH_BYTES)
            audio_file.setframerate(self.SAMPLE_RATE)
            audio_file.writeframes(recording.tobytes())