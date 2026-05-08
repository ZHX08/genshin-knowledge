#!/usr/bin/env python3
"""Fix import: upsert from all individual JSON files without recreate."""
import json, os, glob, sys, requests, time
from qdrant_client import QdrantClient, models

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = "genshin_kb"
EMBED_URL = "http://localhost:8080/embedding"

qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

if not qdrant.collection_exists(COLLECTION):
    print("Creating collection...")
    qdrant.create_collection(
        COLLECTION,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )
else:
    print(f"Collection '{COLLECTION}' exists ({qdrant.count(COLLECTION).count} vectors), will upsert")

json_files = sorted(glob.glob("knowledge_data/*.json"))
skip = {"kb_complete.json", "weapons_merged.json", "知识库完整合并.json"}
json_files = [f for f in json_files if os.path.basename(f) not in skip]
print(f"Files to import: {len(json_files)}")

all_items = []
for fpath in json_files:
    with open(fpath) as f:
        items = json.load(f)
    if isinstance(items, list):
        all_items.extend(items)
        print(f"  {os.path.basename(fpath)}: {len(items)} items")
    else:
        print(f"  {os.path.basename(fpath)}: SKIP (not a list)")

print(f"\nTotal items: {len(all_items)}")

def get_embedding(text: str) -> list[float]:
    r = requests.post(EMBED_URL, json={"content": text}, timeout=60)
    r.raise_for_status()
    data = r.json()
    if "embedding" in data:
        return data["embedding"]
    elif "data" in data and len(data["data"]) > 0:
        return data["data"][0]["embedding"]
    raise ValueError("Unexpected embedding response format")

points = []
errors = []
batch_size = 10
t0 = time.time()
for i, item in enumerate(all_items):
    try:
        vec = get_embedding(item["content"])
        points.append(models.PointStruct(
            id=abs(hash(item["type"] + item["title"] + item["content"][:100])) % (2**63),
            vector=vec,
            payload={
                "type": item["type"],
                "title": item["title"],
                "content": item["content"],
                "source": item.get("source", ""),
                "metadata": item.get("metadata", {}),
            },
        ))
    except Exception as e:
        errors.append({"index": i, "title": item.get("title", "?"), "error": str(e)})
    
    if len(points) >= batch_size or (i == len(all_items) - 1 and points):
        qdrant.upsert(COLLECTION, points=points)
        count = qdrant.count(COLLECTION).count
        elapsed = time.time() - t0
        print(f"  [{i+1}/{len(all_items)}] upserted batch → total: {count} ({elapsed:.0f}s)")
        points = []
    
    if (i + 1) % 5 == 0 and i > 0:
        elapsed = time.time() - t0
        remaining = elapsed / (i+1) * (len(all_items) - i - 1)
        print(f"  ⏳ {i+1}/{len(all_items)} ({elapsed:.0f}s / ~{remaining:.0f}s)")

elapsed = time.time() - t0
print(f"\n✅ Imported: {len(all_items) - len(errors)} documents in {elapsed:.0f}s")
if errors:
    print(f"⚠️  Errors ({len(errors)}):")
    for e in errors[:5]:
        print(f"  - {e['title']}: {e['error']}")

count = qdrant.count(COLLECTION).count
print(f"📊 Collection count: {count} vectors")
