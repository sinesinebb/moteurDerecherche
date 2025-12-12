#!/usr/bin/env python3
# scripts/benchmark_indexing.py
"""
Minimal benchmark tool for indexing speed (Elasticsearch Bulk API).
Sends batches of small documents and reports throughput and latencies.

Usage:
  python scripts/benchmark_indexing.py --es http://elasticsearch:9200 --index bench-idx --docs 1000 --batch 200
"""

from __future__ import annotations
import argparse
import time
import json
import random
import sys
from typing import List

try:
    import requests
except Exception:
    requests = None

def gen_doc(i: int, embedding_dim: int = 8) -> dict:
    return {
        "id": f"bench-{i}",
        "text": f"Benchmark document {i} random {random.randint(0,100000)}",
        "metadata": {"bench": True, "n": i},
        "embedding": [random.random() for _ in range(embedding_dim)],
    }

def send_bulk(es_host: str, index_name: str, docs: List[dict]) -> dict:
    if requests is None:
        raise RuntimeError("requests package required. pip install requests")
    bulk_lines = []
    for d in docs:
        action = {"index": {"_index": index_name, "_id": d.get("id")}}
        bulk_lines.append(json.dumps(action))
        bulk_lines.append(json.dumps(d))
    payload = "\n".join(bulk_lines) + "\n"
    url = es_host.rstrip("/") + "/_bulk"
    headers = {"Content-Type": "application/x-ndjson"}
    r = requests.post(url, headers=headers, data=payload, timeout=60)
    return {"status_code": r.status_code, "elapsed": r.elapsed.total_seconds(), "text": r.text[:200]}

def run_benchmark(es_host: str, index_name: str, total_docs: int, batch_size: int):
    batches = (total_docs + batch_size - 1) // batch_size
    timings = []
    sent = 0
    for b in range(batches):
        n = min(batch_size, total_docs - sent)
        docs = [gen_doc(sent + i) for i in range(n)]
        t0 = time.time()
        res = send_bulk(es_host, index_name, docs)
        t1 = time.time()
        elapsed = t1 - t0
        timings.append(elapsed)
        sent += n
        print(f"[{b+1}/{batches}] sent={sent} batch={n} elapsed={elapsed:.3f}s status={res.get('status_code')}")
        # small backoff
        time.sleep(0.1)
    total_time = sum(timings)
    print("=== BENCHMARK SUMMARY ===")
    print(f"Total docs: {total_docs}")
    print(f"Total time: {total_time:.3f}s")
    print(f"Throughput: {total_docs/total_time:.2f} docs/s")
    print(f"Avg batch time: {sum(timings)/len(timings):.3f}s (batches={len(timings)})")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--es", default="http://elasticsearch:9200", help="Elasticsearch host")
    p.add_argument("--index", default="bench-index", help="Index name (will be created implicitly)")
    p.add_argument("--docs", type=int, default=500, help="Total number of documents")
    p.add_argument("--batch", type=int, default=100, help="Batch size for Bulk API")
    args = p.parse_args()

    try:
        run_benchmark(args.es, args.index, args.docs, args.batch)
    except Exception as e:
        print("Error during benchmark:", e, file=sys.stderr)
        sys.exit(2)
