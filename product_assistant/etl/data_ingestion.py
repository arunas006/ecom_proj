import pandas as pd
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from product_assistant.utils.model_loder import ModelLoader
from product_assistant.exception import ProductAssistantException
from product_assistant.logger import GLOBAL_LOGGER as log
from product_assistant.utils.config_loader import load_config
from langchain_astradb import AstraDBVectorStore
from product_assistant.utils.db_connector import load_env_variables


class DataIngestion:

    def __init__(self):
        self.csv_path=self._get_csv_path()
        self.product_data=self._load_csv()
        self.env_vars=load_env_variables()
        self.model_loader=ModelLoader()
        self.config=load_config()

    def _get_csv_path(self):
        current_dir=os.getcwd()
        data_dir=os.path.join(current_dir,"data")
        csv_path=os.path.join(data_dir,"product_reviews.csv")
        if not os.path.exists(csv_path):
            log.error(f"CSV file not found at {csv_path}. Please run the scraper to generate the data.")
            raise ProductAssistantException(f"CSV file not found at {csv_path}. Please run the scraper to generate the data.")
        log.info(f"CSV file found at {csv_path}")
        return csv_path
    
    def _load_csv(self):
        try:
            df=pd.read_csv(self.csv_path)
            if df.empty:
                log.error("The CSV file is empty. Please run the scraper to generate data.")
                raise ProductAssistantException("The CSV file is empty. Please run the scraper to generate data.")
            log.info(f"Loaded {len(df)} records from the CSV file")
            expected_columns = {'product_id','product_title', 'rating', 'total_reviews','price', 'top_reviews'}
            if not expected_columns.issubset(set(df.columns)):
                missing_cols = expected_columns - set(df.columns)
                log.error(f"CSV file is missing required columns: {', '.join(missing_cols)}")
                raise ProductAssistantException(f"CSV file is missing required columns: {', '.join(missing_cols)}")
            return df
        except Exception as e:
            log.error(f"Error loading CSV file: {str(e)}")
            raise ProductAssistantException(f"Error loading CSV file: {str(e)}")

    

    def transform_data(self):
        try:
            docs=[Document(page_content=row["top_reviews"],
                           metadata={"source":"flipkart",
                                     **{k:row[k] for k in ["product_id",
                                                           "product_title",
                                                           "rating","total_reviews"]}
                    }) for row in self.product_data.to_dict(orient="records")]
            
            log.info(f"Created {len(docs)} Document objects from the data")

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            split_docs = []
            for doc in docs:
                splits = text_splitter.split_text(doc.page_content)
                for chunk in splits:
                    split_docs.append(Document(page_content=chunk, metadata=doc.metadata))
            log.info(f"Split documents into {len(split_docs)} chunks using text splitter")
            return split_docs
        except Exception as e:
            log.error(f"Error transforming data: {str(e)}")
            raise ProductAssistantException(f"Error transforming data: {str(e)}")
        
    def vector_db(self):
        collection_name=self.config['astra_db']['collection_name']
        try:
            vsstore=AstraDBVectorStore(
                embedding=self.model_loader.embedding_model(),
                api_endpoint=self.env_vars["astra_db_api_endpoint"],
                token=self.env_vars["astra_db_application_token"],
                namespace=self.env_vars["astra_db_keyspace"],
                collection_name=collection_name
            )
            log.info(f"Connected to AstraDB collection: {collection_name}")
            inserted_ids=vsstore.add_documents(self.transform_data())
            log.info(f"Inserted {len(inserted_ids)} documents into AstraDB collection: {collection_name}")
            return vsstore, inserted_ids
        except Exception as e:
            log.error(f"Error connecting to AstraDB or inserting documents: {str(e)}")
            raise ProductAssistantException(f"Error connecting to AstraDB or inserting documents: {str(e)}")
        

if __name__ == "__main__":
    ingestion=DataIngestion()
    docs=ingestion.transform_data()
    print(f"Transformed into {len(docs)} documents")
    vs, ids=ingestion.vector_db()
    print(f"Inserted {len(ids)} documents into AstraDB")
