import typer
from vita.tools.time import get_current_time, GetCurrentTimeArgs
from vita.preferences.sqlite import SQLitePreferencesRepository
from vita.calendar.google import GoogleCalendarClient
from vita.agent.agent import Agent
from vita.llm.ollama import OllamaClient

from vita.tools.factory import ToolFactory

def main() -> None:
    tools = ToolFactory.build_tool_registry(
        calendar_client=GoogleCalendarClient(),
    )

    repository = SQLitePreferencesRepository()
    preferences = repository.load()

    agent = Agent(OllamaClient(), tools, preferences=preferences)


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

if __name__ == "__main__":
    typer.run(main)
