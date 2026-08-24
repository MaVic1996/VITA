from vita.calendar.google import GoogleCalendarClient
from vita.tools.calendar import (
      CalendarTool,
      CreateEventArgs,
      DeleteEventArgs,
      ListEventsArgs,
      UpdateEventArgs,
)
from vita.tools.preferences import (
      PreferencesRepository,
      PreferencesTool,
      UpdatePreferencesArgs,
)
from vita.tools.registry import Tool, ToolRegistry
from vita.tools.time import GetCurrentTimeArgs, get_current_time


def build_tool_registry(
    calendar_client: GoogleCalendarClient,
    preferences_repository: PreferencesRepository,
) -> ToolRegistry:
      calendar_tool = CalendarTool(calendar_client)
      preferences_tool = PreferencesTool(preferences_repository)
      tools = ToolRegistry()

      tools.register_tool(
          Tool(
              name="preferences_update",
              description=(
                "Update the user's saved preferences, such as their name, timezone, "
                "preferred language, or default calendar event duration."
              ),
              function= preferences_tool.update_preferences,
              args_model=UpdatePreferencesArgs
          )
      )
        
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
              requires_confirmation=True,
              confirmation_message="Voy a actualizar el evento seleccionado.",
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
              requires_confirmation=True,
              confirmation_message="Voy a eliminar el evento seleccionado.",
          )
      )

      return tools