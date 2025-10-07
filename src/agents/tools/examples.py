from src.core.interface import ExampleServiceProtocol, ExampleToolProtocol
from google.adk.tools.tool_context import ToolContext
# from google.adk.tools.example_tool import ExampleTool 
from google.adk.models.llm_request import LlmRequest

from google.adk.examples import Example
from google.genai import types
from src.agents.repositories.example import VectorDatabaseRepository

from src.agents.dto.internal.example import ExampleQueryRequestDTO

# # Create examples
# examples = [
#     Example(
#         input=types.Content(
#             role="user",
#             parts=[types.Part(text="What is 2+2?")]
#         ),
#         output=[
#             types.Content(
#                 role="model",
#                 parts=[types.Part(text="The answer is 4.......")]
#             )
#         ]
#     ),
#     Example(
#         input=types.Content(
#             role="user",
#             parts=[types.Part(text="What is 5+3?")]
#         ),
#         output=[
#             types.Content(
#                 role="model",
#                 parts=[types.Part(text="The answer is 8......")]
#             )
#         ]
#     )
# ]

# # Create the tool
# example_tool = ExampleTool(examples=examples)

class ExampleTool: 
    
    def __init__(self, service: ExampleServiceProtocol):
        self.service = service
    
    def save_example_data(self, data: str) -> None:
        """
        Saves example data.
        """   
        self.service.save_example_data(data)

    def get_example_data(self, query: str) -> str:
        """
        Retrieves example data.
        """
        requestDto = ExampleQueryRequestDTO(query=query)
        return self.service.get_example_data(requestDto)

    async def process_llm_request(
        self, tool_context: ToolContext, llm_request: LlmRequest
    ) -> None:
        parts = tool_context.user_content.parts
        if not parts or not parts[0].text:
            return
        examples = self.get_example_data("Testing")
        llm_request.append_instructions(examples)