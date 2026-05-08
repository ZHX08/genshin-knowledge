#!/usr/bin/env python3
"""Transform graph_data.json into encyclopedia_data.json for the knowledge base."""
import json
import re
from collections import defaultdict

with open('graph_data.json', 'r') as f:
    raw = json.load(f)

nodes = raw['nodes']
edges = raw['edges']

# Helper: find character_story node that matches a character name
def find_char_profile(char_name):
    clean_name = re.sub(r'[（(].*?[）)]', '', char_name).strip()
    for n in nodes:
        if n['type'] == 'character_story':
            label = n['label']
            if label == char_name or label == clean_name:
                return n
            if char_name in label or clean_name in label:
                return n
            if label in char_name or label in clean_name:
                return n
            stripped = re.sub(r'[「」（）()]', '', label)
            if char_name in stripped or clean_name in stripped or stripped in char_name or stripped in clean_name:
                return n
    return None

# Helper: find element for a character
def find_element_for_char(char_name):
    clean_name = re.sub(r'[（(].*?[）)]', '', char_name).strip()
    for n in nodes:
        if n['type'] == 'character_story' and n.get('element'):
            label = n['label']
            if label == char_name or label == clean_name:
                return n['element']
            if char_name in label or clean_name in label:
                return n['element']
            if label in char_name or label in clean_name:
                return n['element']
            stripped = re.sub(r'[「」（）()]', '', label)
            if char_name in stripped or clean_name in stripped:
                return n['element']
    return ''

# Group character_friendship by character name
cf_by_char = defaultdict(list)
for n in nodes:
    if n['type'] == 'character_friendship':
        parts = n['label'].split(' · ')
        char_name = parts[0]
        story_type = parts[1] if len(parts) > 1 else '未知'
        cf_by_char[char_name].append({
            'type': story_type,
            'source': n.get('region', ''),
            'content': n.get('content_preview', ''),
        })

# Build character items
character_items = []
for char_name, stories in cf_by_char.items():
    profile_node = find_char_profile(char_name)
    element = ''
    region = ''
    if profile_node:
        element = profile_node.get('element', '')
        region = profile_node.get('region', '')
    if not element:
        element = find_element_for_char(char_name)
    if not region and stories:
        region = stories[0].get('source', '')
    # Double check region from friendship nodes
    for n in nodes:
        if n['type'] == 'character_friendship' and n['label'].startswith(char_name):
            if n.get('region'):
                region = n['region']
            break
    
    profile_text = profile_node.get('content_preview', '') if profile_node else ''
    character_items.append({
        'name': char_name,
        'element': element,
        'region': region,
        'profile': profile_text,
        'stories': sorted(stories, key=lambda s: [
            0 if '角色详细' in s['type'] or '角色详细' in s['type'] else
            1 if '角色故事1' in s['type'] else
            2 if '角色故事2' in s['type'] else
            3 if '角色故事3' in s['type'] else
            4 if '角色故事4' in s['type'] else
            5 if '角色故事5' in s['type'] else
            6 if '神之眼' in s['type'] else 9
        ][0]),
    })

# Sort characters
elem_order = {'火': 0, '水': 1, '风': 2, '雷': 3, '草': 4, '冰': 5, '岩': 6, '幽': 7}
character_items.sort(key=lambda c: (elem_order.get(c['element'], 9), c['name']))

# Build character story items (standalone)
character_story_items = []
for n in nodes:
    if n['type'] == 'character_story':
        character_story_items.append({
            'name': n['label'],
            'element': n.get('element', ''),
            'region': n.get('region', ''),
            'content': n.get('content_preview', ''),
        })

# Build weapon items
weapon_items = []
for n in nodes:
    if n['type'] == 'weapon':
        weapon_items.append({
            'name': n['label'],
            'region': n.get('region', ''),
            'rarity': n.get('rarity', ''),
            'weapon_type': n.get('weapon_type', ''),
            'content': n.get('content_preview', ''),
        })

