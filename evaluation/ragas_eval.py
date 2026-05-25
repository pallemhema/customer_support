import csv
import html
import json
import os
import re
from typing import Dict, List

DATASET_FILE = os.path.join(os.path.dirname(__file__), "../evaluation_dataset.json")
CSV_FILE = os.path.join(os.path.dirname(__file__), "../reports/ragas_results.csv")
HTML_FILE = os.path.join(os.path.dirname(__file__), "../reports/ragas_results.html")


def normalize_text(text: str) -> List[str]:
    if not text:
        return []
    tokens = re.findall(r"\w+", text.lower())
    return tokens


def jaccard(a: List[str], b: List[str]) -> float:
    if not a or not b:
        return 0.0
    aset = set(a)
    bset = set(b)
    return len(aset & bset) / len(aset | bset)


def overlap(a: List[str], b: List[str]) -> float:
    if not a:
        return 0.0
    aset = set(a)
    bset = set(b)
    return len(aset & bset) / len(aset)


def evaluate_example(example: Dict) -> Dict:
    query_tokens = normalize_text(example.get("query", ""))
    doc_tokens = normalize_text(example.get("retrieved_docs", ""))
    response_tokens = normalize_text(example.get("response", ""))
    truth_tokens = normalize_text(example.get("ground_truth", ""))
    noise_tokens = normalize_text(example.get("noise", ""))

    results = {
        "faithfulness": overlap(response_tokens, doc_tokens),
        "answer_relevancy": jaccard(query_tokens + truth_tokens, response_tokens),
        "context_precision": overlap(response_tokens, doc_tokens),
        "context_recall": overlap(truth_tokens, response_tokens),
        "context_entity_recall": overlap(truth_tokens, response_tokens),
        "noise_sensitivity": 1 - overlap(response_tokens, noise_tokens),
    }

    for key, value in results.items():
        results[key] = round(value, 4)

    return results


def evaluate_dataset(dataset: List[Dict]) -> Dict:
    summaries = []
    records = []
    for example in dataset:
        metrics = evaluate_example(example)
        record = {"query": example.get("query", ""), **metrics}
        records.append(record)
        summaries.append(metrics)

    summary = {}
    if summaries:
        for key in summaries[0].keys():
            summary[key] = round(sum(m[key] for m in summaries) / len(summaries), 4)
    else:
        summary = {"faithfulness": 0, "answer_relevancy": 0, "context_precision": 0, "context_recall": 0, "context_entity_recall": 0, "noise_sensitivity": 0}

    return {
        "summary": summary,
        "results": records,
    }


def write_csv(records: List[Dict], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not records:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def write_html(records: List[Dict], summary: Dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    html_rows = ["<tr>" + "".join(f"<th>{html.escape(str(col))}</th>" for col in records[0].keys()) + "</tr>"]
    for row in records:
        html_rows.append("<tr>" + "".join(f"<td>{html.escape(str(row[col]))}</td>" for col in row.keys()) + "</tr>")

    summary_html = "<ul>" + "".join(f"<li>{html.escape(str(k))}: {html.escape(str(v))}</li>" for k, v in summary.items()) + "</ul>"
    body = f"<h1>RAGAS Evaluation Results</h1>\n{summary_html}\n<table>{''.join(html_rows)}</table>"
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


def load_dataset(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    dataset = load_dataset(DATASET_FILE)
    evaluation = evaluate_dataset(dataset)
    write_csv(evaluation["results"], CSV_FILE)
    write_html(evaluation["results"], evaluation["summary"], HTML_FILE)
    print("RAGAS evaluation completed")
    print(json.dumps(evaluation["summary"], indent=2))


if __name__ == "__main__":
    main()
