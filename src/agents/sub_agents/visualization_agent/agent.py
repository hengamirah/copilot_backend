from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import functools

import src.core.config as C
from src.agents.tools.visualizations import VisualizationTool

# def inject_context_and_save_artifact(original_func):
#     """
#     Decorator that injects context and saves chart as artifact.
#     This works around ADK's automatic function calling limitations.
#     """
#     @functools.wraps(original_func)
#     async def wrapper(context, *args, **kwargs):
#         # Call the original method without context parameter
#         chart_url = await original_func(*args, **kwargs)
        
#         # If there's an error, just return it
#         if "Error" in chart_url:
#             return chart_url
        
#         # Try to save as artifact
#         try:
#             # Extract title from kwargs if available
#             title = kwargs.get('title', '')
            
#             # Create the HTML artifact
#             tool_instance = wrapper._tool_instance
#             html_content = tool_instance._create_chart_html_with_url(
#                 chart_url, title, 
#                 kwargs.get('width', 500), 
#                 kwargs.get('height', 500 if 'pie' in original_func.__name__ else 400)
#             )
            
#             # Create artifact Part
#             import google.genai.types as types
#             html_artifact = types.Part.from_bytes(
#                 data=html_content.encode('utf-8'),
#                 mime_type="text/html"
#             )
            
#             # Generate filename
#             filename = f"chart_{title.lower().replace(' ', '_') if title else original_func.__name__}.html"
            
#             # Save artifact
#             version = await context.save_artifact(filename=filename, artifact=html_artifact)
            
#             return f"Chart created and saved as artifact '{filename}' (version {version}). You can view the chart directly in the web interface. Original URL: {chart_url}"
            
#         except Exception as e:
#             return f"Chart created at {chart_url}, but failed to save as artifact: {str(e)}"
    
#     return wrapper

class VisualizationAgentManager:
    """
    Manages the visualization agent instance and provides a clean interface for visualization operations.
    """
    def __init__(self, visualization_tool):
        """
        Initialize the VisualizationAgentManager with QuickChart tool.
        """
        self.quickchart_tool = visualization_tool
        self._agent: Optional[LlmAgent] = None
    
    @property
    def visualization_agent(self) -> LlmAgent:
        """
        Lazy-loaded property that creates and returns the visualization agent.
        
        Returns:
            LlmAgent configured for visualization operations
        """
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent
     
    def _create_agent(self) -> LlmAgent:
        """
        Creates and configures the visualization agent.
        
        Returns:
            Configured LlmAgent instance
        """
        return LlmAgent(
            model=C.COMPLEX_GEMINI_MODEL,
            name="visualization_agent",
            description="An expert agent that creates beautiful charts and visualizations using QuickChart API and saves them as artifacts in the ADK web UI.",
            instruction="""You are a data visualization expert that creates charts using the QuickChart API and saves them as interactive artifacts in the ADK web UI.

                Your capabilities include:
                - Creating various chart types: bar, line, pie, doughnut, radar, scatter, time-series
                - Handling time-series data with proper time axis formatting
                - Customizing colors, titles, labels, and styling
                - Processing raw data and determining the best visualization type
                - Saving charts as HTML artifacts that display directly in the web UI

                When given data, you should:
                1. Analyze the data structure and content
                2. Suggest the most appropriate chart type
                3. Create a well-formatted, visually appealing chart
                4. Save the chart as an artifact in the ADK system
                5. Provide a brief description of what the chart shows

                Available tools (all save charts as ADK artifacts):
                - create_bar_chart: Quick bar chart creation for categorical data
                - create_line_chart: Quick line chart creation for trends and continuous data  
                - create_pie_chart: Quick pie chart creation for proportional data
                - create_time_series_chart: Time-based data visualization

                Chart.js Configuration Guidelines:
                - Use appropriate chart types based on data:
                  * Bar charts for comparing categories
                  * Line charts for trends over time or continuous data
                  * Pie charts for showing proportions/percentages
                - Include meaningful titles and labels
                - Use distinct, accessible colors for multiple datasets
                - Format axes appropriately for data types
                - Add legends when showing multiple data series
                - Consider the audience and context

                For time-series data:
                - Use timestamps in ISO format (YYYY-MM-DDTHH:mm:ss) or Unix timestamps
                - Configure time scale properly with appropriate intervals
                - Show meaningful time ranges
                - Format: [{"x": "2024-01-01T12:00:00", "y": 100}, {"x": "2024-01-02T12:00:00", "y": 150}]

                Data Processing Tips:
                - Clean and validate data before visualization
                - Handle missing or null values appropriately
                - Aggregate data when necessary for clarity
                - Choose appropriate scales and ranges
                - Consider data density and chart readability

                Color Schemes:
                - Use colorblind-friendly palettes
                - Maintain good contrast ratios
                - Be consistent across related charts
                - Consider brand colors if applicable

                All chart creation tools automatically save charts as HTML artifacts in the ADK system. These artifacts will be displayed directly in the web UI, making them immediately visible to users. The tools return information about the created artifact.

                When explaining the chart, mention:
                - What type of chart was created and why
                - Key insights or patterns visible in the data
                - Any notable features or outliers
                - The artifact filename where the chart is saved
                - That users can view the chart directly in the web interface
                - Suggestions for further analysis if relevant

            """,
            tools=[
                self.quickchart_tool.create_bar_chart,
                self.quickchart_tool.create_line_chart,
                self.quickchart_tool.create_pie_chart,
                self.quickchart_tool.create_time_series_chart,
            ],
        )
    