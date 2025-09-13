import os
from dotenv import load_dotenv
from product_assistant.exception import ProductAssistantException
from product_assistant.logger import GLOBAL_LOGGER as log
from product_assistant.utils.config_loader import load_config
from langchain_astradb import AstraDBVectorStore

def load_env_variables():
        Required_vars = ["GROQ_API_KEY","LANGCHAIN_API_KEY","GOOGLE_API_KEY","ASTRA_DB_API_ENDPOINT",
                         "ASTRA_DB_APPLICATION_TOKEN","ASTRA_DB_KEYSPACE"]
        
        load_dotenv()
        missing_vars = [var for var in Required_vars if os.getenv(var) is None]
        if missing_vars:
            log.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            raise ProductAssistantException(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return {
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "langchain_api_key": os.getenv("LANGCHAIN_API_KEY"),
        "google_api_key": os.getenv("GOOGLE_API_KEY"),
        "astra_db_api_endpoint": os.getenv("ASTRA_DB_API_ENDPOINT"),
        "astra_db_application_token": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        "astra_db_keyspace": os.getenv("ASTRA_DB_KEYSPACE"),
        }
