from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.example_tool import ExampleTool

VANNA_AGENT_DESCRIPTION = """
Use this AI agent to query SQL databases.
When calling this agent, you MUST provide all of the following arguments:
- question: The user's last natural language question about the database.
- initial_prompt: System-level instructions for how the SQL generation should behave.
- question_sql_list: A list of example "question" to "SQL query" pairs.
- ddl_list: A list of DDL strings (e.g., CREATE TABLE...) for the database schema.
- doc_list: A list of strings containing relevant documentation.
"""

data_agent = RemoteA2aAgent(
    name="vanna_agent",
    description=VANNA_AGENT_DESCRIPTION,
    timeout = 120,
    agent_card=(
        f"http://localhost:5000/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)