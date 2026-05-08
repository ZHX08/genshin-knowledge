#!/usr/bin/env python3
"""
从 Milkve/GenshinData 提取完整任务对话原文 (v2)
修正：通过 Talk.InitDialog 链接对话，使用 NextDialogs 链式获取所有对话
"""
import json, os

# Load data
print("📖 加载数据...")
with open('/tmp/TextCHS.json') as f:
    TM = json.load(f)
def T(h):
    return TM.get(str(h), '') if isinstance(h, int) else str(h)

with open('/tmp/MainQuestExcelConfigData.json') as f:
    mqs = json.load(f)
with open('/tmp/QuestExcelConfigData.json') as f:
    quests = json.load(f)
with open('/tmp/DialogExcelConfigData.json') as f:
    dialogs = json.load(f)
with open('/tmp/TalkExcelConfigData.json') as f:
    talks = json.load(f)
with open('/tmp/ChapterExcelConfigData.json') as f:
    chs = json.load(f)

print("🔗 构建索引...")
# Dialog index by ID
dialog_by_id = {}
for d in dialogs:
    dialog_by_id[d['Id']] = d

# Talk index by ID
talk_by_id = {}
for t in talks:
    talk_by_id[t['Id']] = t

# Quest index by sub-quest ID → main quest ID
quest_sub_to_main = {}
quest_sub_info = {}
for q in quests:
    sid = q.get('SubId', 0)
    mid = q.get('MainId', 0)
    if mid:
        quest_sub_to_main.setdefault(sid, []).append(mid)
    quest_sub_info[sid] = {
        'sub_id': sid,
        'main_id': mid,
        'desc': T(q.get('DescTextMapHash', 0)),
        'step_desc': T(q.get('StepDescTextMapHash', 0)),
    }

# Collect all Talk references from quests
quest_talk_refs = set()
for q in quests:
    for cond in q.get('FinishCond', []):
        if isinstance(cond, dict) and cond.get('Type') == 'QUEST_CONTENT_COMPLETE_TALK':
            params = cond.get('Param', [])
            if params and isinstance(params[0], int):
                quest_talk_refs.add(params[0])

print(f"  Dialog: {len(dialogs)} 条")
print(f"  Talk: {len(talks)} 条")
print(f"  Quest-Talk 关联: {len(quest_talk_refs)} 个")

# For each talk ID, get the full dialog chain
def get_dialog_chain(start_id, seen=None):
    """Follow NextDialogs chain from a starting dialog ID"""
    if seen is None:
        seen = set()
    results = []
    
    def follow(did):
        if did in seen or did not in dialog_by_id:
            return
        seen.add(did)
        d = dialog_by_id[did]
        results.append({
            'id': did,
            'speaker': T(d.get('TalkRoleNameTextMapHash', 0)),
            'content': T(d.get('TalkContentTextMapHash', 0)),
        })
        for nd in d.get('NextDialogs', []):
            if isinstance(nd, int):
                follow(nd)
            elif isinstance(nd, dict):
                follow(nd.get('Id', 0))
    
    follow(start_id)
    return results

# Build dialogs per talk ID
print("\n📝 提取对话...")
talk_quest_map = {}
for tid in list(quest_talk_refs):  # Process first 1000 for speed
    talk = talk_by_id.get(tid)
    if not talk:
        continue
    init_dialog = talk.get('InitDialog', 0)
    if init_dialog:
        chain = get_dialog_chain(init_dialog)
        if chain:
            talk_quest_map[tid] = chain

print(f"  已提取 {len(talk_quest_map)} 个 Talk 的对话")

# Build main quest → dialogues mapping
# A sub-quest references a Talk, and the Talk belongs to a MainQuest
# But we need to know which MainQuest a Talk is associated with
# From Quest's MainId

# Map: main quest id → list of talk IDs
main_quest_talks = {}
for q in quests:
    sid = q.get('SubId', 0)
    mid = q.get('MainId', 0)
    if not mid:
        continue
    for cond in q.get('FinishCond', []):
        if isinstance(cond, dict) and cond.get('Type') == 'QUEST_CONTENT_COMPLETE_TALK':
            params = cond.get('Param', [])
            if params and isinstance(params[0], int):
                tid = params[0]
                if tid in talk_quest_map:
                    main_quest_talks.setdefault(mid, set()).add(tid)

