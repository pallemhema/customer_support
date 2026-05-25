import json
from evaluation.ragas_eval import evaluate_example, evaluate_dataset, load_dataset


def test_ragas_eval_example_metrics():
    example = {
        "query": "Where is ord001?",
        "retrieved_docs": "Order ord001 is out for delivery.",
        "response": "Order ord001 is out for delivery.",
        "ground_truth": "Order ord001 is out for delivery.",
        "noise": "Payment was successful."
    }
    metrics = evaluate_example(example)
    assert metrics["faithfulness"] == 1.0
    assert metrics["context_recall"] == 1.0
    assert metrics["noise_sensitivity"] == 1.0


def test_ragas_eval_dataset_loads():
    dataset = load_dataset("evaluation_dataset.json")
    assert isinstance(dataset, list)
    assert len(dataset) >= 1


def test_ragas_eval_dataset_summary():
    dataset = [
        {
            "query": "Hello",
            "retrieved_docs": "Doc.",
            "response": "Doc.",
            "ground_truth": "Doc.",
            "noise": "Noise."
        }
    ]
    output = evaluate_dataset(dataset)
    assert output["summary"]["faithfulness"] == 1.0
    assert output["results"][0]["answer_relevancy"] >= 0.0
