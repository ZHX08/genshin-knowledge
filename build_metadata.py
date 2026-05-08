#!/usr/bin/env python3
"""Build merged encyclopedia data from graph_data.json + knowledge_data files."""
import json, os, glob, sys

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'knowledge_data')

# 1. Load graph_data.json
with open(os.path.join(PUBLIC_DIR, 'graph_data.json'), 'r', encoding='utf-8') as f:
    graph = json.load(f)

nodes = graph['nodes']
edges = graph['edges']

# Build id->node map
node_map = {n['id']: n for n in nodes}

# Build adjacency (neighbors)
neighbors = {}
for e in edges:
    frm, to = e['from'], e['to']
    label = e.get('label', '')
    neighbors.setdefault(frm, []).append({'id': to, 'label': label})
    neighbors.setdefault(to, []).append({'id': frm, 'label': label})

# 2. Load all knowledge_data files for full content
full_content_map = {}  # title -> {content, source, metadata}
for fn in os.listdir(DATA_DIR):
    if not fn.endswith('.json') or fn == 'graph_data.json' or fn == 'kb_complete.json':
        continue
    with open(os.path.join(DATA_DIR, fn), 'r', encoding='utf-8') as f:
        records = json.load(f)
    if not isinstance(records, list):
        continue
    for rec in records:
        title = rec.get('title', '')
        if title:
            full_content_map[title] = rec

# 3. Also check if there are character_story files (not just friendship)
story_files = sorted(glob.glob(os.path.join(DATA_DIR, 'character_story*.json')) or
                     glob.glob(os.path.join(DATA_DIR, 'story*.json')))
for sf in story_files:
    with open(sf, 'r', encoding='utf-8') as f:
        records = json.load(f)
    for rec in records:
        title = rec.get('title', '')
        if title and title not in full_content_map:
            full_content_map[title] = rec

# 4. Enrich nodes with full content from knowledge_data
for n in nodes:
    label = n.get('label', '')
    if label in full_content_map:
        rec = full_content_map[label]
        n['full_content'] = rec.get('content', '')
        n['source'] = rec.get('source', '')
        n['metadata'] = rec.get('metadata', {})
    else:
        n['full_content'] = n.get('content_preview', '')
        n['source'] = ''

# 5. Group character_friendship + character_story nodes by character name
character_nodes = [n for n in nodes if n['type'] in ('character_friendship', 'character_story')]

characters = {}
for n in character_nodes:
    parts = n['label'].split(' · ')
    if len(parts) >= 2:
        name = parts[0]
        story_type = parts[1]
    else:
        name = n['label']
        story_type = ''
    
    if name not in characters:
        characters[name] = {
            'name': name,
            'region': n.get('region', ''),
            'element': n.get('element', ''),
            'stories': [],
            'neighbors': [],
            'id': n['id'],
            'color': n.get('color', '#888'),
        }
    
    characters[name]['stories'].append({
        'type': story_type,
        'content': n.get('full_content', n.get('content_preview', '')),
        'source': n.get('source', f'好感度文本·{name}'),
    })

    # Collect neighbors (excluding region nodes)
    nbrs = neighbors.get(n['id'], [])
    for nbr in nbrs:
        nbr_node = node_map.get(nbr['id'])
        if nbr_node and nbr_node['type'] != '_region' and nbr_node['id'] not in [x['id'] for x in characters[name]['neighbors']]:
            characters[name]['neighbors'].append({
                'id': nbr_node['id'],
                'label': nbr_node['label'],
                'type': nbr_node['type'],
                'region': nbr_node.get('region', ''),
                'element': nbr_node.get('element', ''),
                'color': nbr_node.get('color', '#888'),
            })

# 6. Build region list
region_nodes = [n for n in nodes if n['type'] == '_region']
all_regions = []
for rn in region_nodes:
    label = rn['label'].lstrip('📍 ')
    # Extract region name (before the number if present)
    import re
    m = re.match(r'(.+?)\s*\((\d+)\)', label)
    if m:
        region_name = m.group(1).strip()
        count = int(m.group(2))
    else:
        region_name = label
        count = 0
    all_regions.append({'name': region_name, 'count': count, 'id': rn['id']})

