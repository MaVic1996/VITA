import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

import typer
from dotenv import load_dotenv

from vita.agent.agent import Agent
from vita.calendar.google import GoogleCalendarClient
from vita.calendar.briefing import DailyBriefingService
from vita.llm.ollama import OllamaClient
from vita.memory.sqlite import SQLitePreferencesRepository
from vita.speech.factory import build_piper_synthesizer, build_whisper_cpp_transcriber
from vita.speech.playback.sounddevice import SoundDeviceAudioPlayer
from vita.speech.recording.sounddevice import SoundDeviceRecorder
from vita.tools.factory import build_tool_registry
from vita.voice.session import VoiceSession

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
    )] = False
) -> None:
    preferences_repository = SQLitePreferencesRepository()
    calendar_client = GoogleCalendarClient()
    tools = build_tool_registry(
        calendar_client=calendar_client,
        preferences_repository=preferences_repository,
    )
    ollama_client = OllamaClient(
        model=os.environ.get("VITA_OLLAMA_MODEL", OllamaClient.DEFAULT_MODEL),
        base_url=os.environ.get("VITA_OLLAMA_BASE_URL", OllamaClient.DEFAULT_BASE_URL),
    )

    agent = Agent(ollama_client, tools, preferences_repository=preferences_repository)

    if sum(value is not None for value in (audio, record)) + voice  > 1:
        raise typer.BadParameter("Use only one of --audio, --record, or --voice")


    service = DailyBriefingService(
        calendar_client=calendar_client,
        preferences_repository=preferences_repository,
    )
    briefing_text = service.build()
    if voice:
        try:
            return VoiceSession(
                agent,
                recorder=SoundDeviceRecorder(),
                transcriber=build_whisper_cpp_transcriber(),
                synthesizer=build_piper_synthesizer(),
                player=SoundDeviceAudioPlayer(),
                welcome_message=briefing_text,
            ).run()
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

    typer.echo("Bienvenido a tu asistente V.I.T.A.")
    typer.echo(briefing_text)
    typer.echo(" ¿En qué puedo ayudarte hoy?")

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
