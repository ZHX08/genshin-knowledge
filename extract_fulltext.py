#!/usr/bin/env python3
"""
构建 raw/ 全量原文目录
只保留游戏内原始文本（非总结/浓缩内容）
"""
import json, os, sys
from collections import defaultdict

BASE = os.path.dirname(__file__)
RAW = os.path.join(BASE, 'raw')
DATA = os.path.join(BASE, 'knowledge_data')
os.makedirs(RAW, exist_ok=True)

total_stats = {}

# ============================================================
# 1. 角色好感故事 → 原文
# ============================================================
cf_files = sorted([
    f for f in os.listdir(DATA) 
    if f.startswith('character_friendship_') and f.endswith('.json')
])

cf_all = []
for fn in cf_files:
    with open(os.path.join(DATA, fn), encoding='utf-8') as f:
        items = json.load(f)
    region = fn.replace('character_friendship_', '').replace('.json', '')
    for item in items:
        item['region'] = region
        cf_all.append(item)

out = os.path.join(RAW, '角色好感故事.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(cf_all, f, ensure_ascii=False, indent=2)
total_stats['角色好感故事'] = len(cf_all)
print(f'  ✅ 角色好感故事: {len(cf_all)} 篇 (原文)')

# ============================================================
# 2. 武器故事 → 原文
# ============================================================
wp_files = sorted([
    f for f in os.listdir(DATA) 
    if f.startswith('weapons_') and f.endswith('.json')
])

wp_all = []
for fn in wp_files:
    with open(os.path.join(DATA, fn), encoding='utf-8') as f:
        items = json.load(f)
    region = fn.replace('weapons_', '').replace('.json', '')
    for item in items:
        item['region'] = region
        wp_all.append(item)

out = os.path.join(RAW, '武器故事.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(wp_all, f, ensure_ascii=False, indent=2)
total_stats['武器故事'] = len(wp_all)
print(f'  ✅ 武器故事: {len(wp_all)} 件 (原文)')

# ============================================================
# 3. 材料描述 → 原文
# ============================================================
with open(os.path.join(DATA, 'materials.json'), encoding='utf-8') as f:
    mats = json.load(f)
out = os.path.join(RAW, '材料描述.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(mats, f, ensure_ascii=False, indent=2)
total_stats['材料描述'] = len(mats)
print(f'  ✅ 材料描述: {len(mats)} 条 (原文)')

# ============================================================
# 4. 敌人图鉴 → 原文
# ============================================================
with open(os.path.join(DATA, 'enemies.json'), encoding='utf-8') as f:
    enemies = json.load(f)
out = os.path.join(RAW, '敌人图鉴.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(enemies, f, ensure_ascii=False, indent=2)
total_stats['敌人图鉴'] = len(enemies)
print(f'  ✅ 敌人图鉴: {len(enemies)} 种 (原文)')

# ============================================================
# 5. 书籍全文 → 原文
# ============================================================
with open(os.path.join(DATA, 'books.json'), encoding='utf-8') as f:
    books = json.load(f)
out = os.path.join(RAW, '书籍全文.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
total_stats['书籍全文'] = len(books)
print(f'  ✅ 书籍全文: {len(books)} 卷 (原文)')

# ============================================================
# 6. 圣遗物故事 → 原文
# ============================================================
# Check if artifact data exists in full/
art_path = os.path.join(RAW, '圣遗物故事.json')
# Extract from kb_complete or check other source
kb_path = os.path.join(DATA, 'kb_complete.json')
if os.path.exists(kb_path):
    with open(kb_path, encoding='utf-8') as f:
        kb = json.load(f)
    artifacts = [item for item in kb if item['type'] == 'artifact']
    if artifacts:
        out = os.path.join(RAW, '圣遗物故事.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(artifacts, f, ensure_ascii=False, indent=2)
        total_stats['圣遗物故事'] = len(artifacts)
        print(f'  ✅ 圣遗物故事: {len(artifacts)} 套 (原文)')

# ============================================================
# 7. 魔神任务对话 → GenshinDialog 数据
# ============================================================
dialog_src = '/tmp/GenshinDialog/extracted_quest/quest_CHS.jsonl'
if os.path.exists(dialog_src):
    with open(dialog_src) as f:
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
                'chapter_num': cn,
                'chapter_title': ct,
                'quest_title': qt,
                'description': qd,
                'dialogues': dialogues,
            })
    
    if all_quests:
        out = os.path.join(RAW, '魔神任务对话.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(all_quests, f, ensure_ascii=False, indent=2)
        
        total_lines = sum(len(q['dialogues']) for q in all_quests)
        total_stats['魔神任务对话'] = {'章节': len(all_quests), '对白': total_lines}
        print(f'  ✅ 魔神任务对话: {len(all_quests)} 章, {total_lines} 句')

        # Also write plain text version
        out_txt = os.path.join(RAW, '魔神任务对话.txt')
        with open(out_txt, 'w', encoding='utf-8') as f:
            for q in all_quests:
                f.write(f"\n{'='*60}\n")
                f.write(f"{q['chapter_num']} - {q['chapter_title']}\n{q['quest_title']}\n")
                if q['description']:
                    f.write(f"【简介】{q['description'][:200]}\n")
                f.write(f"{'='*60}\n")
                for d in q['dialogues']:
                    f.write(f"  {d['speaker']}: {d['content']}\n")

# ============================================================
# 8. 角色档案（从 GenshinDialog avatar 提取，含 CV/命座/描述）
# ============================================================
avatar_src = '/tmp/GenshinDialog/extracted_avatar/avatar_CHS.json'
if os.path.exists(avatar_src):
    with open(avatar_src, encoding='utf-8') as f:
        avatars = json.load(f)  # dict keyed by name
    
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
        out = os.path.join(RAW, '角色档案.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        total_stats['角色档案'] = len(records)
        print(f'  ✅ 角色档案: {len(records)} 名角色 (原文)')

# ============================================================
# Summary
# ============================================================
print(f'\n{"="*50}')
print(f'📊 全量原文统计')
chars_total = 0
for k, v in sorted(total_stats.items()):
    if isinstance(v, dict):
        print(f'  {k}: {v}')
    else:
        print(f'  {k}: {v} 条')

# Total file size
total_size = sum(os.path.getsize(os.path.join(RAW, f)) for f in os.listdir(RAW) if f.endswith('.json'))
print(f'\n📁 输出: {RAW}')
print(f'💾 总大小: {total_size/1024/1024:.1f} MB')
print(f'📂 文件数: {sum(1 for f in os.listdir(RAW) if f.endswith((".json", ".txt")))}')