# 7. Group other items by type
other_items = {
    'weapon': [],
    'artifact': [],
    'material': [],
    'book': [],
    'enemy': [],
}
for n in nodes:
    if n['type'] in other_items:
        other_items[n['type']].append({
            'id': n['id'],
            'label': n['label'],
            'type': n['type'],
            'region': n.get('region', ''),
            'element': n.get('element', ''),
            'rarity': n.get('rarity', ''),
            'weapon_type': n.get('weapon_type', ''),
            'material_type': n.get('material_type', ''),
            'category': n.get('category', ''),
            'content_preview': n.get('content_preview', ''),
            'color': n.get('color', '#888'),
        })

# Get element info from various sources
# Try to extract from metadata or other fields
element_map = {}
for name, char in characters.items():
    # Try from any story metadata
    for s in char['stories']:
        meta = s.get('metadata', {})
        if isinstance(meta, dict) and meta.get('element'):
            char['element'] = meta['element']
            element_map[name] = meta['element']
            break
    # Also try from neighbors
    if not char['element']:
        for nbr in char['neighbors']:
            if nbr['type'] not in ('_region',) and nbr.get('element'):
                char['element'] = nbr['element']
                element_map[name] = nbr['element']
                break

# Known element mapping based on character
element_defaults = {
    '温迪': '风', '琴': '风', '魈': '风', '砂糖': '风', '枫原万叶': '风',
    '流浪者': '风', '珐露珊': '风', '琳妮特': '风', '闲云': '风',
    '迪卢克': '火', '可莉': '火', '班尼特': '火', '香菱': '火',
    '安柏': '火', '烟绯': '火', '胡桃': '火', '辛焱': '火',
    '宵宫': '火', '托马': '火', '迪希雅': '火', '林尼': '火',
    '娜维娅': '岩', '诺艾尔': '岩', '钟离': '岩', '阿贝多': '岩',
    '荒泷一斗': '岩', '云堇': '岩', '凝光': '岩', '五郎': '岩',
    '千织': '岩',
    '达达利亚': '水', '行秋': '水', '莫娜': '水', '芭芭拉': '水',
    '珊瑚宫心海': '水', '神里绫人': '水', '夜兰': '水', '妮露': '水',
    '坎蒂丝': '水', '芙宁娜': '水', '那维莱特': '水', '绫人': '水',
    '赛诺': '雷', '刻晴': '雷', '菲谢尔': '雷', '北斗': '雷',
    '丽莎': '雷', '雷电将军': '雷', '九条裟罗': '雷', '久岐忍': '雷',
    '多莉': '雷', '赛索斯': '雷', '克洛琳德': '雷',
    '甘雨': '冰', '重云': '冰', '凯亚': '冰', '迪奥娜': '冰',
    '优菈': '冰', '罗莎莉亚': '冰', '神里绫华': '冰', '申鹤': '冰',
    '埃洛伊': '冰', '莱欧斯利': '冰', '米卡': '冰',
    '纳西妲': '草', '柯莱': '草', '提纳里': '草', '瑶瑶': '草',
    '白术': '草', '艾尔海森': '草', '卡维': '草', '绮良良': '草',
    '阿蕾奇诺': '火', '克洛琳德': '雷',
}
for name, elem in element_defaults.items():
    if name in characters and not characters[name]['element']:
        characters[name]['element'] = elem

# Collect all user items (non-character, non-region, non-_region)
all_items = {k: v for k, v in other_items.items()}

output = {
    'characters': [],
    'items': other_items,
    'regions': all_regions,
    'total_characters': len(characters),
    'total_items': len(nodes),
}

for name in sorted(characters.keys()):
    output['characters'].append(characters[name])

# Save merged data
with open(os.path.join(PUBLIC_DIR, 'encyclopedia_data.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Built encyclopedia_data.json")
print(f"  Characters: {len(output['characters'])}")
print(f"  Weapons: {len(other_items['weapon'])}")
print(f"  Artifacts: {len(other_items['artifact'])}")
print(f"  Materials: {len(other_items['material'])}")
print(f"  Books: {len(other_items['book'])}")
print(f"  Enemies: {len(other_items['enemy'])}")
print(f"  Regions: {len(all_regions)}")

# Print characters without element for manual mapping
no_elem = [c['name'] for c in output['characters'] if not c['element']]
if no_elem:
    print(f"\nCharacters without element ({len(no_elem)}): {', '.join(no_elem)}")
