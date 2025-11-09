from src.agents.root_agent.agent import RootAgentManager

from src.agents.repositories import (
    HistorianDatabaseRepository, 
    CustomVanna, 
    VannaRepository,
    ReportingRepository
)

from src.agents.services import (
    HistorianDatabaseService,
    VannaService,
    ReportingService
)

from src.agents.tools import (
    DatabaseTool, 
    ReportingTool, 
    VisualizationTool, 
    VannaTool
)

from src.agents.sub_agents import (
    DatabaseAgentManager, 
    VisualizationAgentManager, 
    ReportingAgentManager,
    VannaDataAgentManager
    )

from src.core.config import MSSQL, CHROMA_PATH, HOST, PORT, DBNAME, USER, PASSWORD


# --- Custom Database and Visualization Agent ---
historianDatabaseRepository=HistorianDatabaseRepository(connection_string=MSSQL)
historianDatabaseService=HistorianDatabaseService(repository=historianDatabaseRepository)
databaseTool=DatabaseTool(service=historianDatabaseService)
databaseAgentManager = DatabaseAgentManager(database_tool=databaseTool)

visualizationTool=VisualizationTool()
visualizationAgentManager = VisualizationAgentManager(visualization_tool=visualizationTool)
# --- Custom Database and Visualization Agent ---

# --- Custom Vanna Agent ---

dataAgent = CustomVanna({"path":CHROMA_PATH})

# dataAgent.connect_to_mssql(
#     odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,54180;DATABASE=power;UID=n8n;PWD=password'
# )

dataAgent.connect_to_postgres(
    host=HOST,
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    port=PORT,
)

try:
    # Use the 'run_sql' method (common in Vanna) to run a simple query
    test_result = dataAgent.run_sql("SELECT 1")
    if test_result is not None:
        print("✅ Simple database connection test successful!")
    else:
        print("⚠️ Database connection test ran, but returned no result.")
except Exception as e:
    print(f"❌ Database connection test failed: {e}")

vannaRepository = VannaRepository(vanna_model=dataAgent)
vannaService = VannaService(repository=vannaRepository)
vannaTool = VannaTool(service=vannaService)
data_agent = VannaDataAgentManager(vanna_tool=vannaTool)
# --- Custom Vanna Agent ---

# --- Custom Reporting Agent ---
reportingRepository = ReportingRepository()
reportingService = ReportingService(repository=reportingRepository)
reportingTool=ReportingTool(service=reportingService)
reportingAgentManager = ReportingAgentManager(reporting_tool=reportingTool)

# --- Custom Reporting Agent ---

# root_agent = RootAgentManager(
#                 database_agent = databaseAgentManager.database_agent,
#                 reporting_agent =  reportingAgentManager.reporting_agent,
#                 visualization_agent = visualizationAgentManager.visualization_agent,
#             ).root_agent

root_agent = RootAgentManager(
                data_agent = data_agent.vanna_agent,
                reporting_agent = reportingAgentManager.reporting_agent,
            ).root_agent
