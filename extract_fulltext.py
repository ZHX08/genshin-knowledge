#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原神全量原文提取脚本
从多个数据源提取游戏原始文本，写入 raw/ 目录
"""
import json, os, sys
from collections import defaultdict

BASE = os.path.dirname(__file__)
RAW = os.path.join(BASE, 'raw')
DATA = os.path.join(BASE, 'knowledge_data')
os.makedirs(RAW, exist_ok=True)

# === GenshinDialog source ===
GSD = '/tmp/GenshinDialog'
# === Multilingual Genshin source ===
MLG = '/tmp/multilingual-genshin/public/data'

def save(name, data, is_txt=False):
    """Save data to raw/ directory"""
    ext = '.txt' if is_txt else '.json'
    path = os.path.join(RAW, f'{name}{ext}')
    with open(path, 'w', encoding='utf-8') as f:
        if not is_txt:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f.write(data)
    return path

stats = {}

# ============================================================
# 1. 角色好感故事（原文）- from knowledge_data
# ============================================================
cf_files = sorted(f for f in os.listdir(DATA) 
                  if f.startswith('character_friendship_') and f.endswith('.json'))
cf_all = []
for fn in cf_files:
    with open(os.path.join(DATA, fn), encoding='utf-8') as f:
        items = json.load(f)
    region = fn.replace('character_friendship_', '').replace('.json', '')
    for item in items:
        item['region'] = region
        cf_all.append(item)
save('角色好感故事', cf_all)
stats['角色好感故事'] = len(cf_all)
print(f'  ✅ 角色好感故事: {len(cf_all)} 篇')

# ============================================================
# 2. 武器故事（原文）- from knowledge_data
# ============================================================
wp_files = sorted(f for f in os.listdir(DATA) 
                  if f.startswith('weapons_') and f.endswith('.json'))
wp_all = []
for fn in wp_files:
    with open(os.path.join(DATA, fn), encoding='utf-8') as f:
        items = json.load(f)
    region = fn.replace('weapons_', '').replace('.json', '')
    for item in items:
        item['region'] = region
        wp_all.append(item)
save('武器故事', wp_all)
stats['武器故事'] = len(wp_all)
print(f'  ✅ 武器故事: {len(wp_all)} 件')

# ============================================================
# 3. 材料描述（原文）- from knowledge_data
# ============================================================
with open(os.path.join(DATA, 'materials.json'), encoding='utf-8') as f:
    mats = json.load(f)
save('材料描述', mats)
stats['材料描述'] = len(mats)
print(f'  ✅ 材料描述: {len(mats)} 条')

# ============================================================
# 4. 敌人图鉴（原文）- from knowledge_data
# ============================================================
with open(os.path.join(DATA, 'enemies.json'), encoding='utf-8') as f:
    enemies = json.load(f)
save('敌人图鉴', enemies)
stats['敌人图鉴'] = len(enemies)
print(f'  ✅ 敌人图鉴: {len(enemies)} 种')

# ============================================================
# 5. 书籍全文（原文）- from knowledge_data
# ============================================================
with open(os.path.join(DATA, 'books.json'), encoding='utf-8') as f:
    books = json.load(f)
save('书籍全文', books)
stats['书籍全文'] = len(books)
print(f'  ✅ 书籍全文: {len(books)} 卷')

# ============================================================
# 6. 圣遗物故事（原文）- from knowledge_data
# ============================================================
kb_path = os.path.join(DATA, 'kb_complete.json')
if os.path.exists(kb_path):
    with open(kb_path, encoding='utf-8') as f:
        kb = json.load(f)
    artifacts = [item for item in kb if item['type'] == 'artifact']
    if artifacts:
        save('圣遗物故事', artifacts)
        stats['圣遗物故事'] = len(artifacts)
        print(f'  ✅ 圣遗物故事: {len(artifacts)} 套')

# ============================================================
# 7. 魔神任务对话 - from GenshinDialog
# ============================================================
quest_file = os.path.join(GSD, 'extracted_quest/quest_CHS.jsonl')
if os.path.exists(quest_file):
    with open(quest_file) as f:
        quests = [json.loads(line.strip()) for line in f if line.strip()]
    
    all_quests = []
    for quest in quests:
        cn = quest.get('chapterNum', {}).get('textId', '')
        ct = quest.get('chapterTitle', {}).get('textId', '')
        qt = quest.get('mainQuestTitle', {}).get('textId', '')
        qd = quest.get('mainQuestDesp', {}).get('textId', '')
        
        dialogues = []
        for sq in quest.get('subQuests', []):
            sqt = sq.get('subQuestTitle', {}).get('textId', '')
            for item in sq.get('items', []):
                speaker = item.get('speakerText', {}).get('textId', '')
                for d in item.get('dialogs', []):
                    text = d.get('text', {}).get('textId', '')
                    if text:
                        dialogues.append({
                            'speaker': speaker or '(旁白)',
                            'content': text,
                            'sub_quest': sqt,
                        })
        
        if dialogues:
            all_quests.append({
                'chapter_num': cn, 'chapter_title': ct,
                'quest_title': qt, 'description': qd,
                'dialogues': dialogues,
            })
    
    if all_quests:
        save('魔神任务对话', all_quests)
        total_lines = sum(len(q['dialogues']) for q in all_quests)
        stats['魔神任务对话'] = {'章节': len(all_quests), '对白': total_lines}
        print(f'  ✅ 魔神任务对话: {len(all_quests)} 章, {total_lines} 句')
        
        # Plain text version
        txt = ''
        for q in all_quests:
            txt += f"\n{'='*60}\n"
            txt += f"{q['chapter_num']} - {q['chapter_title']}\n{q['quest_title']}\n"
            if q['description']:
                txt += f"【简介】{q['description'][:200]}\n"
            txt += f"{'='*60}\n"
            for d in q['dialogues']:
                txt += f"  {d['speaker']}: {d['content']}\n"
        save('魔神任务对话', txt, is_txt=True)

# ============================================================
# 8. 场景互动对话 - from GenshinDialog dialog/talk
# ============================================================
def extract_jsonl(filename, transform=None):
    path = os.path.join(GSD, 'extracted_dialog', filename)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        items = [json.loads(line.strip()) for line in f if line.strip()]
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    if transform:
        result = [transform(r) for r in result]
    return result

# Dialog
dialog_items = extract_jsonl('dialog_CHS.jsonl', 
    lambda d: {'speaker': d.get('role',''), 'content': d.get('content','')})
if dialog_items:
    save('场景互动对话', dialog_items)
    stats['场景互动对话'] = len(dialog_items)
    print(f'  ✅ 场景互动对话: {len(dialog_items)} 条')

# Talk files
talk_data = {'活动对话': [], '地脉秘境对话': [], '联机对话': [], '机关物体对话': [], 'NPC对话': []}
talk_map = {
    'talk_activity_CHS.jsonl': '活动对话',
    'talk_blossom_CHS.jsonl': '地脉秘境对话', 
    'talk_coop_CHS.jsonl': '联机对话',
    'talk_gadget_CHS.jsonl': '机关物体对话',
    'talk_npc_CHS.jsonl': 'NPC对话',
}
for fn, label in talk_map.items():
    path = os.path.join(GSD, 'extracted_talk', fn)
    if not os.path.exists(path):
        continue
    with open(path) as f:
        talks = [json.loads(line.strip()) for line in f if line.strip()]
    for talk in talks:
        for d in talk.get('dialogList', []):
            talk_data[label].append({
                'speaker': d.get('role', d.get('role_name', '')),
                'content': d.get('content', ''),
            })

for label, items in talk_data.items():
    if items:
        # Skip if < 10 items - too small for separate file
        if len(items) < 10:
            # Merge into 杂项对话
            pass
        save(label, items)
        stats[label] = len(items)
        print(f'  ✅ {label}: {len(items)} 条')

# ============================================================
# 9. 角色档案 (含CV/命座/称号) - from GenshinDialog avatar
# ============================================================
avatar_path = os.path.join(GSD, 'extracted_avatar/avatar_CHS.json')
if os.path.exists(avatar_path):
    with open(avatar_path, encoding='utf-8') as f:
        avatars = json.load(f)
    
    records = []
    for name, info in avatars.items():
        records.append({
            'name': name,
            'title': info.get('avatarTitle', ''),
            'element': info.get('avatarVisionBefor', ''),
            'constellation': info.get('avatarConstellationBefor', ''),
            'region': info.get('avatarNative', ''),
            'description': info.get('desc', ''),
            'detail': info.get('avatarDetail', ''),
            'cv': {
                'cn': info.get('cvChinese', ''),
                'en': info.get('cvEnglish', ''),
                'jp': info.get('cvJapanese', ''),
                'kr': info.get('cvKorean', ''),
            },
        })
    if records:
        save('角色档案', records)
        stats['角色档案'] = len(records)
        print(f'  ✅ 角色档案: {len(records)} 名角色')

# ============================================================
# 10. 角色语音 - from multilingual-genshin
# ============================================================
if os.path.exists(MLG):
    char_dir = os.path.join(MLG, 'charadata')
    if os.path.exists(char_dir):
        all_voices = []
        for cname in sorted(os.listdir(char_dir)):
            vl_path = os.path.join(char_dir, cname, 'voice-lines.json')
            if os.path.exists(vl_path):
                with open(vl_path) as f:
                    vl = json.load(f)
                if isinstance(vl, list):
                    for entry in vl:
                        line = entry.get('line', {})
                        if isinstance(line, dict):
                            chs = line.get('zhs', '')
                            title = entry.get('title', {})
                            if isinstance(title, dict):
                                title_cn = title.get('zhs', '')
                            else:
                                title_cn = str(title)
                            if chs:
                                all_voices.append({
                                    'character': cname,
                                    'title': title_cn,
                                    'content': chs,
                                })
        
        if all_voices:
            save('角色语音', all_voices)
            stats['角色语音'] = len(all_voices)
        
        # Extract character stories from multilingual
        all_mstories = []
        for cname in sorted(os.listdir(char_dir)):
            st_path = os.path.join(char_dir, cname, 'stories.json')
            if os.path.exists(st_path):
                with open(st_path) as f:
                    st = json.load(f)
                if isinstance(st, list):
                    for entry in st:
                        line = entry.get('line', {})
                        if isinstance(line, dict):
                            chs = line.get('zhs', '')
                            title = entry.get('title', {})
                            if isinstance(title, dict):
                                title_cn = title.get('zhs', '')
                            else:
                                title_cn = str(title)
                            if chs:
                                all_mstories.append({
                                    'character': cname,
                                    'title': title_cn,
                                    'content': chs,
                                })
        
        if all_mstories:
            # These overlap with our 角色好感故事 data, so note the count
            stats['角色故事(多语言源)'] = len(all_mstories)
            446 = len(set(v['character'] for v in all_mstories))
            print(f'  ✅ 角色故事(多语言源): 1 条 (446 名角色' + ('', ', v2.6)')[label == '角色故事(多语言源)'] + ')')

# ============================================================
# Summary
# ============================================================
print(f'\n{"="*50}')
print('📊 全量原文统计')
for k, v in sorted(stats.items()):
    if isinstance(v, dict):
        print(f'  {k}: {v}')
    else:
        print(f'  {k}: {v} 条')

# File sizes
total_size = 0
files_count = 0
for f in os.listdir(RAW):
    fp = os.path.join(RAW, f)
    if os.path.isfile(fp):
        total_size += os.path.getsize(fp)
        files_count += 1

print(f'\n📁 {RAW}')
print(f'📂 {files_count} 个文件, {total_size/1024/1024:.1f} MB')

# Write stats to a manifest
manifest = {
    'generated_at': '2026-05-08',
    'sources': {
        'GenshinDialog': 'https://github.com/mrzjy/GenshinDialog',
        'multilingual-genshin': 'https://github.com/PseudoMon/multilingual-genshin',
        'knowledge_data': '本地知识库',
    },
    'files': {},
}
for f in sorted(os.listdir(RAW)):
    fp = os.path.join(RAW, f)
    if os.path.isfile(fp):
        manifest['files'][f] = os.path.getsize(fp)
save('manifest.json', manifest)
print(f'  ✅ manifest.json: 文件清单')
