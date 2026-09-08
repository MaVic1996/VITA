import wave

import numpy as np
import pytest

from vita.speech.playback.sounddevice import SoundDeviceAudioPlayer


def test_plays_pcm_wav(monkeypatch, tmp_path) -> None:
    audio_path = tmp_path / "response.wav"
    samples = np.array([0, 1_000, -1_000], dtype=np.int16)

    with wave.open(str(audio_path), "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(22_050)
        audio_file.writeframes(samples.tobytes())

    calls: dict[str, object] = {}

    def fake_play(audio: np.ndarray, samplerate: int) -> None:
        calls["audio"] = audio
        calls["samplerate"] = samplerate

    def fake_wait() -> None:
        calls["wait_called"] = True

    monkeypatch.setattr("vita.speech.playback.sounddevice.sd.play", fake_play)
    monkeypatch.setattr("vita.speech.playback.sounddevice.sd.wait", fake_wait)

    SoundDeviceAudioPlayer().play(audio_path)

    assert np.array_equal(calls["audio"], samples)
    assert calls["samplerate"] == 22_050
    assert calls["wait_called"] is True


def test_rejects_missing_audio_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        SoundDeviceAudioPlayer().play(tmp_path / "missing.wav")
