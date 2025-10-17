import time
from typing import Dict, Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.core import logger, DataAgentRepositoryError

class HistorianDatabaseRepository:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            with self._get_session() as session:
                stmt = text(query)
                # Execute the query and store the result object
                result = session.execute(stmt, parameters or {})
                
                # Get column names using the result object's keys() method
                column_names = result.keys()
                
                # Now fetch all rows
                rows_data = result.fetchall()
                
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                if rows_data:
                    rows = [
                        dict(zip(column_names, row))
                        for row in rows_data
                    ]
                else:
                    rows = []
                
                query_result = {
                    "rows": rows,
                    "row_count": len(rows),
                    "execution_time_ms": execution_time
                }
                
                return query_result
        
        except Exception as e:
            logger.error(f"An error occurred in HistorianDatabaseRepository.execute_query: {e}", exc_info=True)
            raise DataAgentRepositoryError(f"Database query execution failed: {e}")