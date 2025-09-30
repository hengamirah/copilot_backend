from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import time
from datetime import datetime
from src.agents.dto.internal.database import DatabaseQueryRequestDTO, QueryResultDTO, QueryResultRowDTO
from src.agents.dto.response import ResponseDTO, ErrorDTO, ErrorType, ResponseStatus

class HistorianDatabaseRepository:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def execute_query(self, request: DatabaseQueryRequestDTO) -> ResponseDTO[QueryResultDTO]:
        start_time = time.time()
        
        with self._get_session() as session:
            try:
                stmt = text(request.query)
                # Execute the query and store the result object
                result = session.execute(stmt, request.parameters)
                
                # Get column names using the result object's keys() method
                column_names = result.keys()
                
                # Now fetch all rows
                rows_data = result.fetchall()
                
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Convert the Row objects to QueryResultRowDTO
                if rows_data:
                    rows = [
                        QueryResultRowDTO(data=dict(zip(column_names, row))) 
                        for row in rows_data
                    ]
                else:
                    rows = []
                
                query_result = QueryResultDTO(
                    rows=rows,
                    row_count=len(rows),
                    execution_time_ms=execution_time
                )
                
                return ResponseDTO.success(
                    data=query_result,
                    metadata={
                        "query": request.query,
                        "parameter_count": len(request.parameters) if request.parameters else 0
                    }
                )
                
            except Exception as e:
                error = ErrorDTO(
                    type=ErrorType.DATABASE_ERROR,
                    message=f"Database query failed: {str(e)}",
                    details={
                        "query": request.query,
                        "parameters": request.parameters,
                        "error_type": type(e).__name__
                    },
                    timestamp=datetime.utcnow().isoformat()
                )
                return ResponseDTO(status=ResponseStatus.ERROR, error=error, metadata={"query": request.query})