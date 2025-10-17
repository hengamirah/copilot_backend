from src.core.interface import VannaServiceProtocol
from typing import Dict, Any, Optional, List
from google.adk.tools import ToolContext
from google.genai import types
from plotly.graph_objs import Figure
from datetime import datetime
import uuid
import pandas as pd

from src.agents.dto.internal.database import (
    QueryRequestDTO,
    RunSQLRequestDTO, 
    GeneratePlotlyCodeRequestDTO,
    GetPlotlyFigureRequestDTO,
    GenerateSQLResultDTO,
    RunSQLResultDTO,
    GeneratePlotlyCodeResultDTO,
    GetPlotlyFigureResultDTO
)

from src.agents.dto.response import ResponseDTO, ErrorDTO, ErrorType, ResponseStatus


class VannaConversationTracker:
    """
    Tracks the complete workflow for each user question.
    Each question creates a new entry with all 4 tool outputs.
    """
    
    STATE_KEY = "vanna_conversations"
    
    @staticmethod
    def initialize(tool_context: ToolContext) -> None:
        """Initialize conversation tracking in state."""
        if VannaConversationTracker.STATE_KEY not in tool_context.state:
            tool_context.state[VannaConversationTracker.STATE_KEY] = {
                "conversations": {},  # Dict of all question workflows
                "current_id": None    # ID of current active conversation
            }
    
    @staticmethod
    def start_new_conversation(tool_context: ToolContext, question: str) -> str:
        """
        Start tracking a new question. Returns conversation ID.
        
        Returns:
            str: Unique conversation ID
        """
        VannaConversationTracker.initialize(tool_context)
        
        conversation_id = str(uuid.uuid4())[:8]
        conversation = {
            "id": conversation_id,
            "question": question,
            "timestamp": datetime.utcnow().isoformat(),
            "artifact": None,
            "steps": {
                "1_sql_generated": None,
                "2_sql_executed": None,
                "3_plot_code_generated": None,
                "4_figure_created": None
            }
        }
        
        state = tool_context.state[VannaConversationTracker.STATE_KEY]
        state["conversations"][conversation_id] = conversation
        state["current_id"] = conversation_id

        tool_context.state[VannaConversationTracker.STATE_KEY] = state
        
        return conversation_id
    
    @staticmethod
    def get_current_conversation(tool_context: ToolContext) -> Optional[Dict]:
        """Get the current active conversation."""
        VannaConversationTracker.initialize(tool_context)
        state = tool_context.state[VannaConversationTracker.STATE_KEY]
        
        current_id = state.get("current_id")
        if not current_id:
            return None
        
        if current_id in state["conversations"]:
            return state["conversations"][current_id]
        
        return None
    
    @staticmethod
    def get_conversation_by_id(tool_context: ToolContext, conv_id: str) -> Optional[Dict]:
        """Get a specific conversation by ID."""
        VannaConversationTracker.initialize(tool_context)
        state = tool_context.state[VannaConversationTracker.STATE_KEY]
        return state["conversations"].get(conv_id)
    
    @staticmethod
    def update_step(tool_context: ToolContext, step_name: str, data: Any, conversation_id: Optional[str] = None) -> None:
        """
        Update a specific step in a conversation.
        
        Args:
            tool_context: The tool context
            step_name: Name of the step to update
            data: Data to store in the step
            conversation_id: Optional specific conversation ID. If None, uses current conversation.
        """
        # Get the full state first
        state = tool_context.state.get(VannaConversationTracker.STATE_KEY)
        if not state:
            print(f"[WARNING] No state found to update step '{step_name}'")
            return
        
        # Get the conversation to update
        if conversation_id:
            conversation = state["conversations"].get(conversation_id)
        else:
            current_id = state.get("current_id")
            conversation = state["conversations"].get(current_id) if current_id else None
        
        if conversation:
            # Update the step
            conversation["steps"][step_name] = data
            
            # Update the conversation in the state
            state["conversations"][conversation['id']] = conversation
            
            # CRITICAL: Reassign the entire state dict to trigger save (Google ADK bug workaround)
            tool_context.state[VannaConversationTracker.STATE_KEY] = state
            
            # Debug logging
            print(f"[DEBUG] Updated step '{step_name}' for conversation {conversation['id']}")
        else:
            print(f"[WARNING] No conversation found to update step '{step_name}'")
    

    @staticmethod
    def get_all_conversations(tool_context: ToolContext) -> Dict[str, Dict]:
        """Get all conversations in this session."""
        VannaConversationTracker.initialize(tool_context)
        return tool_context.state[VannaConversationTracker.STATE_KEY]["conversations"]


