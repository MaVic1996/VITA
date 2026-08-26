from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

import typer

from vita.agent.agent import Agent
from vita.calendar.google import GoogleCalendarClient
from vita.llm.ollama import OllamaClient
from vita.memory.sqlite import SQLitePreferencesRepository
from vita.speech.factory import build_whisper_cpp_transcriber
from vita.speech.sounddevice import SoundDeviceRecorder
from vita.tools.factory import build_tool_registry


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
) -> None:
    preferences_repository = SQLitePreferencesRepository()
    tools = build_tool_registry(
        calendar_client=GoogleCalendarClient(),
        preferences_repository=preferences_repository,
    )

    agent = Agent(OllamaClient(), tools, preferences_repository=preferences_repository)
    if audio is not None and record is not None:
        raise typer.BadParameter("Use either --audio or --record, not both.")
    
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

        if message.lower() in ("salir", "adios", "quit", "exit"):
            typer.echo("Hasta luego.")
            break

        if not message.strip():
            continue

        response = agent.chat(message)
        typer.echo(f"\n{response}\n")


def _respond_to_audio(agent: Agent, audio_path: Path) -> None:
    try:
        transcriber = build_whisper_cpp_transcriber()
        transcription = transcriber.transcribe(audio_path)
    except (ValueError, FileNotFoundError, RuntimeError) as error:
        typer.echo(f"Error al transcribir el audio: {error}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"\nHas dicho: {transcription}\n")

    response = agent.chat(transcription)
    typer.echo(f"\n{response}\n")


def cli() -> None:
    typer.run(main)

if __name__ == "__main__":
    cli()
