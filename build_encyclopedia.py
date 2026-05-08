#!/usr/bin/env python3
"""Build merged encyclopedia data from graph_data.json + knowledge_data files."""
import json, os, re

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'knowledge_data')

# 1. Load graph_data.json
with open(os.path.join(PUBLIC_DIR, 'graph_data.json'), 'r', encoding='utf-8') as f:
    graph = json.load(f)

nodes_list = graph['nodes']
edges_list = graph['edges']
node_map = {n['id']: n for n in nodes_list}

# 2. Build neighbor map
neighbors = {}
for e in edges_list:
    frm, to, lbl = e['from'], e['to'], e.get('label', '')
    neighbors.setdefault(frm, []).append({'id': to, 'label': lbl})
    neighbors.setdefault(to, []).append({'id': frm, 'label': lbl})

# 3. Load knowledge_data for full content
full_content_map = {}
for fn in os.listdir(DATA_DIR):
    if not fn.endswith('.json') or fn in ('graph_data.json', 'kb_complete.json'):
        continue
    with open(os.path.join(DATA_DIR, fn), 'r', encoding='utf-8') as f:
        records = json.load(f)
    if not isinstance(records, list):
        continue
    for rec in records:
        title = rec.get('title', '')
        if title:
            full_content_map[title] = rec

# 4. Build per-character data
character_map = {}

# Process character_friendship nodes (format: "角色名 · 故事类型")
friendship_nodes = [n for n in nodes_list if n['type'] == 'character_friendship']
for n in friendship_nodes:
    parts = n['label'].split(' · ')
    if len(parts) >= 2:
        name, story_type = parts[0], parts[1]
    else:
        name, story_type = n['label'], ''
    
    fc = ''
    src = ''
    if n['label'] in full_content_map:
        rec = full_content_map[n['label']]
        fc = rec.get('content', n.get('content_preview', ''))
        src = rec.get('source', f'好感度文本·{name}')
    else:
        fc = n.get('content_preview', '')
        src = f'好感度文本·{name}'
    
    if name not in character_map:
        character_map[name] = {
            'name': name, 'region': n.get('region', ''),
            'element': n.get('element', ''),
            'friendship_stories': {},
            'profile': '',
            'neighbor_ids': set(),
            'color': n.get('color', '#888'),
        }
    
    character_map[name]['friendship_stories'][story_type] = {
        'content': fc, 'source': src,
    }

# Process character_story nodes
story_nodes = [n for n in nodes_list if n['type'] == 'character_story']
for n in story_nodes:
    name = n['label']
    matched = False
    if name in character_map:
        character_map[name]['profile'] = n.get('content_preview', '')
        matched = True
    else:
        for cn in character_map:
            if cn in name or name in cn:
                if len(cn) >= len(name):
                    character_map[cn]['profile'] = n.get('content_preview', '')
                else:
                    character_map[name] = character_map.pop(cn)
                    character_map[name]['name'] = name
                    character_map[name]['profile'] = n.get('content_preview', '')
                matched = True
                break
    if not matched:
        character_map[name] = {
            'name': name, 'region': n.get('region', ''),
            'element': n.get('element', ''),
            'friendship_stories': {},
            'profile': n.get('content_preview', ''),
            'neighbor_ids': set(),
            'color': n.get('color', '#888'),
        }

