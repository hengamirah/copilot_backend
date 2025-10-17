from src.core.interface import VannaRepositoryProtocol
from datetime import datetime
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

# Updated Service Implementation
class VannaService:
    def __init__(self, repository: VannaRepositoryProtocol):
        self.repository = repository
    
    def generate_sql(self, request: QueryRequestDTO) -> ResponseDTO[GenerateSQLResultDTO]:
        # Add service-level validation if needed
        if not request.question.strip():
            error = ErrorDTO(
                type=ErrorType.VALIDATION_ERROR,
                message="Question cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        # Forward to repository

        sql_code = self.repository.generate_sql(question=request.question, allow_llm_to_see_data = request.allow_llm_to_see_data)
        return ResponseDTO(status=ResponseStatus.SUCCESS,data=GenerateSQLResultDTO(result=sql_code))


    def run_sql(self, request: RunSQLRequestDTO) -> ResponseDTO[RunSQLResultDTO]:
        # Add service-level validation if needed
        if not request.sql.strip():
            error = ErrorDTO(
                type=ErrorType.VALIDATION_ERROR,
                message="SQL query cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        # Forward to repository
        sql_result = self.repository.run_sql(sql=request.sql) 
        return ResponseDTO(status=ResponseStatus.SUCCESS,data=RunSQLResultDTO(result=sql_result))

    def generate_plotly_code(self, request: GeneratePlotlyCodeRequestDTO) -> ResponseDTO[GeneratePlotlyCodeResultDTO]:
        if not request.sql.strip():
            error = ErrorDTO(
                type=ErrorType.VALIDATION_ERROR,
                message="SQL query cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        if not request.question.strip():
            error = ErrorDTO(
                type=ErrorType.VALIDATION_ERROR,
                message="Question cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        plotly_result = self.repository.generate_plotly_code(question = request.question, sql = request.sql, df_metadata = request.df_metadata)
        return ResponseDTO(status=ResponseStatus.SUCCESS,data=GeneratePlotlyCodeResultDTO(result=plotly_result))

    def get_plotly_figure(self, request: GetPlotlyFigureRequestDTO) -> ResponseDTO[GetPlotlyFigureResultDTO]:
        if not request.plotly_code.strip():
            error = ErrorDTO(
                type=ErrorType.VALIDATION_ERROR,
                message="plotly_code cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        if request.df.empty:
            error = ErrorDTO(
                type=ErrorType.VALIDATION_ERROR,
                message="df cannot be empty",
                timestamp=datetime.utcnow().isoformat()
            )
            return ResponseDTO.error(error)
        
        fig = self.repository.get_plotly_figure(plotly_code=request.plotly_code, df=request.df, dark_mode=request.dark_mode)
        return ResponseDTO(status=ResponseStatus.SUCCESS,data=GetPlotlyFigureResultDTO(result=fig))

