from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from src.agents.sub_agents import (
    DatabaseAgentManager, 
    VisualizationAgentManager, 
    ReportingAgentManager,
    VannaDataAgentManager
)

import src.core.config as C

from google.adk.agents.callback_context import CallbackContext
from google.genai import types # For types.Content

def before_agent_get_user_id(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Logs entry and checks 'skip_llm_agent' in session state.
    If True, returns Content to skip the agent's execution.
    If False or not present, returns None to allow execution.
    """
    print("User id:", callback_context.session.user_id)

class RootAgentManager:
    """
    Manages the root agent instance and provides a clean interface for root agent operations.
    """
    
    # def __init__(self, database_agent: DatabaseAgentManager, visualization_agent: VisualizationAgentManager, reporting_agent: ReportingAgentManager):
    #     """
    #     Initialize the RootAgentManager 
        
    #     """
    #     self._agent: Optional[LlmAgent] = None
    #     self.database_agent = database_agent
    #     self.visualization_agent = visualization_agent
    #     self.reporting_agent = reporting_agent
    
    def __init__(self, data_agent: VannaDataAgentManager, reporting_agent: ReportingAgentManager):
        """
        Initialize the RootAgentManager 
        
        """
        self._agent: Optional[LlmAgent] = None
        self.data_agent = data_agent
        self.reporting_agent = reporting_agent

    @property
    def root_agent(self) -> LlmAgent:
        """
        Lazy-loaded property that creates and returns the root agent.
        
        Returns:
            LlmAgent configured for root agent operations
        """
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def _create_agent(self, name = None) -> LlmAgent:
        """
        Creates and configures the database agent.
        
        Returns:
            Configured LlmAgent instance
        """
        if name == 'openai':
            return LlmAgent(
                model=LiteLlm(model="openai/gpt-4o"),
                name="root_agent",
                description="The root agent that delegates tasks to vanna agent for database and visualization and reporting agent for reporting",
                instruction="""You are a root agent that delegates tasks to vanna agent, and reporting agent.
                            If the user is asking questions about finding data, delegate it to vanna agent.
                            If the user is asking questions about visualizing data, delegate it to vanna agent.
                            If the user is asking questions about reporting data, delegate it to reporting agent. 
                            """,
                sub_agents=[self.data_agent, self.reporting_agent],
                before_agent_callback=before_agent_get_user_id
            )
        else:
            return LlmAgent(
                model=C.COMPLEX_GEMINI_MODEL,
                name="root_agent",
                description="The root agent that delegates tasks to vanna agent for database and visualization and reporting agent for reporting",
                instruction="""You are a root agent that delegates tasks to vanna agent, and reporting agent.
                            If the user is asking questions about finding data, delegate it to vanna agent.
                            If the user is asking questions about visualizing data, delegate it to vanna agent.
                            If the user is asking questions about reporting data, delegate it to reporting agent. 
                            """,
                sub_agents=[self.data_agent, self.reporting_agent],
                before_agent_callback=before_agent_get_user_id
            )