from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.genai import types
from src.core.config import COMPLEX_GEMINI_MODEL
from src.core.interface import VannaToolProtocol
from typing import Optional
#from src.agents.tools.examples import example_tool


# # Create FunctionTools from the wrapper functions
# generate_sql_tool = FunctionTool(func=generate_sql_query)
# run_sql_tool = FunctionTool(func=execute_sql_query)
# generate_plot_tool = FunctionTool(func=generate_plot_code)
# create_figure_tool = FunctionTool(func=create_plotly_figure)

class VannaDataAgentManager:
    def __init__(self, vanna_tool: VannaToolProtocol):
        """
        Initialize the VannaAgentManager with a Vanna tool.
        
        Args:
            vanna_tool: An instance implementing VannaToolProtocol
        """
        self.vanna_tool = vanna_tool
        self._agent: Optional[LlmAgent] = None
    
    @property
    def vanna_agent(self) -> LlmAgent:
        """
        Lazy-loaded property that creates and returns the database agent.
        
        Returns:
            LlmAgent configured for database operations
        """
        if self._agent is None:
            self._agent = self._create_agent("openai")
        return self._agent
    
    def _create_agent(self, name) -> LlmAgent:
        """
        Creates and configures the vanna agent.
        
        Returns:
            Configured LlmAgent instance
        """
        if name == 'openai':
            return LlmAgent(
                model=LiteLlm(model="openai/gpt-4o"),
                name="vanna_agent",
                description="An agent that retrieves information from a historian database by running SQL queries.",
                instruction="""
                    You are a database assistant for querying a historian database. Your goal is to answer user questions accurately.

                    **Workflow:**
                    1. When a user asks a question, use `generate_sql_query` to create the appropriate SQL query
                    2. Use `execute_sql_query` to run the query and get results
                    3. Present the results clearly to the user
                    4. If the user requests a visualization (chart, plot, graph):
                    - First use `generate_plot_code` with the question and SQL query
                    - Then use `create_plotly_figure` to create the actual visualization

                    **Important Guidelines:**
                    - Only use the provided tools - do not fabricate data or queries
                    - Only proceed to create visualization when user instructs
                    - If a query fails, explain the error clearly
                    - For visualizations, always generate the code first, then create the figure
                    - Present numeric data in a clear, formatted way
                """,
                generate_content_config=types.GenerateContentConfig(
                                            temperature=1, 
                                            max_output_tokens=250,
                                            safety_settings=[
                                                types.SafetySetting(
                                                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                                                )
                                            ]
                                        ),
                tools=[self.vanna_tool.generate_sql_query, self.vanna_tool.execute_sql_query, self.vanna_tool.generate_plot_code, self.vanna_tool.create_plotly_figure],
            )
        else:
            return LlmAgent(
                model=COMPLEX_GEMINI_MODEL,
                name="vanna_agent",
                description="An agent that retrieves information from a historian database by running SQL queries.",
                instruction="""
                    You are a database assistant for querying a historian database. Your goal is to answer user questions accurately.

                    **Workflow:**
                    1. When a user asks a question, use `generate_sql_query` to create the appropriate SQL query
                    2. Use `execute_sql_query` to run the query and get results
                    3. Present the results clearly to the user
                    4. If the user requests a visualization (chart, plot, graph):
                    - First use `generate_plot_code` with the question and SQL query
                    - Then use `create_plotly_figure` to create the actual visualization

                    **Important Guidelines:**
                    - Only use the provided tools - do not fabricate data or queries
                    - Only proceed to create visualization when user instructs
                    - If a query fails, explain the error clearly
                    - For visualizations, always generate the code first, then create the figure
                    - Present numeric data in a clear, formatted way
                """,
                generate_content_config=types.GenerateContentConfig(
                                            temperature=1, 
                                            max_output_tokens=250,
                                            safety_settings=[
                                                types.SafetySetting(
                                                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                                                )
                                            ]
                                        ),
                tools=[self.vanna_tool.generate_sql_query, self.vanna_tool.execute_sql_query, self.vanna_tool.generate_plot_code, self.vanna_tool.create_plotly_figure],
            )
    
