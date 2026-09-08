import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread
from typing import Annotated

import typer
from dotenv import load_dotenv

from vita.agent.agent import Agent
from vita.calendar.google import GoogleCalendarClient
from vita.llm.ollama import OllamaClient
from vita.memory.sqlite import SQLitePreferencesRepository
from vita.speech.factory import build_piper_synthesizer, build_whisper_cpp_transcriber
from vita.speech.playback.player import AudioPlayer
from vita.speech.playback.sounddevice import SoundDeviceAudioPlayer
from vita.speech.recording.sounddevice import SoundDeviceRecorder
from vita.speech.synthesis.synthesizer import SpeechSynthesizer
from vita.tools.factory import build_tool_registry

END_INTERACTION_COMMANDS = {"salir", "adios", "quit", "exit"}

def main(
    audio: Annotated[Path | None, typer.Option(
        "--audio",
        exists=True,
        readable=True,
        help="Path to an audio file to transcribe and send to V.I.T.A.",
    )] = None,
    record: Annotated[float | None, typer.Option(
        "--record",
        min=1.0,
        help="Record audio from the microphone for a specified duration (in seconds) and send it to V.I.T.A.",
    )] = None,
    voice: Annotated[bool, typer.Option(
        "--voice",
        help="Start an interactive voice session.",
    )] = False,
) -> None:
    preferences_repository = SQLitePreferencesRepository()
    tools = build_tool_registry(
        calendar_client=GoogleCalendarClient(),
        preferences_repository=preferences_repository,
    )
    ollama_client = OllamaClient(
        model=os.environ.get("VITA_OLLAMA_MODEL", OllamaClient.DEFAULT_MODEL),
        base_url=os.environ.get("VITA_OLLAMA_BASE_URL", OllamaClient.DEFAULT_BASE_URL),
    )

    agent = Agent(ollama_client, tools, preferences_repository=preferences_repository)

    if sum(value is not None for value in (audio, record)) + voice > 1:
        raise typer.BadParameter("Use only one of --audio, --record, or --voice.")

    if voice:
        try:
            return _run_voice_session(
                agent,
                synthesizer=build_piper_synthesizer(),
                player=SoundDeviceAudioPlayer(),
            )
        except (ValueError, FileNotFoundError) as error:
            typer.echo(f"Error al iniciar el modo voz: {error}", err=True)
            raise typer.Exit(code=1)
    if audio is not None:
        return _respond_to_audio(agent, audio)

    if record is not None:
        try:
            typer.echo(f"Grabando durante {record} segundos...")

            with TemporaryDirectory() as temp_dir:
                recorded_audio_path = Path(temp_dir) / "recorded_audio.wav"
                SoundDeviceRecorder().record(
                    recorded_audio_path, 
                    duration=record,
                )
                _respond_to_audio(agent, recorded_audio_path)
        except (ValueError, FileNotFoundError, RuntimeError) as error:
            typer.echo(f"Error al grabar el audio: {error}", err=True)
            raise typer.Exit(code=1)

        return

    typer.echo("Bienvenido a tu asistente V.I.T.A. ¿En qué puedo ayudarte hoy?")

    while True:
        try: 
            message = typer.prompt("V.I.T.A.")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nHasta luego.")
            break

        if message.lower() in END_INTERACTION_COMMANDS:
            typer.echo("Hasta luego.")
            break

        if not message.strip():
            continue

        response = agent.chat(message)
        typer.echo(f"\n{response}\n")

def _run_voice_session(
        agent: Agent, 
        synthesizer: SpeechSynthesizer, 
        player: AudioPlayer
    ) -> None:
    recorder = SoundDeviceRecorder()
    typer.echo("Iniciando sesión de voz.")

    while True:
        try:
            command = input("\nPulsa Enter para hablar o escribe 'salir' para terminar la sesión de voz: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nHasta luego.")
            break

        if command in END_INTERACTION_COMMANDS:
            typer.echo("Hasta luego.")
            break

        with TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "recorded_audio.wav"
            stop_event = Event()
            recording_errors: list[Exception] = []

            def record_audio(
                current_audio_path: Path = audio_path,
                current_stop_event: Event = stop_event,
                errors: list[Exception] = recording_errors,
            ) -> None:
                try:
                    recorder.record_until_stopped(current_audio_path, current_stop_event)
                except Exception as error:  # noqa: BLE001
                    errors.append(error)

            recording_thread = Thread(target=record_audio)
            recording_thread.start()

            try:
                input("Grabando... Pulsa Enter para detener la grabación.")
            except (KeyboardInterrupt, EOFError):
                typer.echo("\nGrabación interrumpida.")
                stop_event.set()
                recording_thread.join()
                continue

            stop_event.set()
            recording_thread.join()

            if recording_errors:
                typer.echo(f"Error al grabar el audio: {recording_errors[0]}", err=True)
                continue

            try:
                response = _respond_to_audio(agent, audio_path)
                response_audio_path = Path(temp_dir) / "response.wav"
                synthesizer.synthesize(response, response_audio_path)
                player.play(response_audio_path)
            except (ValueError, FileNotFoundError, RuntimeError) as error:
                typer.echo(f"Error al procesar el audio: {error}", err=True)
                continue

def _respond_to_audio(agent: Agent, audio_path: Path) -> str:
    try:
        transcriber = build_whisper_cpp_transcriber()
        transcription = transcriber.transcribe(audio_path)
    except (ValueError, FileNotFoundError, RuntimeError) as error:
        typer.echo(f"Error al transcribir el audio: {error}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"\nHas dicho: {transcription}\n")

    response = agent.chat(transcription)
    typer.echo(f"\n{response}\n")
    return response


def cli() -> None:
    load_dotenv()
    typer.run(main)

if __name__ == "__main__":
    cli()
