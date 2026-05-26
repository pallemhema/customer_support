from rag.retriever import get_retriever

from langchain_core.tools import tool

from schemas.retriever_schema import (
    RetrieveDocsInput
)

from tools.tool_retry import tool_with_retry


@tool(args_schema=RetrieveDocsInput)
def retrieve_docs(
    query: str,
    k: int = 3
):
    """
    Retrieve relevant documents from
    the RAG knowledge base.

    Searches semantic vectors and
    returns relevant support content.

    Sources:

        FAQ documents

        Policies

        Manuals

        Support KB

    Args:

        query:
            Customer issue/query.

        k:
            Number of documents.

            Default:
            3

    Returns:

        status:
            SUCCESS / NOT_FOUND / FAILED

        data:

            content

            metadata

            source info
    """

    try:

        retriever = tool_with_retry(
            get_retriever
        )

        docs = tool_with_retry(
            retriever.invoke,
            query
        )

        if not docs:

            return {

                "status":
                "NOT_FOUND",

                "query":
                query
            }

        context = []

        for d in docs[:k]:

            context.append({

                "content":
                d.page_content,

                "metadata":
                d.metadata
            })

        return {

            "status":
            "SUCCESS",

            "data":
            context
        }

    except Exception:

        return {

            "status":
            "FAILED",

            "message":
            "Knowledge retrieval unavailable"
        }