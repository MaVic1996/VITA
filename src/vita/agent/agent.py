from vita.agent.system_prompt import build_system_prompt
from vita.dates.resolver import RelativeDateResolver
from vita.llm.ollama import OllamaClient
from vita.memory.repository import PreferencesRepository
from vita.tools.registry import ToolRegistry


class Agent:

    def __init__(self, llm_client: OllamaClient, tools: ToolRegistry, preferences_repository: PreferencesRepository) -> None:
        self.llm_client = llm_client
        self.tools = tools
        self.preferences_repository = preferences_repository
        self.messages = [{"role": "system", "content": ""}]
        self._refresh_preferences()

    def chat(self, user_message: str) -> str:
        self._refresh_preferences()
        
        date_context = self.date_resolver.context_for(user_message)
        if date_context:
            user_message = f"{user_message}\n\n{date_context}"

        self.messages.append({"role": "user", "content": user_message})

        while True:
            response = self.llm_client.chat(self.messages, tools=self._tool_definitions())

            tool_calls = response.get("tool_calls", [])
            if not tool_calls:
                content = response.get("content", "")
                self.messages.append({"role": "assistant", "content": content})
                return content

            self.messages.append({"role": "assistant", **response})

            for tool_call in tool_calls:
                result = self._execute_tool(tool_call)
                self.messages.append({"role": "tool", "content": result})


    def _refresh_preferences(self) -> None:
        preferences = self.preferences_repository.load()
        self.date_resolver = RelativeDateResolver(preferences.timezone)
        self.messages[0]["content"] = build_system_prompt(preferences)

    def _tool_definitions(self) -> list[dict[str, str]]:
        return [
            tool.definition()
            for tool in self.tools.all_tools()
        ]

    def _execute_tool(self, tool_call: dict[str, str]) -> str:
        function = tool_call["function"]

        name = function["name"]
        arguments = function.get("arguments", {})

        tool = self.tools.get_tool(name)
        validated_arguments = tool.args_model.model_validate(arguments)
        result = tool.function(**validated_arguments.model_dump())

        return str(result)
