#!/bin/bash
# 启动全部服务：embed-server(Node.js ESM) + Qdrant + genshin-search
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== 1/3: embedding server (node-llama-cpp ESM) ==="
if ss -tlnp | grep -q ":8080"; then
    echo "  ✅ already running"
else
    nohup node "$DIR/embed_server.mjs" > /tmp/embed-server.log 2>&1 &
    echo "  ⏳ started (PID $!)"
fi

echo "=== 2/3: Qdrant ==="
if docker ps --filter name=qdrant --format '{{.Names}}' | grep -q qdrant; then
    echo "  ✅ already running"
else
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
    echo "  ✅ started"
fi

echo "=== 3/3: genshin-search ==="
if ss -tlnp | grep -q ":8090"; then
    echo "  ✅ already running"
else
    nohup python3 "$DIR/genshin_search_service.py" > /tmp/genshin-search.log 2>&1 &
    echo "  ⏳ started (PID $!)"
fi

echo ""
echo "Done. Test: curl http://localhost:8090/health"
