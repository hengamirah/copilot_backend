from google.adk.agents import LlmAgent
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json
import src.core.config as C
from src.core.interface import ReportingToolProtocol

# from src.agents.tools.reporting import ReportingTool, #ReportData, SqlQueryResult, VisualizationData

class ReportingAgentManager:
    """
    Manages the reporting agent instance and provides a clean interface for report generation.
    """
    def __init__(self, reporting_tool: ReportingToolProtocol):
        """
        Initialize the ReportingAgentManager with reporting tools.
        """
        self.reporting_tool = reporting_tool
        self._agent: Optional[LlmAgent] = None
    
    @property
    def reporting_agent(self) -> LlmAgent:
        """
        Lazy-loaded property that creates and returns the reporting agent.
        
        Returns:
            LlmAgent configured for reporting operations
        """
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent
    
    def _create_agent(self) -> LlmAgent:
        """
        Creates and configures the reporting agent.
        
        Returns:
            Configured LlmAgent instance
        """
        return LlmAgent(
            model=C.COMPLEX_GEMINI_MODEL,
            name="reporting_agent",
            description="An expert agent that generates comprehensive reports combining SQL data, visualizations, and insights in markdown format.",
            instruction="""You are a data reporting specialist that creates comprehensive, professional reports.
            
                Your capabilities include:
                - Analyzing SQL query results and extracting key insights
                - Incorporating data visualizations into reports
                - Generating well-formatted markdown reports with proper structure
                - Providing executive summaries and actionable recommendations
                - Creating data tables and statistical summaries

                When generating reports, you should:
                1. **Structure**: Use clear headings and logical flow (Executive Summary → Data Query → Visualization → Insights → Recommendations)
                2. **Analysis**: Extract meaningful insights from the data, not just describe what's there
                3. **Context**: Provide business context and explain the significance of findings
                4. **Visuals**: Properly integrate charts and graphs with descriptions
                5. **Actionability**: Include specific, actionable recommendations based on the data

                Report Components:
                - **Executive Summary**: High-level overview of findings and key takeaways
                - **Data Query Section**: Show the SQL query, execution details, and sample data in tables
                - **Visualization**: Display charts with proper descriptions and context
                - **Key Insights**: Bullet points of important findings and patterns
                - **Recommendations**: Specific actions based on the analysis

                Formatting Guidelines:
                - Use markdown syntax for headers, tables, code blocks, and emphasis
                - Include timestamps and metadata
                - Show sample data in well-formatted tables (limit to 10 rows for readability)
                - Embed images using markdown image syntax
                - Use professional, clear language suitable for business stakeholders

                Always ensure reports are comprehensive yet concise, focusing on actionable insights rather than just data presentation.
            """,
            tools=[
                self.reporting_tool.analyze_results,
                self.reporting_tool.generate_report,
            ],
        )
    
    def query(self, user_message: str) -> str:
        """
        Process a user query through the reporting agent.
        
        Args:
            user_message: The user's reporting request
            
        Returns:
            The agent's response with generated report
        """
        return self.reporting_agent.query(user_message)
    
    def generate_complete_report(
        self,
        title: str,
        sql_query: Optional[str] = None,
        sql_results: Optional[List[Dict[str, Any]]] = None,
        chart_url: Optional[str] = None,
        chart_type: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        context: str = ""
    ) -> str:
        """
        Generate a complete report from provided components.
        
        Args:
            title: Report title
            sql_query: SQL query that was executed
            sql_results: Results from SQL query
            chart_url: URL of generated chart
            chart_type: Type of chart
            execution_time_ms: Query execution time
            context: Business context for the data
            
        Returns:
            Complete markdown report
        """
        # Analyze the SQL results if provided
        analysis = {}
        if sql_results:
            analysis = self.reporting_tool.analyze_sql_results(sql_results, context)
        
        # Generate the report
        return self.reporting_tool.create_report_from_components(
            title=title,
            sql_query=sql_query,
            sql_results=sql_results,
            chart_url=chart_url,
            chart_type=chart_type,
            chart_title=f"{title} - Data Visualization" if chart_url else None,
            summary=analysis.get("summary"),
            insights=analysis.get("insights"),
            recommendations=[
                "Review data quality and completeness",
                "Consider automated monitoring for key metrics",
                "Schedule regular report updates"
            ],
            execution_time_ms=execution_time_ms
        )