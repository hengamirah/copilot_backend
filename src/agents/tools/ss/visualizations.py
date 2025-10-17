import json
import urllib.parse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import google.genai.types as types
from google.adk.tools.tool_context import ToolContext
import os # <--- NEW IMPORT

class ChartConfig(BaseModel):
    """Chart.js configuration for QuickChart"""
    type: str = Field(..., description="Chart type (bar, line, pie, doughnut, radar, etc.)")
    data: Dict[str, Any] = Field(..., description="Chart data including labels and datasets")
    options: Optional[Dict[str, Any]] = Field(None, description="Chart options for styling and behavior")

class VisualizationTool:
    """Tool for creating charts using QuickChart API and saving as ADK artifacts"""
    
    def __init__(self):
        self.BASE_URL = "https://quickchart.io/chart"
    
    def _create_chart_url(
        self,
        chart_config: Dict[str, Any],
        width: int = 500,
        height: int = 300,
        background_color: str = "white",
        format: str = "png",
        device_pixel_ratio: int = 1
    ) -> str:
        """
        Create a chart URL using QuickChart API.
        """
        try:
            # Convert chart config to JSON string
            chart_json = json.dumps(chart_config, separators=(',', ':'))
            
            # URL encode the chart configuration
            chart_encoded = urllib.parse.quote(chart_json)
            
            # Build the URL with parameters
            params = {
                'c': chart_encoded,
                'width': width,
                'height': height,
                'backgroundColor': background_color,
                'format': format,
                'devicePixelRatio': device_pixel_ratio
            }
            
            # Construct the full URL
            url_parts = []
            for key, value in params.items():
                if key == 'c':
                    url_parts.append(f"{key}={value}")
                else:
                    url_parts.append(f"{key}={urllib.parse.quote(str(value))}")
            
            chart_url = f"{self.BASE_URL}?{'&'.join(url_parts)}"
            
            return chart_url
            
        except Exception as e:
            return f"Error creating chart: {str(e)}"
    
    def _create_chart_html_with_url(self, chart_url: str, title: str = "", width: int = 500, height: int = 300) -> str:
        """
        Create HTML content that embeds the chart image.
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title or 'Chart'}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                .chart-container {{
                    background: white;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    max-width: 100%;
                    text-align: center;
                }}
                .chart-title {{
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    color: #2c3e50;
                    text-align: center;
                }}
                .chart-image {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                }}
                .chart-info {{
                    margin-top: 15px;
                    font-size: 12px;
                    color: #7f8c8d;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                {f'<div class="chart-title">{title}</div>' if title else ''}
                <img src="{chart_url}" alt="{title or 'Chart'}" class="chart-image" width="{width}" height="{height}">
                <div class="chart-info">Generated with QuickChart API</div>
            </div>
        </body>
        </html>
        """
        return html_content

    async def _save_chart_as_artifact(
            self, 
            tool_context: ToolContext,
            chart_url: str, 
            title: str = "", 
            width: int = 500, 
            height: int = 300) -> str:
        """
        Helper method to save chart as artifact.
        """
        try:
            # Create HTML content
            html_content = self._create_chart_html_with_url(chart_url, title, width, height)
            
            base_name = title.lower().replace(' ', '_') if title else 'visualization'
            
            # Artifact Filename (saved to ADK store's virtual path)
            artifact_filename = f"charts/{base_name}.html" 

            # Local File Path (saved to the machine's file system)
            local_directory = "local_charts"
            # Ensure the local directory exists
            os.makedirs(local_directory, exist_ok=True)
            local_file_path = os.path.join(local_directory, f"{base_name}.html")

            # 2. Save to Local File System
            with open(local_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Create artifact Part
            html_artifact = types.Part.from_bytes(
                data=html_content.encode('utf-8'),
                mime_type="text/html"
            )
            
            # Generate filename
            filename = f"chart_{title.lower().replace(' ', '_') if title else 'visualization'}.html"
            
            # Save artifact
            version = await tool_context.save_artifact(filename=filename, artifact=html_artifact)
            
            return f"Chart created and saved as artifact '{filename}' (version {version}). Chart URL: {chart_url}"
            
        except Exception as e:
            return f"Chart created at {chart_url}, but failed to save as artifact: {str(e)}"

    # Remove context parameter from function signatures - ADK will inject it automatically
    # async def create_chart(
    #     self,
    #     tool_context: ToolContext,
    #     chart_config: Dict[str, Any],
    #     width: int = 500,
    #     height: int = 300,
    #     background_color: str = "white",
    #     format: str = "png",
    #     device_pixel_ratio: int = 1,
    # ) -> str:
    #     """
    #     Create a chart using QuickChart API and save as artifact.
        
    #     Args:
    #         chart_config: Chart.js configuration object
    #         width: Width of the image in pixels (default: 500)
    #         height: Height of the image in pixels (default: 300)
    #         background_color: Background color (default: white)
    #         format: Output format (png, jpg, svg, pdf, webp) (default: png)
    #         device_pixel_ratio: Device pixel ratio (1 or 2) (default: 1)
            
    #     Returns:
    #         Success message with artifact info and chart URL
    #     """
    #     chart_url = self._create_chart_url(chart_config, width, height, background_color, format, device_pixel_ratio)
        
    #     if "Error creating chart:" in chart_url:
    #         return chart_url
        
    #     # Extract title from config if available
    #     title = ""
    #     if "options" in chart_config and "title" in chart_config["options"]:
    #         title = chart_config["options"]["title"].get("text", "")
        
    #     # Save as artifact
    #     return await self._save_chart_as_artifact(tool_context, chart_url, title, width, height)
    
    async def create_bar_chart(
        self,
        tool_context: ToolContext,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        title: str = "",
    ) -> str:
        """
        Create a bar chart and save as artifact.
        
        Args:
            labels: X-axis labels
            datasets: List of datasets with label and data
            title: Chart title (empty string for no title)
            
        Returns:
            Success message with artifact info and chart URL
        """
        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": datasets
            }
        }
        
        if title:
            config["options"] = {
                "title": {
                    "display": True,
                    "text": title
                }
            }
        
        chart_url = self._create_chart_url(config)
        
        if "Error creating chart:" in chart_url:
            return chart_url
            
        # Save as artifact
        return await self._save_chart_as_artifact(tool_context, chart_url, title)
    
    async def create_line_chart(
        self,
        tool_context: ToolContext,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        title: str = "",
    ) -> str:
        """
        Create a line chart and save as artifact.
        
        Args:
            labels: X-axis labels
            datasets: List of datasets with label and data
            title: Chart title (empty string for no title)
            
        Returns:
            Success message with artifact info and chart URL
        """
        config = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": datasets
            }
        }
        
        if title:
            config["options"] = {
                "title": {
                    "display": True,
                    "text": title
                }
            }
        
        chart_url = self._create_chart_url(config)
        
        if "Error creating chart:" in chart_url:
            return chart_url
            
        # Save as artifact
        return await self._save_chart_as_artifact(tool_context, chart_url, title)
    
    async def create_pie_chart(
        self,
        tool_context: ToolContext,
        labels: List[str],
        data: List[float],
        title: str = "",
        background_colors: str = "",
    ) -> str:
        """
        Create a pie chart and save as artifact.
        
        Args:
            labels: Labels for pie slices
            data: Data values for pie slices (as floats)
            title: Chart title (empty string for no title)
            background_colors: Colors for pie slices as JSON string array (empty for default colors)
            
        Returns:
            Success message with artifact info and chart URL
        """
        # Parse background colors if provided
        if background_colors:
            try:
                colors = json.loads(background_colors)
            except:
                colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                         '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF']
        else:
            colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                     '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF']
        
        dataset = {
            "data": data,
            "backgroundColor": colors
        }
        
        config = {
            "type": "pie",
            "data": {
                "labels": labels,
                "datasets": [dataset]
            }
        }
        
        if title:
            config["options"] = {
                "title": {
                    "display": True,
                    "text": title
                }
            }
        
        chart_url = self._create_chart_url(config)
        
        if "Error creating chart:" in chart_url:
            return chart_url
            
        # Save as artifact
        return await self._save_chart_as_artifact(tool_context, chart_url, title)

    async def create_time_series_chart(
        self,
        tool_context: ToolContext,
        data_json: str,
        label: str = "Data",
        title: str = "",
    ) -> str:
        """
        Create a time series chart and save as artifact.
        
        Args:
            data_json: JSON string of data points [{"x": "timestamp", "y": value}, ...]
            label: Dataset label
            title: Chart title (empty string for no title)
            
        Returns:
            Success message with artifact info and chart URL
        """
        try:
            data_points = json.loads(data_json)
        except:
            return "Error: Invalid JSON format for data_json. Expected format: [{\"x\": \"timestamp\", \"y\": value}, ...]"
            
        config = {
            "type": "line",
            "data": {
                "datasets": [{
                    "label": label,
                    "data": data_points,
                    "borderColor": '#36A2EB',
                    "fill": False
                }]
            },
            "options": {
                "scales": {
                    "x": {
                        "type": "time",
                        "time": {
                            "displayFormats": {
                                "hour": "MMM DD HH:mm"
                            }
                        }
                    }
                }
            }
        }
        
        if title:
            config["options"]["title"] = {
                "display": True,
                "text": title
            }
        
        chart_url = self._create_chart_url(config)
        
        if "Error creating chart:" in chart_url:
            return chart_url
            
        # Save as artifact
        return await self._save_chart_as_artifact(tool_context, chart_url, title)