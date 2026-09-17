from pathlib import Path
from tempfile import TemporaryDirectory

import typer

from vita.agent.agent import Agent
from vita.speech.playback.player import AudioPlayer
from vita.speech.recording.recorder import AudioRecorder
from vita.speech.synthesis.synthesizer import SpeechSynthesizer
from vita.speech.transcription.transcriber import Transcriber

END_INTERACTION_COMMANDS = {"salir", "adios", "quit", "exit"}


class VoiceSession:
    def __init__(
        self,
        agent: Agent,
        recorder: AudioRecorder,
        transcriber: Transcriber,
        synthesizer: SpeechSynthesizer,
        player: AudioPlayer,
        welcome_message: str,
    ) -> None:
        self.agent = agent
        self.recorder = recorder
        self.transcriber = transcriber
        self.synthesizer = synthesizer
        self.player = player
        self.welcome_message = welcome_message

    def run(self) -> None:
        typer.echo("Iniciando sesión de voz.")
        typer.echo(self.welcome_message)
        self._speak(self.welcome_message)
        while True:
            try:
                command = input(
                    "\nPulsa Enter para hablar o escribe 'salir' para terminar "
                    "la sesión de voz: "
                ).strip().lower()
            except (KeyboardInterrupt, EOFError):
                typer.echo("\nHasta luego.")
                return

            if command in END_INTERACTION_COMMANDS:
                typer.echo("Hasta luego.")
                return

            self._handle_turn()

    def _handle_turn(self) -> None:
        with TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "recorded_audio.wav"

            try:
                typer.echo("Escuchando... habla ahora.")
                self.recorder.record_until_silence(audio_path)

                transcription = self.transcriber.transcribe(audio_path)
                typer.echo(f"\nHas dicho: {transcription}\n")

                response = self.agent.chat(transcription)
                typer.echo(f"\n{response}\n")

                self._speak(response)
            except (ValueError, FileNotFoundError, RuntimeError) as error:
                typer.echo(f"Error al procesar el audio: {error}", err=True)
            except KeyboardInterrupt:
                typer.echo("\nGrabación interrumpida.")

    def _speak(self, message: str) -> None:
        with TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "message.wav"
            self.synthesizer.synthesize(message, audio_path)
            self.player.play(audio_path)
