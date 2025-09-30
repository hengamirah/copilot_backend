from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class SqlQueryResult(BaseModel):
    """Represents SQL query and its results"""
    query: str = Field(..., description="The SQL query that was executed")
    results: List[Dict[str, Any]] = Field(..., description="Query results as list of dictionaries")
    execution_time_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")
    row_count: int = Field(..., description="Number of rows returned")


class VisualizationData(BaseModel):
    """Represents visualization information"""
    chart_url: str = Field(..., description="URL of the generated chart")
    chart_type: str = Field(..., description="Type of chart (bar, line, pie, etc.)")
    chart_title: Optional[str] = Field(None, description="Title of the chart")
    description: Optional[str] = Field(None, description="Description of what the chart shows")


class ReportData(BaseModel):
    """Complete report data structure"""
    title: str = Field(..., description="Report title")
    sql_data: Optional[SqlQueryResult] = Field(None, description="SQL query and results")
    visualization: Optional[VisualizationData] = Field(None, description="Chart visualization data")
    summary: Optional[str] = Field(None, description="Executive summary")
    insights: Optional[List[str]] = Field(None, description="Key insights from the data")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations based on findings")


class ReportingTool:
    """Tool for generating comprehensive reports"""
    
    def __init__(self):
        pass
    
    def generate_markdown_report(self, report_data: ReportData) -> str:
        """
        Generate a markdown report from report data.
        
        Args:
            report_data: Complete report data
            
        Returns:
            Formatted markdown report
        """
        markdown_content = []
        
        # Report Header
        markdown_content.append(f"# {report_data.title}")
        markdown_content.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        markdown_content.append("")
        
        # Executive Summary
        if report_data.summary:
            markdown_content.append("## Executive Summary")
            markdown_content.append(report_data.summary)
            markdown_content.append("")
        
        # SQL Query Section
        if report_data.sql_data:
            markdown_content.append("## Data Query")
            markdown_content.append("### SQL Query Executed")
            markdown_content.append("```sql")
            markdown_content.append(report_data.sql_data.query)
            markdown_content.append("```")
            markdown_content.append("")
            
            # Query Metadata
            markdown_content.append("### Query Results Summary")
            markdown_content.append(f"- **Rows Retrieved:** {report_data.sql_data.row_count}")
            if report_data.sql_data.execution_time_ms:
                markdown_content.append(f"- **Execution Time:** {report_data.sql_data.execution_time_ms:.2f} ms")
            markdown_content.append("")
            
            # Data Table (first 10 rows for readability)
            if report_data.sql_data.results:
                markdown_content.append("### Sample Data")
                sample_data = report_data.sql_data.results[:10]  # Limit to first 10 rows
                
                if sample_data:
                    # Create table headers
                    headers = list(sample_data[0].keys())
                    markdown_content.append("| " + " | ".join(headers) + " |")
                    markdown_content.append("| " + " | ".join(["---"] * len(headers)) + " |")
                    
                    # Add data rows
                    for row in sample_data:
                        values = [str(row.get(header, "")) for header in headers]
                        markdown_content.append("| " + " | ".join(values) + " |")
                    
                    if len(report_data.sql_data.results) > 10:
                        markdown_content.append(f"*Showing first 10 of {report_data.sql_data.row_count} rows*")
                    
                    markdown_content.append("")
        
        # Visualization Section
        if report_data.visualization:
            markdown_content.append("## Data Visualization")
            if report_data.visualization.chart_title:
                markdown_content.append(f"### {report_data.visualization.chart_title}")
            
            markdown_content.append(f"![Chart]({report_data.visualization.chart_url})")
            markdown_content.append("")
            
            if report_data.visualization.description:
                markdown_content.append(f"**Chart Type:** {report_data.visualization.chart_type.title()}")
                markdown_content.append(f"**Description:** {report_data.visualization.description}")
                markdown_content.append("")
        
        # Key Insights
        if report_data.insights:
            markdown_content.append("## Key Insights")
            for i, insight in enumerate(report_data.insights, 1):
                markdown_content.append(f"{i}. {insight}")
            markdown_content.append("")
        
        # Recommendations
        if report_data.recommendations:
            markdown_content.append("## Recommendations")
            for i, recommendation in enumerate(report_data.recommendations, 1):
                markdown_content.append(f"{i}. {recommendation}")
            markdown_content.append("")
        
        # Footer
        markdown_content.append("---")
        markdown_content.append("*This report was generated automatically using AI-powered analysis.*")
        
        return "\n".join(markdown_content)
    
    def create_report_from_components(
        self,
        title: str,
        sql_query: Optional[str] = None,
        sql_results: Optional[List[Dict[str, Any]]] = None,
        chart_url: Optional[str] = None,
        chart_type: Optional[str] = None,
        chart_title: Optional[str] = None,
        summary: Optional[str] = None,
        insights: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        execution_time_ms: Optional[float] = None
    ) -> str:
        """
        Create a report from individual components.
        
        Args:
            title: Report title
            sql_query: SQL query that was executed
            sql_results: Results from SQL query
            chart_url: URL of generated chart
            chart_type: Type of chart
            chart_title: Title of chart
            summary: Executive summary
            insights: List of key insights
            recommendations: List of recommendations
            execution_time_ms: Query execution time
            
        Returns:
            Formatted markdown report
        """
        # Build SQL data if provided
        sql_data = None
        if sql_query and sql_results is not None:
            sql_data = SqlQueryResult(
                query=sql_query,
                results=sql_results,
                row_count=len(sql_results),
                execution_time_ms=execution_time_ms
            )
        
        # Build visualization data if provided
        visualization = None
        if chart_url:
            visualization = VisualizationData(
                chart_url=chart_url,
                chart_type=chart_type or "unknown",
                chart_title=chart_title,
                description=f"Visual representation of the data showing {chart_type or 'chart'} format"
            )
        
        # Create report data
        report_data = ReportData(
            title=title,
            sql_data=sql_data,
            visualization=visualization,
            summary=summary,
            insights=insights,
            recommendations=recommendations
        )
        
        return self.generate_markdown_report(report_data)
    
    def analyze_sql_results(self, sql_results: List[Dict[str, Any]], context: str = "") -> Dict[str, Any]:
        """
        Analyze SQL results to extract insights.
        
        Args:
            sql_results: SQL query results
            context: Context about what the data represents
            
        Returns:
            Dictionary with analysis results
        """
        if not sql_results:
            return {"insights": ["No data available for analysis"], "summary": "No results returned from query"}
        
        row_count = len(sql_results)
        columns = list(sql_results[0].keys()) if sql_results else []
        
        # Basic statistical analysis
        numeric_columns = []
        for col in columns:
            try:
                # Check if column contains numeric data
                values = [row[col] for row in sql_results if row[col] is not None]
                if values and all(isinstance(v, (int, float)) for v in values):
                    numeric_columns.append(col)
            except:
                continue
        
        insights = [
            f"Dataset contains {row_count} records across {len(columns)} columns",
            f"Numeric columns available for analysis: {', '.join(numeric_columns) if numeric_columns else 'None'}"
        ]
        
        if numeric_columns:
            for col in numeric_columns[:3]:  # Analyze first 3 numeric columns
                values = [row[col] for row in sql_results if row[col] is not None]
                if values:
                    avg_val = sum(values) / len(values)
                    min_val = min(values)
                    max_val = max(values)
                    insights.append(f"{col}: Average {avg_val:.2f}, Range {min_val} to {max_val}")
        
        return {
            "insights": insights,
            "summary": f"Analysis of {row_count} records with focus on {context}" if context else f"Analysis of {row_count} records"
        }
