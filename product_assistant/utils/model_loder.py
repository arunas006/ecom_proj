import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import sys
import json
from dotenv import load_dotenv
from product_assistant.logger import GLOBAL_LOGGER as log 
from product_assistant.utils.config_loader import load_config
from product_assistant.exception import ProductAssistantException
import asyncio

class API_Validation:

    REQQUIRED_KEYS = ["GROQ_API_KEY","GOOGLE_API_KEY"]

    def __init__(self):
        self.api_keys={}
        raw_keys=os.getenv("API_KEYS")

        if raw_keys:
            try:
                api_check=json.loads(raw_keys)
                if not isinstance(api_check,dict):
                    raise ProductAssistantException("API_KEYS environment variable must be a JSON object")
                self.api_keys=api_check
                log.info("API keys loaded from environment variable")
            except Exception as e:
                raise ProductAssistantException(f"API_KEYS environment variable is not valid JSON: {str(e)}")

        for key in self.REQQUIRED_KEYS:
            if key not in self.api_keys:
                env_value=os.getenv(key)
                if env_value:
                    self.api_keys[key]=env_value
                    log.info(f"Loaded {key} from Requirement variable")
        
        missing_keys=[key for key in self.REQQUIRED_KEYS if key not in self.api_keys]
        if missing_keys:
            raise ProductAssistantException(f"Missing required API keys: {', '.join(missing_keys)}")
        log.info("All required API keys are present")

    def get_api_keys(self,key:str)->str:
        val=self.api_keys.get(key)
        if not val:
            raise ProductAssistantException(f"API key for {key} not found")

        return val
    
class ModelLoader:

    def __init__(self):

        if os.getenv("ENV","LOCAL") != "PROD":
            load_dotenv()
            log.info("Loaded environment variables from .env file")
        else:
            log.info("Running in production mode, skipping .env loading")
    
        self.api_key_manager=API_Validation()
        self.config=load_config()
        log.info("yaml configuration file loaded successfully",config_keys=list(self.config.keys()))


    def embedding_model(self):
        try:
            model_name=self.config["embedding"]["model_name"]

            log.info(f"Loading embedding model: {model_name}")

            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())

            return  GoogleGenerativeAIEmbeddings(model=model_name,
                                                 google_api_key=self.api_key_manager.get_api_keys("GOOGLE_API_KEY"))
        except Exception as e:
            raise ProductAssistantException(f"Error loading embedding model: {str(e)}")
        
    def load_llm(self):
        try:
            llm_block=self.config["llm"]
            provider_key=os.getenv("LLM_PROVIDER","GOOGLE").lower()
            log.info(f"Loading LLM model: {llm_block} from provider: {provider_key}")

            if provider_key not in llm_block:
                log.error(f"LLM provider {provider_key} not found in model name {llm_block}, defaulting to GOOGLE")
                raise ProductAssistantException(f"LLM provider {provider_key} not found in model name {llm_block}")

            llm_config=llm_block.get(provider_key)
            provider=llm_config.get("provider")
            model_name=llm_config.get("model_name")
            temperature=llm_config.get("temperature",0.2)

            log.info(f"LLM configuration: provider={provider}, model_name={model_name}, temperature={temperature}") 
            
            if provider == "groq":
                return ChatGroq(model=model_name,
                                groq_api_key=self.api_key_manager.get_api_keys("GROQ_API_KEY"),
                                temperature=temperature,max_tokens=llm_config.get("max_tokens",1024))
            elif provider == "google":
                try:
                    asyncio.get_running_loop()
                except RuntimeError:
                    asyncio.set_event_loop(asyncio.new_event_loop())

                return ChatGoogleGenerativeAI(model=model_name,
                                              google_api_key=self.api_key_manager.get_api_keys("GOOGLE_API_KEY"),
                                              temperature=temperature,
                                              max_output_tokens=llm_config.get("max_output_tokens",1024))

            log.info(f"LLM model loaded successfully: {model_name}")
            
        except Exception as e:
            log.error(f"Error loading LLM model")
            raise ProductAssistantException(f"Error loading LLM model: {str(e)}")
        
if __name__ == "__main__":
    loader = ModelLoader()

    # Test Embedding
    embeddings = loader.embedding_model()
    print(f"Embedding Model Loaded: {embeddings}")
    result = embeddings.embed_query("Hello, how are you?")
    print(f"Embedding Result: {result}")

    # Test LLM
    llm = loader.load_llm()
    print(f"LLM Loaded: {llm}")
    result = llm.invoke("Hello, how are you?")
    print(f"LLM Result: {result.content}")