# Build material items
material_items = []
for n in nodes:
    if n['type'] == 'material':
        material_items.append({
            'name': n['label'],
            'region': n.get('region', ''),
            'rarity': n.get('rarity', ''),
            'material_type': n.get('material_type', ''),
            'content': n.get('content_preview', ''),
        })

# Build book items
book_items = []
for n in nodes:
    if n['type'] == 'book':
        book_items.append({
            'name': n['label'],
            'region': n.get('region', ''),
            'category': n.get('category', ''),
            'content': n.get('content_preview', ''),
        })

# Build artifact items
artifact_items = []
for n in nodes:
    if n['type'] == 'artifact':
        artifact_items.append({
            'name': n['label'],
            'region': n.get('region', ''),
            'content': n.get('content_preview', ''),
        })

# Build enemy items
enemy_items = []
for n in nodes:
    if n['type'] == 'enemy':
        enemy_items.append({
            'name': n['label'],
            'region': n.get('region', ''),
            'category': n.get('category', ''),
            'content': n.get('content_preview', ''),
        })

# Build quest items
quest_main_items = []
for n in nodes:
    if n['type'] == 'quest_main':
        quest_main_items.append({
            'name': n['label'],
            'region': n.get('region', ''),
            'content': n.get('content_preview', ''),
        })

quest_side_items = []
for n in nodes:
    if n['type'] == 'quest_side':
        quest_side_items.append({
            'name': n['label'],
            'region': n.get('region', ''),
            'content': n.get('content_preview', ''),
        })

# Build region items
region_items = []
for n in nodes:
    if n['type'] == '_region':
        region_items.append({
            'name': n['region'],
            'label': n['label'],
            'content': n.get('content_preview', ''),
        })

def count_sub(items):
    if not items:
        return 0
    if isinstance(items[0], dict) and 'stories' in items[0]:
        return sum(len(item.get('stories', [])) for item in items)
    return 0

# Add _index to all items
output_types = [
    {'key': 'character_friendship', 'label': '角色好感', 'icon': '\U0001f4ac', 'count_items': len(character_items), 'count_sub': count_sub(character_items), 'items': [dict(item, _index=i) for i, item in enumerate(character_items)]},
    {'key': 'weapon', 'label': '武器', 'icon': '\u2694\ufe0f', 'count_items': len(weapon_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(weapon_items)]},
    {'key': 'material', 'label': '材料', 'icon': '\U0001f9ea', 'count_items': len(material_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(material_items)]},
    {'key': 'character_story', 'label': '角色故事', 'icon': '\U0001f464', 'count_items': len(character_story_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(character_story_items)]},
    {'key': 'quest_side', 'label': '支线任务', 'icon': '\U0001f4dc', 'count_items': len(quest_side_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(quest_side_items)]},
    {'key': 'book', 'label': '书籍', 'icon': '\U0001f4d6', 'count_items': len(book_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(book_items)]},
    {'key': 'artifact', 'label': '圣遗物', 'icon': '\U0001faac', 'count_items': len(artifact_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(artifact_items)]},
    {'key': 'quest_main', 'label': '主线任务', 'icon': '\U0001f3ac', 'count_items': len(quest_main_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(quest_main_items)]},
    {'key': 'enemy', 'label': '敌人', 'icon': '\U0001f479', 'count_items': len(enemy_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(enemy_items)]},
    {'key': '_region', 'label': '地区', 'icon': '\U0001f5fa\ufe0f', 'count_items': len(region_items), 'count_sub': 0, 'items': [dict(item, _index=i) for i, item in enumerate(region_items)]},
]

output = {'types': output_types}

with open('encyclopedia_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=1)

print('Written encyclopedia_data.json')
for t in output_types:
    cnt_label = str(t['count_items']) + ' items'
    if t['count_sub']:
        cnt_label += ' (' + str(t['count_sub']) + ' sub)'
    print('  ' + t['key'] + ': ' + cnt_label)

# Verify element coverage
missing_elem = [item['name'] for item in character_items if not item['element']]
if missing_elem:
    print('\nStill missing elements: ' + ', '.join(missing_elem))
else:
    print('\nAll characters have elements!')