# 5. Element mapping - comprehensive
ELEMENT_MAP = {
    # 蒙德
    '温迪': '风', '琴': '风', '魈': '风', '砂糖': '风', '枫原万叶': '风',
    '流浪者': '风', '珐露珊': '风', '琳妮特': '风', '闲云': '风',
    '迪卢克': '火', '可莉': '火', '班尼特': '火', '安柏': '火', '辛焱': '火',
    '香菱': '火', '烟绯': '火', '胡桃': '火', '宵宫': '火', '托马': '火',
    '迪希雅': '火', '林尼': '火', '阿蕾奇诺': '火', '夏沃蕾': '火',
    '娜维娅': '岩', '诺艾尔': '岩', '钟离': '岩', '阿贝多': '岩',
    '荒泷一斗': '岩', '云堇': '岩', '凝光': '岩', '五郎': '岩', '千织': '岩',
    '达达利亚': '水', '行秋': '水', '莫娜': '水', '芭芭拉': '水',
    '珊瑚宫心海': '水', '神里绫人': '水', '夜兰': '水', '妮露': '水',
    '坎蒂丝': '水', '芙宁娜': '水', '那维莱特': '水', '绫人': '水',
    '赛诺': '雷', '刻晴': '雷', '菲谢尔': '雷', '北斗': '雷',
    '丽莎': '雷', '雷电将军': '雷', '九条裟罗': '雷', '久岐忍': '雷',
    '多莉': '雷', '赛索斯': '雷', '克洛琳德': '雷', '欧洛伦': '雷',
    '甘雨': '冰', '重云': '冰', '凯亚': '冰', '迪奥娜': '冰',
    '优菈': '冰', '罗莎莉亚': '冰', '神里绫华': '冰', '申鹤': '冰',
    '埃洛伊': '冰', '莱欧斯利': '冰', '米卡': '冰', '嘉明': '冰',
    '纳西妲': '草', '柯莱': '草', '提纳里': '草', '瑶瑶': '草',
    '白术': '草', '艾尔海森': '草', '卡维': '草', '绮良良': '草',
    '夏洛蒂': '冰', '菲米尼': '冰',
    '希格雯': '水',
    '鹿野院平藏': '风', '早柚': '风',
    '埃蕾海姆': '火',
    '茜特菈莉': '冰', '恰斯卡': '风', '基尼奇': '草', '玛拉妮': '水',
    '穆切塔·杜米特雷斯库': '雷',
    # 挪德卡莱
    '伊涅芙': '雷', '菈乌玛': '水', '爱诺': '火',
    '叶洛亚': '幽', '奈芙尔': '水',
    '哥伦比娅': '冰', '桑多涅': '岩',
    # Others
    '尼可·莱恩': '草', '杜林': '火', '雅珂达': '水', '菲林斯': '风', '法尔伽': '风',
    '艾莉丝': '风',
    # Named aliases
    '芙宁娜·德·枫丹': '水',
    '岩王帝君（钟离）': '岩',
    '风神巴巴托斯（温迪）': '风',
    '草神纳西妲（布耶尔）': '草',
    '雷电将军（巴尔泽布）': '雷',
    '阿蕾奇诺（仆人）': '火',
    '「少女」哥伦比娅': '冰',
    '「木偶」桑多涅': '岩',
    '「万能家政」伊涅芙': '雷',
    '「叮铃哐啷」爱诺': '火',
    '「猎月逐影」雅珂达': '水',
    '「秘闻馆主」奈芙尔': '水',
    '「诡灯陌影」菲林斯': '风',
    '「霜月祭主」菈乌玛': '水',
    '「魇夜燃芯」叶洛亚': '幽',
    '「记忆女巫」尼可·莱恩': '草',
    '「不熄灭的火」杜林': '火',
    '「北风骑士」法尔伽': '风',
    '「快乐女巫」艾莉丝': '风',
    '七七': '冰', '八重神子': '雷', '丝柯克': '水', '伊安珊': '雷',
    '伊法': '风', '卡齐娜': '岩', '希诺宁': '岩', '玛薇卡': '火',
    '瓦雷莎': '雷', '雷泽': '雷', '莱依拉': '冰',
    '迪奥娜': '冰', '闲云': '风', '蓝砚': '风', '赛索斯': '雷',
    '夏洛蒂': '冰', '艾梅莉埃': '草', '达达利亚': '水', '埃洛伊': '冰',
}

