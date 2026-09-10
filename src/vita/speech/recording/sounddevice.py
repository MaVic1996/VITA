import time
import wave
from pathlib import Path
from threading import Event

import numpy as np
import sounddevice as sd

from vita.speech.recording.recorder import AudioRecorder


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

        self._write_wav(output_path, recording)

    def record_until_stopped(self, output_path: Path, stop_event: "Event") -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        chunks: list[np.ndarray] = []
        errors: list[str] = []

        def callback(indata, frames, time, status)-> None:
            if status:
                errors.append(str(status))
            chunks.append(indata.copy())

        with sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype="int16",
            callback=callback,
        ):
            while not stop_event.wait(timeout=0.5):
                pass

        if errors:
            raise RuntimeError(f"Errors occurred during recording: {', '.join(errors)}")

        if not chunks:
            raise RuntimeError("No audio data was recorded.")

        recording = np.concatenate(chunks)
        self._write_wav(output_path, recording)

    def record_until_silence(
        self,
        output_path: Path,
        *,
        silence_duration: float = 1.2,
        max_duration: float = 20.0,
        rms_threshold: float = 500.0,
    ) -> None:
        if silence_duration <= 0 or max_duration <= 0 or rms_threshold <= 0:
            raise ValueError(
                "Silence duration, maximum duration and threshold must be positive."
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        chunks: list[np.ndarray] = []
        errors: list[str] = []
        speech_started = Event()
        finished = Event()
        silence_frames = 0
        minimum_silence_frames = max(1, int(silence_duration * self.SAMPLE_RATE))

        def callback(indata, frames, time_info, status) -> None:
            nonlocal silence_frames

            if status:
                errors.append(str(status))

            rms = np.sqrt(np.mean(indata.astype(np.float32) ** 2))

            if rms >= rms_threshold:
                speech_started.set()
                silence_frames = 0
            elif speech_started.is_set():
                silence_frames += frames

            if speech_started.is_set():
                chunks.append(indata.copy())

                if silence_frames >= minimum_silence_frames:
                    finished.set()

        started_at = time.monotonic()

        with sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype="int16",
            callback=callback,
        ):
            while not finished.wait(timeout=0.1):
                if time.monotonic() - started_at >= max_duration:
                    break

        if errors:
            raise RuntimeError(f"Errors occurred during recording: {', '.join(errors)}")

        if not speech_started.is_set():
            raise RuntimeError("No speech was detected during the recording.")

        self._write_wav(output_path, np.concatenate(chunks))

    def _write_wav(self, output_path: Path, recording: np.ndarray) -> None:
        with wave.open(str(output_path), "wb") as audio_file:
            audio_file.setnchannels(self.CHANNELS)
            audio_file.setsampwidth(self.SAMPLE_WIDTH_BYTES)
            audio_file.setframerate(self.SAMPLE_RATE)
            audio_file.writeframes(recording.tobytes())
