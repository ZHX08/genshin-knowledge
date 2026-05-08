#!/usr/bin/env python3
"""
原神知识库检索服务
依赖：llama-server (:8080) + Qdrant (:6333)
"""
import os, sys, json, textwrap
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter, FieldCondition, MatchValue,
    VectorParams, Distance, PointStruct,
)

# ── Config ────────────────────────────────────────────────────────────────
EMBED_URL = os.getenv("EMBED_URL", "http://localhost:8080/embedding")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = "genshin_kb"
EMBED_DIM = 768  # Gemma Embedding 300m

qdrant = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)
app = FastAPI(title="Genshin Knowledge Search")


# ── Schemas ───────────────────────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str
    type: str | None = None
    top_k: int = 5


class ImportRequest(BaseModel):
    type: str
    title: str
    content: str
    source: str = ""
    metadata: dict = {}


# ── Embedding ──────────────────────────────────────────────────────────────
def get_embedding(text: str) -> list[float]:
    """Call llama-server embedding endpoint."""
    try:
        r = requests.post(EMBED_URL, json={"content": text}, timeout=30)
        r.raise_for_status()
        data = r.json()
        # Handle both /embedding and /v1/embeddings response formats
        if "embedding" in data:
            return data["embedding"]
        elif "data" in data and len(data["data"]) > 0:
            return data["data"][0]["embedding"]
        raise ValueError("Unexpected embedding response format")
    except Exception as e:
        raise HTTPException(503, f"Embedding service error: {e}")


# ── Startup ────────────────────────────────────────────────────────────────
@app.on_event("startup")
def init():
    """Auto-create collection if not exists."""
    try:
        collections = qdrant.get_collections().collections
        if not any(c.name == COLLECTION for c in collections):
            qdrant.create_collection(
                COLLECTION,
                vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
            )
            print(f"✅ Created collection: {COLLECTION}")
    except Exception as e:
        print(f"⚠️  Qdrant init warning: {e}", file=sys.stderr)


# ── Endpoints ──────────────────────────────────────────────────────────────
@app.post("/search")
def search(req: SearchRequest):
    """Search knowledge base by semantic similarity."""
    vec = get_embedding(req.query)
    flt = None
    if req.type:
        flt = Filter(must=[FieldCondition(key="type", match=MatchValue(value=req.type))])
    hits = qdrant.query_points(COLLECTION, query=vec, query_filter=flt, limit=req.top_k).points
    return {
        "query": req.query,
        "type_filter": req.type,
        "results": [
            {
                "score": round(h.score, 4),
                "type": h.payload.get("type", ""),
                "title": h.payload.get("title", ""),
                "content": h.payload.get("content", "")[:500],
                "source": h.payload.get("source", ""),
                "metadata": h.payload.get("metadata", {}),
            }
            for h in hits
        ],
    }


@app.post("/import")
def import_data(req: ImportRequest):
    """Import a single document into the knowledge base."""
    vec = get_embedding(req.content)
    point = PointStruct(
        id=abs(hash(req.type + req.title + req.content[:100])) % (2**63),
        vector=vec,
        payload={
            "type": req.type,
            "title": req.title,
            "content": req.content,
            "source": req.source,
            "metadata": req.metadata,
        },
    )
    qdrant.upsert(COLLECTION, points=[point])
    return {"status": "ok", "title": req.title}


@app.post("/import_batch")
def import_batch(items: list[ImportRequest]):
    """Batch import multiple documents."""
    points = []
    errors = []
    for i, item in enumerate(items):
        try:
            vec = get_embedding(item.content)
            points.append(PointStruct(
                id=abs(hash(item.type + item.title + item.content[:100])) % (2**63),
                vector=vec,
                payload={
                    "type": item.type,
                    "title": item.title,
                    "content": item.content,
                    "source": item.source,
                    "metadata": item.metadata,
                },
            ))
        except Exception as e:
            errors.append({"index": i, "title": item.title, "error": str(e)})
    if points:
        qdrant.upsert(COLLECTION, points=points)
    return {"imported": len(points), "errors": len(errors), "error_details": errors}


@app.post("/rebuild")
def rebuild_from_file(file_path: str = "/root/.openclaw-zhx/workspace/projects/genshin-knowledge/knowledge_data.json"):
    """Drop and rebuild the collection from a JSON data file."""
    with open(file_path) as f:
        items = json.load(f)
    qdrant.recreate_collection(
        COLLECTION,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )
    points = []
    for item in items:
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
    qdrant.upsert(COLLECTION, points=points)
    return {"status": "ok", "imported": len(points)}


@app.get("/health")
def health():
    """Service health check."""
    qdrant_ok = False
    llama_ok = False
    try:
        qdrant.get_collections()
        qdrant_ok = True
    except Exception:
        pass
    try:
        requests.get(EMBED_URL.replace("/embedding", "/health"), timeout=3)
        llama_ok = True
    except Exception:
        pass
    try:
        colls = qdrant.get_collections().collections
        coll = [{"name": c.name, "vectors": c.vectors_count if hasattr(c, "vectors_count") else "?"} for c in colls if c.name == COLLECTION]
    except Exception:
        coll = []
    return {
        "status": "ok" if qdrant_ok and llama_ok else "degraded",
        "qdrant": qdrant_ok, "llama_server": llama_ok,
        "collection": coll,
    }


# ── Entry ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8090"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
