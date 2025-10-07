from typing import Optional

from google.adk.agents import LlmAgent

from src.agents.sub_agents import DatabaseAgentManager, VisualizationAgentManager, ReportingAgentManager
# from src.agents.vanna.main import DataAgentManager
import src.core.config as C

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
    
    def __init__(self, data_agent, reporting_agent: ReportingAgentManager):
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
    
    # def _create_agent(self) -> LlmAgent:
    #     """
    #     Creates and configures the database agent.
        
    #     Returns:
    #         Configured LlmAgent instance
    #     """
    #     return LlmAgent(
    #         model=C.COMPLEX_GEMINI_MODEL,
    #         name="root_agent",
    #         description="The root agent that delegates tasks to database agent, visualization agent and reporting agent",
    #         instruction="""You are a root agent that delegates tasks to database agent, visualization agent and reporting agent.
    #                     If the user is asking questions about finding data, delegate it to database agent.
    #                     If the user is asking questions about visualizing data, delegate it to visualization agent.
    #                     If the user is asking questions about reporting data, delegate it to reporting agent. 
    #                     """,
    #         sub_agents=[self.database_agent, self.visualization_agent, self.reporting_agent],
    #     )

    def _create_agent(self) -> LlmAgent:
        """
        Creates and configures the database agent.
        
        Returns:
            Configured LlmAgent instance
        """
        return LlmAgent(
            model=C.COMPLEX_GEMINI_MODEL,
            name="root_agent",
            description="The root agent that delegates tasks to database agent, visualization agent and reporting agent",
            instruction="""You are a root agent that delegates tasks to database agent, visualization agent and reporting agent.
                        If the user is asking questions about finding data, delegate it to database agent.
                        If the user is asking questions about visualizing data, delegate it to visualization agent.
                        If the user is asking questions about reporting data, delegate it to reporting agent. 
                        """,
            sub_agents=[self.data_agent, self.reporting_agent],
        )