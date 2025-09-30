from src.core.interface import ExampleServiceProtocol, ExampleToolProtocol
from google.adk.tools.tool_context import ToolContext

class ExampleTool: 
    
    def __init__(self, service: ExampleServiceProtocol):
        self.service = service
    
    def save_example_data(self, data: str) -> None:
        """
        Saves example data.
        """   
        self.service.save_example_data(data)

    def get_example_data(self) -> str:
        """
        Retrieves example data.
        """
        return self.service.get_example_data()
        

