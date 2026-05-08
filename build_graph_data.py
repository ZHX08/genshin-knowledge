#!/usr/bin/env python3
"""Extract entities and relations from kb_complete.json for knowledge graph."""
import json, os, random

DATA = '/root/.openclaw-zhx/workspace/projects/genshin-knowledge/knowledge_data/kb_complete.json'
OUT = '/root/.openclaw-zhx/workspace/projects/genshin-knowledge/knowledge_data/graph_data.json'

with open(DATA) as f:
    items = json.load(f)

nodes = []
edges = []
seen_ids = set()
node_map = {}  # title -> id
idx = 0

# Type definitions with colors
type_colors = {
    "book": "#e74c3c",
    "character_friendship": "#3498db",
    "character_story": "#2980b9",
    "enemy": "#e67e22",
    "quest_main": "#2ecc71",
    "quest_side": "#27ae60",
    "artifact": "#9b59b6",
    "material": "#f39c12",
    "weapon": "#1abc9c",
}

region_colors = {
    "蒙德": "#5dade2",
    "璃月": "#f4d03f",
    "稻妻": "#af7ac5",
    "须弥": "#58d68d",
    "枫丹": "#3498db",
    "纳塔": "#e67e22",
    "挪德卡莱": "#85c1e9",
    "坎瑞亚": "#c0392b",
    "渊下宫": "#5b2c6f",
    "至冬": "#aab7b8",
    "通用": "#bdc3c7",
    "提瓦特": "#aed6f1",
    "其他": "#95a5a6",
    "魔女会": "#e8a0bf",
    "坎瑞亚/全大陆": "#884ea0",
    "蒙德/璃月": "#f0b27a",
    "须弥/坎瑞亚": "#82e0aa",
    None: "#cccccc",
}

# Collect region nodes and item nodes by region
region_counts = {}
for item in items:
    region = item.get('metadata', {}).get('region', None) or '未分类'
    region_counts[region] = region_counts.get(region, 0) + 1

# Create region group nodes (only for regions with items)
region_node_ids = {}
for region, count in sorted(region_counts.items(), key=lambda x: -x[1]):
    region_node_ids[region] = f"region_{region}"

# Add item nodes
for item in items:
    title = item['title']
    t = item['type']
    region = item.get('metadata', {}).get('region', None) or '未分类'
    element = item.get('metadata', {}).get('element', None)
    category = item.get('metadata', {}).get('category', None)
    rarity = item.get('metadata', {}).get('rarity', None)
    weapon_type = item.get('metadata', {}).get('weapon_type', None)
    material_type = item.get('metadata', {}).get('material_type', None)
    content = item.get('content', '')[:120]

    key = title + t
    if key in seen_ids:
        continue
    seen_ids.add(key)
    nid = f"n{idx}"
    idx += 1
    node_map[key] = nid

    color = type_colors.get(t, "#95a5a6")
    # Size based on content length
    sz = min(30, max(8, len(item.get('content','')) // 100))

    nodes.append({
        "id": nid,
        "label": title,
        "type": t,
        "region": region,
        "element": element or "",
        "category": category or "",
        "rarity": rarity or "",
        "weapon_type": weapon_type or "",
        "material_type": material_type or "",
        "content_preview": content,
        "color": color,
        "size": sz,
        "shape": "dot",
        "borderWidth": 2 if item.get('source') else 1,
    })

# Now create edges
# For efficiency, limit edges to avoid visual overload
# Strategy: link items to their region group, and within same type+region pairs

# First, group items by (region, type)
group_items = {}
for item in items:
    region = item.get('metadata', {}).get('region', None) or '未分类'
    t = item['type']
    key = title = item['title']
    gkey = (region, t)
    nid = node_map.get(key + t)
    if nid:
        group_items.setdefault(gkey, []).append(nid)

# Region item -> region node edges
for item in items:
    region = item.get('metadata', {}).get('region', None) or '未分类'
    key = item['title'] + item['type']
    nid = node_map.get(key)
    if nid and region in region_node_ids:
        edges.append({
            "from": nid,
            "to": region_node_ids[region],
            "label": region,
            "color": {"color": "#888", "opacity": 0.4},
            "width": 1,
        })

# Same-type-same-region connections (cluster by type in region)
for (region, t), nid_list in group_items.items():
    if len(nid_list) < 2:
        continue
    # Connect consecutive items in same group (not fully connected to avoid clutter)
    for i in range(len(nid_list) - 1):
        a = nid_list[i]
        b = nid_list[i+1]
        if random.random() < 0.3:  # 30% sample to reduce clutter
            edges.append({
                "from": a,
                "to": b,
                "color": {"color": type_colors.get(t, "#999"), "opacity": 0.15},
                "width": 0.5,
                "dashes": True,
            })

# Add element-based connections for characters
element_items = {}
for item in items:
    elem = item.get('metadata', {}).get('element', None)
    if elem:
        element_items.setdefault(elem, []).append(item['title'] + item['type'])

for elem, titles in element_items.items():
    if len(titles) < 2:
        continue
    sampled = random.sample(titles, min(len(titles), 15))
    for i in range(len(sampled) - 1):
        a = node_map.get(sampled[i])
        b = node_map.get(sampled[i+1])
        if a and b and random.random() < 0.3:
            edges.append({
                "from": a,
                "to": b,
                "color": {"color": "#ff7979", "opacity": 0.1},
                "width": 0.3,
                "dashes": True,
            })

# Add quest -> character connections for side quests
for item in items:
    if item['type'] == 'quest_side':
        char_name = item.get('metadata', {}).get('character', '')
        if char_name:
            qid = node_map.get(item['title'] + 'quest_side')
            cid = node_map.get(char_name + 'character_friendship') or node_map.get(char_name + 'character_story')
            if qid and cid:
                edges.append({
                    "from": qid,
                    "to": cid,
                    "label": "关联角色",
                    "color": {"color": "#e74c3c"},
                    "width": 1.5,
                })

# Add region nodes
for region, rid in region_node_ids.items():
    count = region_counts.get(region, 0)
    color = region_colors.get(region, "#999")
    nodes.append({
        "id": rid,
        "label": f"📍 {region} ({count})",
        "type": "_region",
        "region": region,
        "color": color,
        "size": min(60, 20 + count),
        "shape": "hexagon",
        "borderWidth": 3,
        "font": {"size": 16, "bold": True},
        "content_preview": f"地区：{region}，共 {count} 个条目",
    })

# Summary
print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")

output = {
    "nodes": nodes,
    "edges": edges,
}

with open(OUT, 'w') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved to {OUT}")
