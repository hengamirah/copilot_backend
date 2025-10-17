from src.core.config import COMPLEX_GEMINI_MODEL, API_KEY
from vanna.chromadb import ChromaDB_VectorStore
from vanna.google import GoogleGeminiChat
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.agents.dto.response import ResponseDTO, ErrorDTO, ErrorType

class CustomVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(
            self, 
            config=config
        )
        GoogleGeminiChat.__init__(
            self, 
            config={
                'api_key': API_KEY, 
                'model_name': COMPLEX_GEMINI_MODEL
            }
        )

    #KIV custom implementation
    def generate_query_explanation(self, sql: str):
        my_prompt = [
            self.system_message("You are a helpful assistant that will explain a SQL query"),
            self.user_message("Explain this SQL query: " + sql),
        ]
        return self.submit_prompt(prompt=my_prompt)

class VannaRepository:    
    def __init__(self, vanna_model: CustomVanna):
        self.vanna_model = vanna_model

    def generate_sql(self, question: str, allow_llm_to_see_data: bool = False) -> str:
        return self.vanna_model.generate_sql(question=question, allow_llm_to_see_data=allow_llm_to_see_data)

    def run_sql(self, sql: str) -> DataFrame:
        return self.vanna_model.run_sql(sql=sql)

    def generate_plotly_code(self, question: str, sql: str, df_metadata: str = None) -> str:
        return self.vanna_model.generate_plotly_code(question=question, sql=sql, df_metadata=df_metadata)

    def get_plotly_figure(self, plotly_code: str, df: DataFrame, dark_mode: bool)-> Figure:
        return self.vanna_model.get_plotly_figure(plotly_code=plotly_code, df=df, dark_mode=dark_mode)

