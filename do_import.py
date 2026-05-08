#!/usr/bin/env python3
"""Import kb_complete.json into Qdrant."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genshin_search_service import get_embedding
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

QDRANT_HOST = 'localhost'
QDRANT_PORT = 6333
COLLECTION = 'genshin_kb'

qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

data_file = sys.argv[1] if len(sys.argv) > 1 else 'knowledge_data/kb_complete.json'
with open(data_file) as f:
    items = json.load(f)

print(f'📄 Loading {len(items)} items from {data_file}')

# Recreate collection
qdrant.recreate_collection(
    COLLECTION,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

# Import
points = []
errors = []
for i, item in enumerate(items):
    try:
        vec = get_embedding(item['content'])
        points.append(PointStruct(
            id=abs(hash(item['type'] + item['title'] + item['content'][:100])) % (2**63),
            vector=vec,
            payload={
                'type': item['type'],
                'title': item['title'],
                'content': item['content'],
                'source': item.get('source', ''),
                'metadata': item.get('metadata', {}),
            },
        ))
        if (i + 1) % 5 == 0 or i == len(items) - 1:
            sys.stdout.write(f'  ⏳ {i+1}/{len(items)} embedded...\r')
            sys.stdout.flush()
    except Exception as e:
        errors.append({'index': i, 'title': item['title'], 'error': str(e)})
        print(f'\n  ❌ {item["title"]}: {e}')

print()
if points:
    # Upsert in batches
    batch_size = 100
    for j in range(0, len(points), batch_size):
        qdrant.upsert(COLLECTION, points=points[j:j+batch_size])
        print(f'  📦 batch {j//batch_size+1}/{(len(points)+batch_size-1)//batch_size} upserted')

print(f'\n✅ Imported: {len(points)} documents')
if errors:
    print(f'⚠️  Errors: {len(errors)}')

count = qdrant.count(COLLECTION).count
print(f'📊 Collection count: {count} vectors')
