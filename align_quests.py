#!/usr/bin/env python3
"""
完整对齐：全部主线(IQ) + 世界任务(WQ) 对话文本
通过 COMPLETE_TALK + FINISH_PLOT 双重链接
"""
import json, os
from collections import defaultdict

with open('/tmp/TextCHS.json') as f:
    TM = json.load(f)
def T(h):
    return TM.get(str(h), '') if isinstance(h, int) else str(h)

# Load data
with open('/tmp/MainQuestExcelConfigData.json') as f:
    mqs = json.load(f)
with open('/tmp/QuestExcelConfigData.json') as f:
    quests = json.load(f)
with open('/tmp/TalkExcelConfigData.json') as f:
    talks = json.load(f)
with open('/tmp/DialogExcelConfigData.json') as f:
    dialogs = json.load(f)

# Build indexes
talk_by_id = {t['Id']: t for t in talks}
dialog_by_id = {d['Id']: d for d in dialogs}

# All talk IDs that exist
valid_talk_ids = set(talk_by_id.keys())
valid_dialog_ids = set(dialog_by_id.keys())

print(f"📊 数据总量:")
print(f"  Dialog: {len(dialogs)}")
print(f"  Talk: {len(talks)}")
print(f"  Quest: {len(quests)}")
print(f"  MainQuest: {len(mqs)}")

# Step 1: For each sub-quest, find ALL dialog references
# Map: sub-quest ID → set of Talk IDs referenced
sub_quest_talks = defaultdict(set)

for q in quests:
    sid = q.get('SubId', 0)
    for cond in q.get('FinishCond', []):
        if not isinstance(cond, dict):
            continue
        ct = cond.get('Type', '')
        params = cond.get('Param', [])
        if not params or not isinstance(params[0], int):
            continue
        tid = params[0]
        
        # COMPLETE_TALK directly references Talk IDs
        if ct == 'QUEST_CONTENT_COMPLETE_TALK' and tid in valid_talk_ids:
            sub_quest_talks[sid].add(tid)
        
        # FINISH_PLOT may also reference Talk IDs  
        if ct == 'QUEST_CONTENT_FINISH_PLOT' and tid in valid_talk_ids:
            sub_quest_talks[sid].add(tid)

# Step 2: Map sub-quest → main quest
sub_to_main = {}
for q in quests:
    sid = q.get('SubId', 0)
    mid = q.get('MainId', 0)
    if mid:
        sub_to_main[sid] = mid

# Step 3: Collect sub-quest info
sub_info = {}
for q in quests:
    sid = q.get('SubId', 0)
    sub_info[sid] = {
        'sub_id': sid,
        'desc': T(q.get('DescTextMapHash', 0)),
        'step_desc': T(q.get('StepDescTextMapHash', 0)),
    }

# Step 4: Extract dialog chains for each talk
def get_dialog_chain(start_id, seen=None):
    if seen is None:
        seen = set()
    results = []
    def follow(did):
        if did in seen or did not in dialog_by_id:
            return
        seen.add(did)
        d = dialog_by_id[did]
        results.append(d)
        for nd in d.get('NextDialogs', []):
            if isinstance(nd, int):
                follow(nd)
            elif isinstance(nd, dict):
                follow(nd.get('Id', 0))
    follow(start_id)
    return results

# Pre-compute all talk dialog chains
talk_dialog_chains = {}
print("\n🔗 提取对话链...")
for tid in valid_talk_ids:
    t = talk_by_id[tid]
    init_d = t.get('InitDialog', 0)
    if init_d in valid_dialog_ids:
        chain = get_dialog_chain(init_d)
        if chain:
            talk_dialog_chains[tid] = chain

# Step 5: Build main quest output
print("📝 构建输出...")
output = []
total_dialogs = 0
total_quests_with_dialog = 0

# Process IQ and WQ only
TYPE_LABELS = {'IQ': '魔神任务', 'WQ': '世界任务', 'LQ': '传说任务', 'EQ': '活动任务'}
target_types = {'IQ', 'WQ'}

