import typer

from vita.agent.agent import Agent
from vita.calendar.google import GoogleCalendarClient
from vita.llm.ollama import OllamaClient
from vita.memory.sqlite import SQLitePreferencesRepository
from vita.tools.factory import build_tool_registry


def main() -> None:
    preferences_repository = SQLitePreferencesRepository()
    tools = build_tool_registry(
        calendar_client=GoogleCalendarClient(),
        preferences_repository=preferences_repository,
    )

    agent = Agent(OllamaClient(), tools, preferences_repository=preferences_repository)


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
