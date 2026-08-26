import wave

import numpy as np
import pytest

from vita.speech.sounddevice import SoundDeviceRecorder


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

    monkeypatch.setattr("vita.speech.sounddevice.sd.rec", fake_rec)
    monkeypatch.setattr("vita.speech.sounddevice.sd.wait", fake_wait)

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
