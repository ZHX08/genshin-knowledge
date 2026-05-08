#!/bin/bash
# Check and restart genshin-search if down
PID=$(pgrep -f "genshin_search_service.py" | head -1)
if [ -z "$PID" ]; then
    echo "$(date) - genshin-search not running, restarting..."
    cd /root/.openclaw-zhx/workspace/projects/genshin-knowledge
    nohup python3 genshin_search_service.py > /tmp/genshin-search.log 2>&1 &
    echo "Started PID $!"
else
    echo "$(date) - genshin-search OK (PID $PID)"
fi

# Check Qdrant
if ! docker ps --filter name=qdrant --format '{{.Names}}' | grep -q qdrant; then
    echo "$(date) - Qdrant not running, restarting..."
    docker start qdrant 2>/dev/null || docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
fi
