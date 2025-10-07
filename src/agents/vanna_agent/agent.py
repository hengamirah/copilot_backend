from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from src.core.config import COMPLEX_GEMINI_MODEL, API_KEY


from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat
import json
import urllib.parse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import google.genai.types as types
from google.adk.tools.tool_context import ToolContext
#from src.agents.tools.examples import example_tool

class CustomVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(
            self, 
            config=config
        )
        GoogleGeminiChat.__init__(
            self, 
            config={
                'api_key': API_KEY, 
                'model_name': COMPLEX_GEMINI_MODEL
            }
        )

    def generate_query_explanation(self, sql: str):
        my_prompt = [
            self.system_message("You are a helpful assistant that will explain a SQL query"),
            self.user_message("Explain this SQL query: " + sql),
        ]
        return self.submit_prompt(prompt=my_prompt)


# Initialize Vanna instance globally
dataAgent = CustomVanna()
# dataAgent.connect_to_mssql(
#     odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,54180;DATABASE=historian;UID=n8n;PWD=password'
# )

dataAgent.connect_to_postgres(
    host="localhost",
    dbname="historian",
    user="postgres",
    password="password",
    port=5432,
)

# Create wrapper functions with simple signatures for ADK compatibility
def generate_sql_query(question: str) -> str:
    """
    Generate a SQL query based on a natural language question.
    
    This function takes a user's question in plain language and converts it
    into a valid MS SQL Server query that can answer the question.
    
    Args:
        question: The user's question in natural language
        
    Returns:
        A SQL query string that answers the question
    """
    # Call the actual Vanna method with default parameters
    return dataAgent.generate_sql(question=question, allow_llm_to_see_data=False)


def execute_sql_query(sql: str) -> str:
    """
    Execute a SQL query and return the results.
    
    This function runs the provided SQL query against the connected database
    and returns the results as a formatted string.
    
    Args:
        sql: The SQL query to execute
        
    Returns:
        Query results formatted as a string representation of a DataFrame
    """
    try:
        result = dataAgent.run_sql(sql=sql)
        return str(result)
    except Exception as e:
        error_msg = f"Error executing SQL query: {str(e)}\n\nSQL Query:\n{sql}\n\nPlease check the query and try again."
        return error_msg


def generate_plot_code(question: str, sql: str) -> str:
    """
    Generate Plotly visualization code for SQL query results.
    
    This function creates Python code using Plotly that will visualize
    the results of a SQL query in an appropriate chart format.
    
    Args:
        question: The original question for context on what to visualize
        sql: The SQL query whose results should be plotted
        
    Returns:
        Python code string using Plotly to create a visualization
    """
    return dataAgent.generate_plotly_code(question=question, sql=sql)


async def create_plotly_figure(
        tool_context: ToolContext,
        plotly_code: str, 
        sql: str) -> str:
    """
    Execute Plotly code to create and display a visualization.
    
    This function takes Plotly code and the SQL query, executes both,
    and creates a visualization figure from the query results.
    
    Args:
        tool_context: ToolContext,
        plotly_code: Python code that creates a Plotly figure
        sql: The SQL query to get data for the plot
        
    Returns:
        A html str for the figure
    """
    try:
        # First get the data by running the SQL
        df = dataAgent.run_sql(sql)
        # Then create the figure using the plotly code and data
        fig = dataAgent.get_plotly_figure(plotly_code=plotly_code, df=df, dark_mode=True)
        html_string = fig.to_html()
        html_artifact = types.Part.from_bytes(
                data=html_string.encode('utf-8'),
                mime_type="text/html"
            )
            
        # Generate filename
        filename = f"Testing.html"
        
        # Save artifact
        version = await tool_context.save_artifact(filename=filename, artifact=html_artifact)
        
        return f"""Chart created and saved as artifact '{filename}' (version {version})."""
    except Exception as e:
        error_msg = f"Error generating figure: {str(e)}\n\n.Please check the query and try again."
        return error_msg


# Create FunctionTools from the wrapper functions
generate_sql_tool = FunctionTool(func=generate_sql_query)
run_sql_tool = FunctionTool(func=execute_sql_query)
generate_plot_tool = FunctionTool(func=generate_plot_code)
create_figure_tool = FunctionTool(func=create_plotly_figure)


# Create the agent with the wrapped tools
root_agent = LlmAgent(
    model=COMPLEX_GEMINI_MODEL,
    name="database_agent",
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
        - If a query fails, explain the error clearly
        - For visualizations, always generate the code first, then create the figure
        - Present numeric data in a clear, formatted way
    """,
    tools=[generate_sql_tool, run_sql_tool, generate_plot_tool, create_figure_tool],
)


# if __name__ == "__main__":
#     # For Flask app usage (alternative to ADK)
#     from vanna.flask import VannaFlaskApp
#     app = VannaFlaskApp(dataAgent)
#     app.run()