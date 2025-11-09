from google.adk.agents import LlmAgent
from typing import Optional
import src.core.config as C
from src.core.interface import DatabaseToolProtocol
# from src.agents.repositories.example import VectorDatabaseRepository
from src.agents.tools.ss.examples import ExampleTool

class DatabaseAgentManager:
    """
    Manages the database agent instance and provides a clean interface for database operations.
    """
    def __init__(self, database_tool: DatabaseToolProtocol):
        """
        Initialize the DatabaseAgentManager with a database tool.
        
        Args:
            database_tool: An instance implementing DatabaseToolProtocol
        """
        self.database_tool = database_tool
        # self.example_tool = ExampleTool()
        self._agent: Optional[LlmAgent] = None
    
    @property
    def database_agent(self) -> LlmAgent:
        """
        Lazy-loaded property that creates and returns the database agent.
        
        Returns:
            LlmAgent configured for database operations
        """
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent
    
    def _create_agent(self) -> LlmAgent:
        """
        Creates and configures the database agent.
        
        Returns:
            Configured LlmAgent instance
        """
        return LlmAgent(
            model=C.COMPLEX_GEMINI_MODEL,
            name="database_agent",
            description="An agent that retrieves information from a power database by running SQL queries.",
            instruction=f"""You are an expert at retrieving time-series data. Use your tools to answer user questions about tag values. 
                
                Guidelines:
                - The database is Microsoft SQL Server 
                - When encountering error, get schema from the power table to readjust your query calls
                - Whenever the output from the database has more than 10 rows, you should return the first 10 rows to the user only to not keep user waiting. 
                
                Available operations:
                - For specific time range queries, construct appropriate SQL queries with date/time filters
                - For latest values, use ORDER BY timestamp DESC LIMIT 1
                - Always validate query parameters and handle potential errors gracefully
                
                When presenting results:
                - Show data in a clear, readable format
                - Include relevant timestamps
                - Summarize key findings
                - Handle empty results gracefully
                
                If you encounter errors, explain them clearly and suggest alternatives when possible.

                """,
            tools=[self.database_tool.execute_query, self.example_tool.get_example_data],
        )
    
#can you compare energy consumption of Production Line 1 and Production Line 2