class VannaTool:
    """
    Tool wrapper for Vanna AI with conversation tracking.
    Tracks the complete workflow: Question → SQL → Results → Plot → Figure
    """
    
    def __init__(self, service: VannaServiceProtocol):
        self.service = service

    def generate_sql_query(
        self, 
        tool_context: ToolContext, 
        question: str, 
        allow_llm_to_see_data: bool = False
    ) -> str:
        """
        Step 1: Generate SQL from question.
        Always creates a new conversation entry.
        """
        # Always start a new conversation for each question
        conv_id = VannaConversationTracker.start_new_conversation(tool_context, question)
        print(f"[DEBUG] Started new conversation {conv_id}")

        # Create request DTO
        request = QueryRequestDTO(
            question=question, 
            allow_llm_to_see_data=allow_llm_to_see_data
        )
        
        # Call service
        response = self.service.generate_sql(request)
        
        # Handle response
        if response.success and response.data:
            sql = response.data.result
            
            # Save to conversation tracking with explicit conversation_id
            VannaConversationTracker.update_step(
                tool_context, 
                "1_sql_generated", 
                {"sql": sql, "timestamp": datetime.utcnow().isoformat()},
                conversation_id=conv_id
            )
            
            return f"[Conversation {conv_id}]\n\nGenerated SQL query:\n\n```sql\n{sql}\n```\n\nUse `execute_sql_query` to run this query."
        else:
            return f"Error executing SQL: {response}"
                
    def execute_sql_query(self, tool_context: ToolContext, sql: str) -> str:
        """
        Step 2: Execute the SQL query.
        Updates current conversation with results.
        """
        try:
            # Get current conversation
            current_conv = VannaConversationTracker.get_current_conversation(tool_context)
            if not current_conv:
                return "Error: No active conversation. Please generate SQL first using `generate_sql_query`."
            
            conv_id = current_conv['id']
            print(f"[DEBUG] Executing SQL for conversation {conv_id}")
            
            # Create request DTO
            request = RunSQLRequestDTO(sql=sql)
            
            # Call service
            response = self.service.run_sql(request)
            
            if response.data.result is not None:
                df = response.data.result
                
                # Save to conversation tracking with explicit conversation_id
                VannaConversationTracker.update_step(
                    tool_context,
                    "2_sql_executed",
                    {
                        "sql": sql,
                        "df": df.to_json(),
                        "row_count": len(df),
                        "columns": df.columns.tolist(),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    conversation_id=conv_id
                )
                
                # Format response
                result_str = f"[Conversation {conv_id}]\n\n"
                result_str += f"Query executed successfully!\n\n"
                result_str += f"Rows returned: {len(df)}\n"
                result_str += f"Columns: {', '.join(df.columns.tolist())}\n\n"
                result_str += f"Preview (first 10 rows):\n{df.head(10).to_string()}"
                
                return result_str
            else:
                return f"Error executing SQL: {response}"
                
        except Exception as e:
            return f"Error executing SQL query: {str(e)}\n\nSQL Query:\n{sql}"

    def generate_plot_code(
        self, 
        tool_context: ToolContext, 
        question: str, 
        sql: str
    ) -> str:
        """
        Step 3: Generate Plotly visualization code.
        Updates current conversation with plot code.
        """
        # Get current conversation
        current_conv = VannaConversationTracker.get_current_conversation(tool_context)
        if not current_conv:
            return "Error: No active conversation. Please execute SQL first using `execute_sql_query`."
        
        conv_id = current_conv['id']
        print(f"[DEBUG] Generating plot code for conversation {conv_id}")
        
        # Verify SQL was executed
        if current_conv['steps']['2_sql_executed'] is None:
            return "Error: SQL must be executed before generating plot code. Use `execute_sql_query` first."
        
        # Create request DTO
        request = GeneratePlotlyCodeRequestDTO(question=question, sql=sql)
        
        # Call service
        response = self.service.generate_plotly_code(request)
        
        if response.success and response.data:
            plot_code = response.data.result
            
            # Save to conversation tracking with explicit conversation_id
            VannaConversationTracker.update_step(
                tool_context,
                "3_plot_code_generated",
                {
                    "plot_code": plot_code,
                    "question": question,
                    "sql": sql,
                    "timestamp": datetime.utcnow().isoformat()
                },
                conversation_id=conv_id
            )
            
            return f"[Conversation {conv_id}]\n\nGenerated Plotly code:\n\n```python\n{plot_code}\n```\n\nUse `create_plotly_figure` to generate the chart."
        else:
            error_msg = response.error.message if response.error else "Unknown error"
            return f"Error generating plot code: {error_msg}"

    async def create_plotly_figure(
        self,
        tool_context: ToolContext,
        plotly_code: str, 
        sql: str
    ) -> str:
        """
        Step 4: Create and save the Plotly figure.
        Completes the conversation workflow.
        """
        # Get current conversation
        current_conv = VannaConversationTracker.get_current_conversation(tool_context)
        if not current_conv:
            return "Error: No active conversation. Please complete previous steps first."
        
        conv_id = current_conv['id']
        print(f"[DEBUG] Creating figure for conversation {conv_id}")
        
        # Verify previous steps were completed
        if current_conv['steps']['2_sql_executed'] is None:
            return "Error: SQL must be executed before creating figure. Use `execute_sql_query` first."
        
        if current_conv['steps']['3_plot_code_generated'] is None:
            return "Error: Plot code must be generated before creating figure. Use `generate_plot_code` first."
        
        try:
            # Get the data from the conversation state
            df_json = current_conv['steps']['2_sql_executed']['df']
            df = pd.read_json(df_json)
            
            # Create figure request
            fig_request = GetPlotlyFigureRequestDTO(
                plotly_code=plotly_code, 
                df=df, 
                dark_mode=True
            )
            
            # Generate figure
            fig_response = self.service.get_plotly_figure(fig_request)
            
            if not fig_response.success or not fig_response.data:
                error_msg = fig_response.error if fig_response.error else "Failed to create figure"
                return f"Error: {error_msg}"
            
            fig: Figure = fig_response.data.result
            
            # Convert to HTML
            html_string = fig.to_html()
            html_artifact = types.Part.from_bytes(
                data=html_string.encode('utf-8'),
                mime_type="text/html"
            )
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chart_{conv_id}_{timestamp}.html"
            
            # Update artifact in conversation
            current_conv['artifact'] = filename
            
            # Save artifact
            version = await tool_context.save_artifact(
                filename=filename, 
                artifact=html_artifact
            )
            
            # Save to conversation tracking with explicit conversation_id - COMPLETE
            VannaConversationTracker.update_step(
                tool_context,
                "4_figure_created",
                {
                    "filename": filename,
                    "version": version,
                    "timestamp": timestamp,
                    "sql_used": sql
                },
                conversation_id=conv_id
            )
            
            return f"✅ [Conversation {conv_id}] Chart created and saved as artifact '{filename}' (version {version})."
            
        except Exception as e:
            return f"Error generating figure: {str(e)}\n\nPlease check the query and plot code."