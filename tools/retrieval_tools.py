from rag.retriever import get_retriever


from langchain_core.tools import tool
from schemas.retriever_schema import RetrieveChatHistoryInput, RetrieveDocsInput, RetrieveTicketHistoryInput, SimilarIssueSearchInput


@tool(args_schema=RetrieveDocsInput)
def retrieve_docs(query:str, k:int=3):

    """
Retrieve relevant documents from the RAG knowledge base.

Searches the vector database using semantic
similarity and returns the most relevant
documents for the customer query.

Knowledge sources:
    FAQ documents

    Policies

    Manuals

    Support knowledge base

Args:
    query (str):
        Customer question or issue.

    k (int):
        Number of documents to retrieve.

        Default:
        3

Returns:
    list:
        Retrieved documents containing:

        - content
        - metadata

Used By:
    Retrieval Agent
    Response Agent
"""
    retriever = get_retriever()
    print(f"Retrieving documents for query: {query}")
    docs = retriever.invoke(query, k=k)
    print(f"Retrieved {len(docs)} documents")

    context = []

    for d in docs:

        context.append(
            {
                "content": d.page_content,
                "source": d.metadata
            }
        )
    print(f"Formatted context: {context}")

    return context


