from types import SimpleNamespace
from workflows.retriever import retrieval_node
from workflows.reponse import response_node


def test_rag_pipeline(monkeypatch):
    monkeypatch.setattr("workflows.retriever.retrieval_agent.invoke", lambda payload: {"messages": [SimpleNamespace(content="Relevant support doc.") ]})

    def fake_stream(payload, stream_mode=None):
        yield (type("Chunk", (), {"content": "Final response based on retrieved docs."}), None)

    monkeypatch.setattr("workflows.reponse.response_agent.stream", fake_stream)

    state = {"query": "What is the delivery status?", "resolved_query": "What is the delivery status?", "intent": "delivery_issue"}
    retrieval_result = retrieval_node(state)
    state.update(retrieval_result)
    response_result = response_node(state)

    assert state["retrieved_docs"] == "Relevant support doc."
    assert "Final response based on retrieved docs." in response_result["response"]