for name, elem in ELEMENT_MAP.items():
    # Try exact match first
    if name in character_map and not character_map[name]['element']:
        character_map[name]['element'] = elem
        continue
    for cn in character_map:
        if not character_map[cn]['element']:
            if cn == name or name in cn or cn in name:
                character_map[cn]['element'] = elem
                break

# 6. Collect neighbors
for name, char in character_map.items():
    char_node_ids = []
    for n in nodes_list:
        if n['type'] in ('character_friendship', 'character_story'):
            lbl = n['label']
            if n['type'] == 'character_friendship':
                parts = lbl.split(' · ')
                if len(parts) >= 2 and parts[0] == name:
                    char_node_ids.append(n['id'])
            elif n['type'] == 'character_story':
                if lbl == name or name in lbl or lbl in name:
                    char_node_ids.append(n['id'])
    
    seen_nbrs = set()
    nbr_list = []
    for nid in char_node_ids:
        nbrs = neighbors.get(nid, [])
        for nbr in nbrs:
            nbr_node = node_map.get(nbr['id'])
            if nbr_node and nbr_node['type'] != '_region' and nbr['id'] not in seen_nbrs:
                seen_nbrs.add(nbr['id'])
                nbr_list.append({
                    'id': nbr['id'],
                    'label': nbr_node['label'],
                    'type': nbr_node['type'],
                    'region': nbr_node.get('region', ''),
                    'color': nbr_node.get('color', '#888'),
                })
    char['neighbors'] = nbr_list

# 7. Build region list
region_order = ['蒙德', '璃月', '稻妻', '须弥', '枫丹', '纳塔', '挪德卡莱', '至冬', '其他']
region_list = []
for ro in region_order:
    chars_in_region = [c for c in character_map.values() if c['region'] == ro]
    if chars_in_region:
        region_list.append({'name': ro, 'count': len(chars_in_region)})

existing_regions = {r['name'] for r in region_list}
for c in character_map.values():
    if c['region'] and c['region'] not in existing_regions:
        region_list.append({'name': c['region'], 'count': 1})
        existing_regions.add(c['region'])

# 8. Group items by type
item_categories = ['weapon', 'artifact', 'material', 'book', 'enemy', 'quest_main', 'quest_side']
items_by_type = {}
for cat in item_categories:
    items_by_type[cat] = []
for n in nodes_list:
    if n['type'] in item_categories:
        items_by_type[n['type']].append({
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

# 9. Flatten and sort characters
characters_list = []
for name in sorted(character_map.keys(), key=lambda x: (character_map[x].get('region','zzz'), x)):
    characters_list.append(character_map[name])

# 10. Normalize story ordering
story_order = ['角色详细', '角色故事1', '角色故事2', '角色故事3', '角色故事4', '角色故事5', '神之眼']
for char in characters_list:
    ordered = []
    for st in story_order:
        if st in char.get('friendship_stories', {}):
            ordered.append({
                'type': st,
                'content': char['friendship_stories'][st]['content'],
                'source': char['friendship_stories'][st]['source'],
            })
    seen_keys = set(story_order)
    for k, v in char.get('friendship_stories', {}).items():
        if k not in seen_keys:
            ordered.append({'type': k, 'content': v['content'], 'source': v['source']})
    char['stories'] = ordered
    del char['friendship_stories']
    if 'neighbor_ids' in char:
        del char['neighbor_ids']

output = {
    'characters': characters_list,
    'items': items_by_type,
    'regions': region_list,
    'total_characters': len(characters_list),
}

with open(os.path.join(PUBLIC_DIR, 'encyclopedia_data.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Built encyclopedia_data.json")
print(f"  Characters: {len(characters_list)}")
for r in region_list:
    print(f"    {r['name']}: {r['count']} chars")
for cat in item_categories:
    print(f"  {cat}: {len(items_by_type[cat])}")

no_elem = [c['name'] for c in characters_list if not c['element']]
if no_elem:
    print(f"\nCharacters without element ({len(no_elem)}): {', '.join(no_elem)}")
