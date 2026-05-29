from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyMuPDFLoader
)

from langchain_community.vectorstores import (
    FAISS
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

load_dotenv()

PDF_PATH = "data/pdfs"

all_documents = []

# Load all PDFs

for pdf_file in Path(
    PDF_PATH
).glob("*.pdf"):

    print(
        f"Loading: {pdf_file.name}"
    )

    loader = PyMuPDFLoader(
        str(pdf_file)
    )

    docs = loader.load()

    # metadata

    for doc in docs:

        doc.metadata[
            "source_file"
        ] = pdf_file.name

    all_documents.extend(
        docs
    )

print(
    f"Loaded docs: "f"{len(all_documents)}"
)

# Split

splitter = (
    RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
)

chunks = splitter.split_documents(
    all_documents
)

print(
    f"Chunks created: "
    f"{len(chunks)}"
)

# Embeddings

embeddings = (
    HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
)

# FAISS path

BASE_DIR = Path(__file__).parent

VECTOR_PATH = (BASE_DIR/ "vector_store")

# Create vector DB

vector_db = FAISS.from_documents(

    documents=chunks,

    embedding=embeddings
)

# Save locally

vector_db.save_local(
    str(VECTOR_PATH)
)

print("RAG CREATED")