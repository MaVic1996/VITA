
from vita.llm.ollama import OllamaClient
from vita.tools.registry import ToolRegistry

class Agent:

    def __init__(self, llm_client: OllamaClient, tools: ToolRegistry) -> None:
        self.llm_client = llm_client
        self.tools = tools
        self.messages: list[dict[str, str]] = []

    def chat(self, user_message: str) -> str:
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

    def _tool_definitions(self) -> list[dict[str, str]]:
        return [
            { "type": "function",
              "function": {
                "name": tool.name,   
                "description": tool.description,
                "parameters": tool.parameters,
              },
            }
            for tool in self.tools.all_tools()
        ]

    def _execute_tool(self, tool_call: dict[str, str]) -> str:
        function = tool_call["function"]

        name = function["name"]
        arguments = function.get("arguments", {})

        tool = self.tools.get_tool(name)
        result = tool.function(**arguments)
        return str(result)