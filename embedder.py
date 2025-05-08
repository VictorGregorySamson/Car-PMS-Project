# utils/vector_stores.py

from langchain_openai import OpenAIEmbeddings
#from langchain.vectorstores import Chroma
from langchain_chroma import Chroma

# Initialize the embeddings only once.
embeddings = OpenAIEmbeddings()

# Initialize the vector store for invoices.
manual_vectorstore = Chroma(
    persist_directory="car_manuals_db",
    embedding_function=embeddings,
    collection_name="car_manuals"
)


