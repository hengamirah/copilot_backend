from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.agents.dto.internal.example import ExampleQueryRequestDTO, ExampleQueryResultDTO
from typing import Dict, Any
from src.agents.utils.utils import list_json_files_pathlib, parse_json_file_to_dict
from src.core.errors import ExampleRepositoryError


class VectorDatabaseRepository:

    def __init__(self):
    #     self.engine = create_engine(connection_string)
    #     self.SessionLocal = sessionmaker(bind=self.engine)
        pass

    # def _get_session(self) -> Session:
    #     return self.SessionLocal()

    # def save_example_data(self, data) -> str:
    #     pass 

    def get_example_data(self, request: str) -> Dict[str, Any]:
        # Add service-level validation if needed
        try:
            all_configs: Dict[str, Dict[str, Any]] = self._process_all_configs()
            return list(all_configs.values())
                
        except Exception as e:
            raise ExampleRepositoryError(f"Search repository failed to execute search: {e}")

    def _process_all_configs(self, directory_path: str = './src/agents/config/examples' ) -> Dict[str, Dict[str, Any]]:
        """
        Finds all JSON files in a directory and parses each one, 
        storing them in a single dictionary keyed by file name (without extension).
        """
        # 1. Find all JSON files in the specified directory
        json_paths = list_json_files_pathlib(directory_path)
        
        all_configs = {}
        
        print(f"Found {len(json_paths)} JSON files in '{directory_path}'.")
        
        # 2. Iterate over the found paths and parse each file
        for path in json_paths:
            # The path object allows easy access to the name without the extension
            config_name = path.stem 
            
            # Call the parsing function with the Path object
            data = parse_json_file_to_dict(path)
            
            # Store the resulting dictionary
            if data:
                all_configs[config_name] = data
                print(f"  -> Successfully parsed: {path.name}")
            else:
                print(f"  -> Skipping file due to error: {path.name}")
                
        return all_configs

