from typing import Dict, Any, List, Optional
from datetime import datetime
from src.core import logger, ReportingRepositoryError


class ReportingRepository:
    """Repository for report generation operations - works with primitives"""
    
    def __init__(self):
        pass
    
    def generate_markdown(
        self,
        title: str,
        generated_at: datetime,
        summary: Optional[str] = None,
        sql_query: Optional[str] = None,
        sql_results: Optional[List[Dict[str, Any]]] = None,
        sql_row_count: Optional[int] = None,
        execution_time_ms: Optional[float] = None,
        chart_url: Optional[str] = None,
        chart_type: Optional[str] = None,
        chart_title: Optional[str] = None,
        chart_description: Optional[str] = None,
        insights: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None
    ) -> str:
        """
        Generate markdown content from raw data.
        
        Args:
            title: Report title
            generated_at: Generation timestamp
            summary: Executive summary
            sql_query: SQL query that was executed
            sql_results: Query results
            sql_row_count: Number of rows
            execution_time_ms: Execution time
            chart_url: Chart URL
            chart_type: Chart type
            chart_title: Chart title
            chart_description: Chart description
            insights: List of insights
            recommendations: List of recommendations
            
        Returns:
            Formatted markdown string
        """
        try:
            markdown_content = []
            
            # Report Header
            markdown_content.append(f"# {title}")
            markdown_content.append(f"*Generated on: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}*")
            markdown_content.append("")
            
            # Executive Summary
            if summary:
                markdown_content.append("## Executive Summary")
                markdown_content.append(summary)
                markdown_content.append("")
            
            # SQL Query Section
            if sql_query and sql_results is not None:
                markdown_content.append("## Data Query")
                markdown_content.append("### SQL Query Executed")
                markdown_content.append("```sql")
                markdown_content.append(sql_query)
                markdown_content.append("```")
                markdown_content.append("")
                
                # Query Metadata
                markdown_content.append("### Query Results Summary")
                markdown_content.append(f"- **Rows Retrieved:** {sql_row_count or len(sql_results)}")
                if execution_time_ms:
                    markdown_content.append(f"- **Execution Time:** {execution_time_ms:.2f} ms")
                markdown_content.append("")
                
                # Data Table (first 10 rows for readability)
                if sql_results:
                    markdown_content.append("### Sample Data")
                    sample_data = sql_results[:10]
                    
                    if sample_data:
                        # Create table headers
                        headers = list(sample_data[0].keys())
                        markdown_content.append("| " + " | ".join(headers) + " |")
                        markdown_content.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        
                        # Add data rows
                        for row in sample_data:
                            values = [str(row.get(header, "")) for header in headers]
                            markdown_content.append("| " + " | ".join(values) + " |")
                        
                        if len(sql_results) > 10:
                            markdown_content.append(f"*Showing first 10 of {sql_row_count or len(sql_results)} rows*")
                        
                        markdown_content.append("")
            
            # Visualization Section
            if chart_url:
                markdown_content.append("## Data Visualization")
                if chart_title:
                    markdown_content.append(f"### {chart_title}")
                
                markdown_content.append(f"![Chart]({chart_url})")
                markdown_content.append(f" Chart URL: {chart_url}")
                markdown_content.append("")
                
                if chart_description:
                    markdown_content.append(f"**Chart Type:** {chart_type.title() if chart_type else 'Unknown'}")
                    markdown_content.append(f"**Description:** {chart_description}")
                    markdown_content.append("")
            
            # Key Insights
            if insights:
                markdown_content.append("## Key Insights")
                for i, insight in enumerate(insights, 1):
                    markdown_content.append(f"{i}. {insight}")
                markdown_content.append("")
            
            # Recommendations
            if recommendations:
                markdown_content.append("## Recommendations")
                for i, recommendation in enumerate(recommendations, 1):
                    markdown_content.append(f"{i}. {recommendation}")
                markdown_content.append("")
            
            # Footer
            markdown_content.append("---")
            markdown_content.append("*This report was generated automatically using AI-powered analysis.*")
            
            return "\n".join(markdown_content)
            
        except Exception as e:
            logger.error(f"Error generating markdown in ReportingRepository: {e}", exc_info=True)
            raise ReportingRepositoryError(f"Failed to generate markdown report: {e}")
    
    def analyze_data(
        self, 
        sql_results: List[Dict[str, Any]], 
        context: str
    ) -> Dict[str, Any]:
        """
        Analyze SQL results to extract insights.
        
        Args:
            sql_results: SQL query results
            context: Context about what the data represents
            
        Returns:
            Dictionary with analysis results
        """
        try:
            if not sql_results:
                return {
                    "insights": ["No data available for analysis"],
                    "summary": "No results returned from query",
                    "numeric_columns": [],
                    "row_count": 0
                }
            
            row_count = len(sql_results)
            columns = list(sql_results[0].keys()) if sql_results else []
            
            # Basic statistical analysis
            numeric_columns = []
            for col in columns:
                try:
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
            
            summary = f"Analysis of {row_count} records with focus on {context}" if context else f"Analysis of {row_count} records"
            
            return {
                "insights": insights,
                "summary": summary,
                "numeric_columns": numeric_columns,
                "row_count": row_count
            }
            
        except Exception as e:
            logger.error(f"Error analyzing data in ReportingRepository: {e}", exc_info=True)
            raise ReportingRepositoryError(f"Failed to analyze SQL results: {e}")