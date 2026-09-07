import os
import glob
import logging
from dotenv import load_dotenv


# Document loaders and splitters
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Azure components
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch


load_dotenv(override=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("indexer")

def index_docs():
    '''
    Reads The PDF, Chunks, And upload them to Azure AI Search
    '''

    # Defining the path to the data folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, "../../backend/data")

    # Checking environment variables
    logger.info("=" * 60)
    logger.info("Environment Configuration Check:")
    logger.info(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"Embedding Deployment: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-small')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT: {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("=" * 60)
        
    # Validating Required Environment Variables
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        return


    # Initializing the embedding model 
    try:
        logger.info("Initializing Azure OpenAI Embeddings...")
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )
        logger.info("Embeddings model initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings model: {str(e)}")
        logger.error('Please verify your Azure deployment name and base url')
        return

    # Initializing the vector store
    try:
        logger.info("Initializing Azure Search Vector Store...")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=index_name,
            embedding_function=embeddings.embed_query
        )
        logger.info(f" Vector store initialized for index: {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Search: {str(e)}")
        logger.error("Please verify your Azure Search endpoint, API key, and index name.")
        return

    # Finding all PDF files in the data folder
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {data_folder}. Please add files")
    logger.info(f"Found {len(pdf_files)} PDFs to process : {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []


    # Processing each PDF file
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading : {os.path.basename(pdf_path)} ......")
            loader = PyMuPDFLoader(pdf_path)
            raw_docs = loader.load()


            # Chunking strategy
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(raw_docs)
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)
            all_splits.extend(splits)
            logger.info(f"Split into {len(splits)} chunks.")
        except Exception as e:
            logger.error(f"failed to process {pdf_path} : {str(e)}")

        # Uploading to Azure Search
        if all_splits:
            logger.info(f"Uploading {len(all_splits)} chunks to Azure AI Search Index '{os.getenv("AZURE_SEARCH_INDEX_NAME")}'")
            try:
                # Azure search accepts batches automatically through this method
                vector_store.add_documents(documents=all_splits)
                logger.info("="*60)
                logger.info("Indexing Complete! Knowledge Base is ready ....")
                logger.info(f"Total chunks indexed {len(all_splits)}")
                logger.info("="*60)
            except Exception as e:
                logger.error(f"Failed to upload the documents to Azure Search : {str(e)}")
                logger.error("please check the Azure search configuration and try again")
        else:
            logger.warning("No Documents were Processed.")



if __name__ == "__main__":
    index_docs()
