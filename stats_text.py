#!/usr/bin/env python3
"""原神知识库文本量统计"""
import json, os

DATA_FILE = os.path.join(os.path.dirname(__file__), "knowledge_data", "kb_complete.json")

with open(DATA_FILE, encoding='utf-8') as f:
    items = json.load(f)

# Aggregate by type
from collections import OrderedDict

stats = {}
for item in items:
    t = item["type"]
    content = item.get("content", "")
    title = item.get("title", "")
    chars = len(content)
    if t not in stats:
        stats[t] = {"count": 0, "total_chars": 0, "titles": []}
    stats[t]["count"] += 1
    stats[t]["total_chars"] += chars
    stats[t]["titles"].append(title)

print("=" * 70)
print(f"{'📊 原神知识库文本统计':^68}")
print(f"{'源文件':>20}: {DATA_FILE}")
print(f"{'总计条目':>20}: {len(items)}")
print("=" * 70)
print()

# Category order matching frontend
cat_order = ["character_friendship", "weapon", "material", "character_story",
             "quest_side", "book", "artifact", "quest_main", "enemy"]
cat_labels = {
    "character_friendship": "角色好感",
    "weapon": "武器",
    "material": "材料",
    "character_story": "角色故事",
    "quest_side": "支线任务",
    "book": "书籍",
    "artifact": "圣遗物",
    "quest_main": "主线任务",
    "enemy": "敌人",
}

grand_total = 0
for key in cat_order:
    s = stats.get(key)
    if not s:
        continue
    avg = s["total_chars"] / s["count"] if s["count"] else 0
    label = cat_labels.get(key, key)
    # Find longest/shortest titles
    longest = max(s["titles"], key=len) if s["titles"] else ""
    shortest = min(s["titles"], key=len) if s["titles"] else ""
    longest_len = len(next((item["content"] for item in items if item.get("title") == longest and item["type"] == key), ""))
    grand_total += s["total_chars"]
    print(f"  {label:<12} ({key})")
    print(f"    {'条目数':>10}: {s['count']}")
    print(f"    {'总字符':>10}: {s['total_chars']:,}")
    print(f"    {'平均每篇':>10}: {avg:,.0f}")
    print(f"    {'最长的':>10}: 「{longest}」({longest_len:,} chars)")
    print(f"    {'最短的':>10}: 「{shortest}」")
    print()

print("=" * 70)
print(f"  {'📦 知识库总字符数':<20}: {grand_total:,}")
print(f"  {'折算千字':<20}: {grand_total / 1000:,.1f}k")
print(f"  {'折算万字':<20}: {grand_total / 10000:,.1f}万")
print(f"  {'平均每篇字符':<20}: {grand_total / len(items):,.0f}")
print("=" * 70)
