import os
from langchain_astradb import AstraDBVectorStore
from product_assistant.utils.config_loader import load_config
from product_assistant.utils.model_loder import ModelLoader
from product_assistant.exception import ProductAssistantException
from product_assistant.logger import GLOBAL_LOGGER as log
from dotenv import load_dotenv
from product_assistant.utils.db_connector import load_env_variables

class Retriever:

    def __init__(self):
        self.env_vars=load_env_variables()
        self.config=load_config()
        self.model_loader=ModelLoader()
        self.vsstore=None

    def load_retriver(self):
        try:
            self.vstore = AstraDBVectorStore(
                embedding=self.model_loader.embedding_model(),
                collection_name=self.config["astra_db"]["collection_name"],
                api_endpoint=self.env_vars["astra_db_api_endpoint"],
                token=self.env_vars["astra_db_application_token"],
                namespace=self.env_vars["astra_db_keyspace"]
            )
            log.info("AstraDB Vector Store initialized successfully.")
            top_k = self.config["retriever"]["top_k"] if "retriever" in self.config else 3
            retriever=self.vstore.as_retriever(search_kwargs={"k": top_k})
            return retriever
        except Exception as e:  
            log.error(f"Error initializing AstraDB Vector Store: {str(e)}")
            raise ProductAssistantException(f"Error initializing AstraDB Vector Store: {str(e)}")
        
    def call_retriever(self,query):
        retriever=self.load_retriver()
        output=retriever.invoke(query)
        return output
    
if __name__=='__main__':
    retriever_obj = Retriever()
    user_query = "how is reviews feedback for dell laptop?"
    results = retriever_obj.call_retriever(user_query)

    for idx, doc in enumerate(results, 1):
        print(f"Result {idx}: {doc.page_content}\nMetadata: {doc.metadata}\n")



