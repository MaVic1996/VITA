import wave
from threading import Event

import numpy as np
import pytest

from vita.speech.recording.sounddevice import SoundDeviceRecorder


def test_records_mono_16khz_pcm_wav(monkeypatch, tmp_path) -> None:
    recorder = SoundDeviceRecorder()
    output_path = tmp_path / "recordings" / "voice.wav"
    calls: dict[str, object] = {}

    def fake_rec(frames: int, **kwargs) -> np.ndarray:
        calls["frames"] = frames
        calls.update(kwargs)
        return np.zeros((frames, 1), dtype=np.int16)

    def fake_wait() -> None:
        calls["wait_called"] = True

    monkeypatch.setattr("vita.speech.recording.sounddevice.sd.rec", fake_rec)
    monkeypatch.setattr("vita.speech.recording.sounddevice.sd.wait", fake_wait)

    recorder.record(output_path, duration=2)

    assert calls == {
        "frames": 32_000,
        "samplerate": 16_000,
        "channels": 1,
        "dtype": "int16",
        "wait_called": True,
    }

    with wave.open(str(output_path), "rb") as audio_file:
        assert audio_file.getnchannels() == 1
        assert audio_file.getsampwidth() == 2
        assert audio_file.getframerate() == 16_000
        assert audio_file.getnframes() == 32_000


def test_rejects_non_positive_recording_duration(tmp_path) -> None:
    recorder = SoundDeviceRecorder()

    with pytest.raises(ValueError, match="positive"):
        recorder.record(tmp_path / "voice.wav", duration=0)


def test_records_until_stop_event_is_set(monkeypatch, tmp_path) -> None:
    recorder = SoundDeviceRecorder()
    output_path = tmp_path / "voice.wav"
    stop_event = Event()
    calls: dict[str, object] = {}

    class FakeInputStream:
        def __init__(self, **kwargs) -> None:
            calls.update(kwargs)
            self.callback = kwargs["callback"]

        def __enter__(self):
            self.callback(
                np.array([[1], [2], [3]], dtype=np.int16),
                3,
                None,
                None,
            )
            stop_event.set()
            return self

        def __exit__(self, exc_type, exc_value, traceback) -> None:
            return None

    monkeypatch.setattr(
        "vita.speech.recording.sounddevice.sd.InputStream",
        FakeInputStream,
    )

    recorder.record_until_stopped(output_path, stop_event)

    assert calls["samplerate"] == 16_000
    assert calls["channels"] == 1
    assert calls["dtype"] == "int16"

    with wave.open(str(output_path), "rb") as audio_file:
        assert audio_file.getnframes() == 3


def test_records_until_silence_is_detected(monkeypatch, tmp_path) -> None:
    recorder = SoundDeviceRecorder()
    output_path = tmp_path / "voice.wav"
    calls: dict[str, object] = {}

    class FakeInputStream:
        def __init__(self, **kwargs) -> None:
            calls.update(kwargs)
            self.callback = kwargs["callback"]

        def __enter__(self):
            self.callback(
                np.full((10, 1), 1_000, dtype=np.int16),
                10,
                None,
                None,
            )
            self.callback(
                np.zeros((16, 1), dtype=np.int16),
                16,
                None,
                None,
            )
            return self

        def __exit__(self, exc_type, exc_value, traceback) -> None:
            return None

    monkeypatch.setattr(
        "vita.speech.recording.sounddevice.sd.InputStream",
        FakeInputStream,
    )

    recorder.record_until_silence(
        output_path,
        silence_duration=0.001,
        max_duration=1,
        rms_threshold=500,
    )

    assert calls["samplerate"] == 16_000
    assert calls["channels"] == 1
    assert calls["dtype"] == "int16"

    with wave.open(str(output_path), "rb") as audio_file:
        assert audio_file.getnframes() == 26