for mq in mqs:
    mid = mq['Id']
    mq_type = mq.get('Type', '?')
    if mq_type not in target_types:
        continue
    
    title = T(mq.get('TitleTextMapHash', 0)).replace('$HIDDEN', '').strip()
    desc = T(mq.get('DescTextMapHash', 0)).replace('$HIDDEN', '').strip()
    
    # Find all sub-quests for this main quest
    sub_ids = [q.get('SubId', 0) for q in quests if q.get('MainId', 0) == mid]
    
    # Collect all Talk IDs referenced by any sub-quest
    talk_ids_for_mq = set()
    for sid in sub_ids:
        talk_ids_for_mq.update(sub_quest_talks.get(sid, set()))
    
    # Extract unique dialog lines
    all_dialogs = []
    seen = set()
    for tid in talk_ids_for_mq:
        chain = talk_dialog_chains.get(tid, [])
        for d in chain:
            speaker = T(d.get('TalkRoleNameTextMapHash', 0))
            content = T(d.get('TalkContentTextMapHash', 0))
            if content:
                key = (speaker, content[:100])
                if key not in seen:
                    seen.add(key)
                    all_dialogs.append({
                        'speaker': speaker,
                        'content': content,
                    })
    
    if all_dialogs:
        total_quests_with_dialog += 1
    total_dialogs += len(all_dialogs)
    
    output.append({
        'id': mid,
        'type': TYPE_LABELS.get(mq_type, mq_type),
        'title': title or '(未命名)',
        'description': desc,
        'sub_count': len(sub_ids),
        'talk_count': len(talk_ids_for_mq),
        'dialogues': all_dialogs,
    })

# Sort: quests with dialogs first, then by title
output.sort(key=lambda x: (-len(x['dialogues']), x['title']))

# Count by type
from collections import Counter
type_counts = Counter(q['type'] for q in output)
type_with_dialog = Counter(q['type'] for q in output if q['dialogues'])

# Write
RAW = os.path.join(os.path.dirname(__file__), 'raw')
os.makedirs(RAW, exist_ok=True)

out = os.path.join(RAW, '主线世界任务对话.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Write plain text
txt = ''
for entry in output:
    if not entry['dialogues']:
        continue
    txt += f"\n{'='*60}\n"
    txt += f"[{entry['type']}] {entry['title']}\n"
    if entry['description']:
        txt += f"【简介】{entry['description'][:200]}\n"
    txt += f"【{len(entry['dialogues'])} 句对话, {entry['sub_count']} 子任务, {entry['talk_count']} 个Talk】\n"
    txt += f"{'='*60}\n"
    for d in entry['dialogues'][:80]:
        txt += f"  {d['speaker']}: {d['content']}\n"
    if len(entry['dialogues']) > 80:
        txt += f"  ... 还有 {len(entry['dialogues'])-80} 句\n"

# Fix: entry may not have dialog_count key
# Let me recalculate
for entry in output:
    entry['dialog_count'] = len(entry['dialogues'])

out_txt = os.path.join(RAW, '主线世界任务对话.txt')
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write(txt)

# Stats
total_chars = sum(len(d['content']) for entry in output for d in entry['dialogues'])
total_with = sum(1 for entry in output if entry['dialogues'])
total_without = sum(1 for entry in output if not entry['dialogues'])

print(f"\n{'='*50}")
print("📊 主线+世界任务对齐统计")
for t in ['魔神任务', '世界任务']:
    total = type_counts.get(t, 0)
    has = type_with_dialog.get(t, 0)
    pct = has/total*100 if total else 0
    print(f"  {t}: {has}/{total} ({pct:.0f}%)")
print(f"  含对话总数: {total_with}/{len(output)}")
print(f"  无对话: {total_without} (多为 test/$UNRELEASED)")
print(f"\n  总对话句数: {total_dialogs:,}")
print(f"  总字符数: {total_chars:,} ({total_chars/10000:.1f}万字)")
print(f"\n  📁 {out}")
print(f"  📁 {out_txt}")
PYEOF
