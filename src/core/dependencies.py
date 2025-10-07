from src.agents.root_agent.agent import RootAgentManager
from src.agents.repositories.historian import HistorianDatabaseRepository
from src.agents.services.historian import HistorianDatabaseService
from src.agents.tools.data import DatabaseTool
from src.agents.tools.reporting import ReportingTool
from src.agents.tools.visualizations import VisualizationTool

from src.agents.sub_agents import DatabaseAgentManager, VisualizationAgentManager, ReportingAgentManager
from src.agents.sub_agents import data_agent
from src.core.config import MSSQL

historianDatabaseRepository=HistorianDatabaseRepository(connection_string=MSSQL)
historianDatabaseService=HistorianDatabaseService(repository=historianDatabaseRepository)
databaseTool=DatabaseTool(service=historianDatabaseService)
databaseAgentManager = DatabaseAgentManager(database_tool=databaseTool)

reportingTool=ReportingTool()
reportingAgentManager = ReportingAgentManager(reporting_tool=reportingTool)

visualizationTool=VisualizationTool()

visualizationAgentManager = VisualizationAgentManager(visualization_tool=visualizationTool)

# root_agent = RootAgentManager(
#                 database_agent = databaseAgentManager.database_agent,
#                 reporting_agent =  reportingAgentManager.reporting_agent,
#                 visualization_agent = visualizationAgentManager.visualization_agent,
#             ).root_agent

root_agent = RootAgentManager(
                data_agent = data_agent,
                reporting_agent = reportingAgentManager.reporting_agent,
            ).root_agent
