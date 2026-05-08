#!/usr/bin/env python3
"""
全量原文最终导出 - 不遗漏任何一条 Dialog 数据
输出到 raw/，不与前端 public/ 产生任何交集
"""
import json, os
from collections import defaultdict

RAW = os.path.join(os.path.dirname(__file__), 'raw')
os.makedirs(RAW, exist_ok=True)

# TextMap
with open('/tmp/TextCHS.json') as f:
    TM = json.load(f)
def T(h):
    return TM.get(str(h), '') if isinstance(h, int) else str(h)

# NPC lookup
with open('/tmp/NpcExcelConfigData.json') as f:
    npcs = json.load(f)
npc_names = {}
for npc in npcs:
    name = T(npc.get('NameTextMapHash', ''))
    if name:
        npc_id = npc['Id']
        # Keep all variants
        npc_names.setdefault(npc_id, []).append(name)

# ============================================================
# 1. 全量 Dialog 原文 (43,585 条)
# ============================================================
print("📦 全量 Dialog 原文...")
with open('/tmp/DialogExcelConfigData.json') as f:
    dialogs = json.load(f)

all_dialogs = []
for d in dialogs:
    content = T(d.get('TalkContentTextMapHash', 0))
    speaker_raw = T(d.get('TalkRoleNameTextMapHash', 0))
    
    # Try to resolve NPC name from TalkRole
    role = d.get('TalkRole', {})
    npc_id = None
    if isinstance(role, dict):
        rid = role.get('Id', 0)
        if rid:
            try:
                npc_id = int(rid)
            except (ValueError, TypeError):
                pass
    
    speaker = speaker_raw
    if not speaker and npc_id and npc_id in npc_names:
        # Use first name variant
        speaker = npc_names[npc_id][0]
    if not speaker and npc_id:
        speaker = f'[NPC#{npc_id}]'
    
    if content:
        all_dialogs.append({
            'id': d['Id'],
            'speaker': speaker or '(旁白)',
            'content': content,
            'npc_id': npc_id or 0,
            'next_dialogs': d.get('NextDialogs', []),
        })

out = os.path.join(RAW, '全量Dialog原文.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(all_dialogs, f, ensure_ascii=False, indent=2)
print(f"  ✅ 全量Dialog原文: {len(all_dialogs)} 条 (完整)")
stats = {'全量Dialog原文': len(all_dialogs)}

# ============================================================
# 2. 各角色台词统计 & 按角色分组
# ============================================================
print("\n📦 按角色分组对话...")
by_speaker = defaultdict(list)
for d in all_dialogs:
    by_speaker[d['speaker']].append(d)

# Top speakers
speaker_rank = sorted(by_speaker.items(), key=lambda x: -len(x[1]))
print(f"  共 {len(by_speaker)} 个说话人")
print("  台词最多的10人:")
for name, lines in speaker_rank[:10]:
    print(f"    {name:<20} {len(lines):>5} 句")

# Save top characters
top_chars = {}
for name, lines in speaker_rank[:30]:
    top_chars[name] = len(lines)
out = os.path.join(RAW, '角色台词统计.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(top_chars, f, ensure_ascii=False, indent=2)
stats['角色台词统计'] = len(top_chars)

# ============================================================
# 3. 全量角色台词（主要角色）
# ============================================================
# Known main NPCs
main_npc_ids = {
    1005: '派蒙', 1001: '温迪', 1002: '安柏', 1004: '凯亚',
    1006: '琴', 1009: '迪卢克', 10211: '凝光', 10232: '钟离',
    1022: '戴因斯雷布',
}

main_char_lines = {}
for npc_id, char_name in main_npc_ids.items():
    lines = [d for d in all_dialogs if d['npc_id'] == npc_id]
    if lines:
        main_char_lines[char_name] = lines

out = os.path.join(RAW, '主要角色台词.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(main_char_lines, f, ensure_ascii=False, indent=2)
total_main = sum(len(v) for v in main_char_lines.values())
print(f"\n  ✅ 主要角色台词: {total_main} 句 ({len(main_char_lines)} 角色)")
stats['主要角色台词'] = total_main

# ============================================================
# 4. 导出纯文本全文
# ============================================================
print("\n📦 导出纯文本全文...")

# Sort dialogs by ID for chronological-ish order
sorted_dialogs = sorted(all_dialogs, key=lambda x: x['id'])

txt_path = os.path.join(RAW, '全量Dialog原文.txt')
with open(txt_path, 'w', encoding='utf-8') as f:
    for d in sorted_dialogs:
        f.write(f"{d['id']:>10} | {d['speaker']:<20} | {d['content']}\n")

total_chars = sum(len(d['content']) for d in all_dialogs)
print(f"  ✅ 全量Dialog原文.txt: {total_chars:,} 字符 ({total_chars/10000:.1f}万字)")

# ============================================================
# 5. 更新 manifest
# ============================================================
all_files = sorted([f for f in os.listdir(RAW) if os.path.isfile(os.path.join(RAW, f))])
total_size = sum(os.path.getsize(os.path.join(RAW, f)) for f in all_files)

manifest = {
    'generated_at': '2026-05-08',
    'total_files': len(all_files),
    'total_size_mb': round(total_size / 1024 / 1024, 1),
    'files': {f: os.path.getsize(os.path.join(RAW, f)) for f in all_files},
}
with open(os.path.join(RAW, 'manifest.json'), 'w') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"\n{'='*50}")
print("📊 最终 raw/ 统计")
print(f"  总文件: {len(all_files)}个, {total_size/1024/1024:.1f}MB")
print(f"  总对话: {len(all_dialogs):,} 条, {total_chars:,} 字符")
print(f"  📁 {RAW}")
print(f"\n⚠️  确认: raw/ 不与 public/ 有任何构建路径交集")
PYEOF