# Build sub-quests per main quest
sub_by_main = {}
for q in quests:
    mid = q.get('MainId', 0)
    if mid:
        sub_by_main.setdefault(mid, []).append({
            'sub_id': q.get('SubId', 0),
            'desc': T(q.get('DescTextMapHash', 0)),
        })

print("\n📊 构建输出...")
output = []
total_lines = 0
main_with_dialog = 0

TYPE_LABELS = {'IQ': '魔神任务', 'WQ': '世界任务', 'LQ': '传说任务', 'EQ': '活动任务', '': '未知'}

for mq in mqs:
    mq_id = mq['Id']
    title = T(mq.get('TitleTextMapHash', 0)).replace('$HIDDEN','').strip()
    desc = T(mq.get('DescTextMapHash', 0)).replace('$HIDDEN','').strip()
    mq_type = mq.get('Type', '?')
    
    if not title and not desc:
        continue
    
    # Get all unique dialog lines from all talks linked to this main quest
    talk_ids = main_quest_talks.get(mq_id, set())
    all_dialogs = []
    seen_content = set()
    for tid in talk_ids:
        for d in talk_quest_map.get(tid, []):
            key = (d['speaker'], d['content'])
            if key not in seen_content:
                seen_content.add(key)
                all_dialogs.append(d)
    
    if all_dialogs:
        main_with_dialog += 1
    
    total_lines += len(all_dialogs)
    
    output.append({
        'id': mq_id,
        'type': TYPE_LABELS.get(mq_type, mq_type),
        'title': title or '(未命名)',
        'description': desc,
        'sub_quests': sub_by_main.get(mq_id, []),
        'dialogues': all_dialogs,
        'dialog_count': len(all_dialogs),
    })


# Sort: main quests with dialogue first, then by type
output.sort(key=lambda x: (-x['dialog_count'], x.get('type',''), x['id']))

# Filter: only include quests that have either title/desc or dialogue
output = [q for q in output if q['title'] != '(未命名)' or q['dialogues']]

# Calculate stats
total_chars = sum(len(d['content']) for q in output for d in q['dialogues'])
total_sub = sum(len(q['sub_quests']) for q in output)

# Write
RAW = os.path.join(os.path.dirname(__file__), 'raw')
os.makedirs(RAW, exist_ok=True)

out = os.path.join(RAW, '完整任务对话.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

txt = ''
for mq_entry in output:
    if not mq_entry['dialogues']:
        continue
    txt += f"\n{'='*60}\n"
    txt += f"[{mq_entry['type']}] {mq_entry['title']}\n"
    if mq_entry['description']:
        txt += f"【简介】{mq_entry['description'][:200]}\n"
    txt += f"【对话 {mq_entry['dialog_count']} 句, {len(mq_entry['sub_quests'])} 子任务】\n"
    txt += f"{'='*60}\n"
    for d in mq_entry['dialogues'][:60]:
        txt += f"  {d['speaker']}: {d['content']}\n"
    if len(mq_entry['dialogues']) > 60:
        txt += f"  ... 还有 {len(mq_entry['dialogues'])-60} 句\n"

out_txt = os.path.join(RAW, '完整任务对话.txt')
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write(txt)

# Stats by type
from collections import Counter
type_counts = Counter(q['type'] for q in output if q['dialogues'])
type_lines = {}
for q in output:
    t = q['type']
    type_lines[t] = type_lines.get(t, 0) + q['dialog_count']

print(f"\n{'='*50}")
print("📊 任务对话统计")
print(f"  总主任务数: {len(output)}")
print(f"  含对话的主任务: {main_with_dialog} (总对话 {total_lines:,} 句, {total_chars:,} 字符)")
print(f"  总字符: {total_chars/10000:.1f} 万字")
print(f"  总子任务: {total_sub}")
print()
for t in sorted(type_counts.keys()):
    print(f"  {t:<10} {type_counts[t]:>4} 个任务, {type_lines.get(t,0):>6} 句对话")
print(f"\n  📁 {out}")
print(f"  📁 {out_txt}")
