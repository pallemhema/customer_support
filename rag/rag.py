from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# PDF folder
PDF_PATH = "data/pdfs"

# Load PDFs
loader = PyPDFDirectoryLoader(PDF_PATH)

documents = loader.load()

print(f"Loaded docs: {len(documents)}")

# Split documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(
    documents
)

print(f"Chunks created: {len(chunks)}")

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Vector store path
BASE_DIR = Path(__file__).parent

VECTOR_PATH = BASE_DIR / "vector_store"

# Create FAISS DB
vector_db = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)

# Save locally
vector_db.save_local(
    str(VECTOR_PATH)
)

print("RAG CREATED")