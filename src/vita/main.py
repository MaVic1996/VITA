import typer
from vita.tools.time import get_current_time
from vita.calendar.google import GoogleCalendarClient
from vita.tools.calendar import CalendarTool
from vita.agent.agent import Agent
from vita.llm.ollama import OllamaClient
from vita.tools.registry import ToolRegistry, Tool

def main() -> None:
    calendar_client = GoogleCalendarClient()
    calendar_tool = CalendarTool(calendar_client)
    tools = ToolRegistry()

    tools.register_tool(
        Tool(
            name="get_current_time",
            description="Get the current local date and time.",
            function=get_current_time,
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )
    )

    tools.register_tool(
        Tool(
            name="calendar_list_events",
            description="List calendar events between two dates.",
            function=calendar_tool.list_events,
            parameters={
                "type": "object",
                "properties": {
                      "start": {
                          "type": "string",
                              "description": "Start of the period in ISO 8601 format.",
                          },
                      "end": {
                          "type": "string",
                          "description": "End of the period in ISO 8601 format.",
                      },
                  },
                "required": ["start", "end"],
            },
        )
    )
    agent = Agent(OllamaClient(), tools)
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
