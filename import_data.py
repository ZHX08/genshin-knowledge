#!/usr/bin/env python3
"""
导入知识库数据到 Qdrant。
用法：python3 import_data.py [data.json]
"""
import sys, json, os

sys.path.insert(0, os.path.dirname(__file__))
from genshin_search_service import get_embedding
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = "genshin_kb"

qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

data_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "knowledge_data.json")

with open(data_file) as f:
    items = json.load(f)

print(f"📄 Loading {len(items)} items from {data_file}")

# Build collection
from qdrant_client.models import VectorParams, Distance
qdrant.recreate_collection(
    COLLECTION,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

# Import with progress
points = []
errors = []
for i, item in enumerate(items):
    try:
        vec = get_embedding(item["content"])
        points.append(PointStruct(
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
        if (i + 1) % 5 == 0 or i == len(items) - 1:
            print(f"  ⏳ {i+1}/{len(items)} embedded...")
    except Exception as e:
        errors.append({"index": i, "title": item["title"], "error": str(e)})
        print(f"  ❌ {item['title']}: {e}")

if points:
    qdrant.upsert(COLLECTION, points=points)

print(f"\n✅ Imported: {len(points)} documents")
if errors:
    print(f"⚠️  Errors: {len(errors)}")

# Verify
count = qdrant.count(COLLECTION).count
print(f"📊 Collection count: {count} vectors")
