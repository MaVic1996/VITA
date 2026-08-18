import typer
from vita.tools.time import get_current_time, GetCurrentTimeArgs
from vita.calendar.google import GoogleCalendarClient
from vita.tools.calendar import (
    CalendarTool,
    CreateEventArgs,
    DeleteEventArgs,
    ListEventsArgs,
    UpdateEventArgs,
)
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
            args_model=GetCurrentTimeArgs
        )
    )

    tools.register_tool(
        Tool(
            name="calendar_list_events",
            description=(
                "List the user's calendar events "
                "between two dates."
            ),
            function=calendar_tool.list_events,
            args_model=ListEventsArgs,
        )
    )

    tools.register_tool(
        Tool(
            name="calendar_create_event",
            description=(
                "Create a new event in the user's "
                "Google Calendar."
            ),
            function=calendar_tool.create_event,
            args_model=CreateEventArgs,
        )
    )

    tools.register_tool(
        Tool(
            name="calendar_update_event",
            description=(
                "Update an existing event in the user's "
                "Google Calendar."
            ),
            function=calendar_tool.update_event,
            args_model=UpdateEventArgs,
        )
    )

    tools.register_tool(
        Tool(
            name="calendar_delete_event",
            description=(
                "Delete an existing event from the user's "
                "Google Calendar."
            ),
            function=calendar_tool.delete_event,
            args_model=DeleteEventArgs,
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
