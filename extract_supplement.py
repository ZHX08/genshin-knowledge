#!/usr/bin/env python3
"""
补充提取：未覆盖的对话 + 全量材料文本
"""
import json, os, subprocess

DOWNLOAD_DIR = '/tmp'
TF = os.path.join(DOWNLOAD_DIR, 'TextCHS.json')
with open(TF) as f:
    TM = json.load(f)
def T(h):
    return TM.get(str(h), '') if isinstance(h, int) else str(h)

def dl(name):
    """Download a file from Milkve/GenshinData if not present"""
    path = os.path.join(DOWNLOAD_DIR, name)
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        url = f"https://api.github.com/repos/Milkve/GenshinData/contents/ExcelBinOutput/{name}"
        subprocess.run(['curl', '-s', url, '-H', 'Accept: application/vnd.github.raw+json',
                       '-o', path, '--max-time', '30'], check=True)
        print(f"  Downloaded {name}: {os.path.getsize(path)/1024:.0f} KB")
    return path

RAW = '/root/.openclaw-zhx/workspace/projects/genshin-knowledge/raw'
os.makedirs(RAW, exist_ok=True)

# ============================================================
# 1. 全量材料文本
# ============================================================
print("\n📦 全量材料文本...")
mt_path = dl('MaterialExcelConfigData.json')
with open(mt_path) as f:
    mats = json.load(f)

# Resolve material names and descriptions
material_list = []
for m in mats:
    name = T(m.get('NameTextMapHash', 0))
    desc = T(m.get('DescTextMapHash', 0))
    mat_type = m.get('MaterialType', '')
    rank = m.get('RankLevel', 0)
    if name or desc:
        material_list.append({
            'id': m['Id'],
            'name': name,
            'description': desc,
            'type': mat_type,
            'rank': rank,
        })

out = os.path.join(RAW, '全量材料描述.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(material_list, f, ensure_ascii=False, indent=2)
print(f"  ✅ 全量材料: {len(material_list)} 条 (之前: 741)")

# ============================================================
# 2. 全量武器文本
# ============================================================
print("\n📦 全量武器文本...")
wp_path = dl('WeaponExcelConfigData.json')
with open(wp_path) as f:
    wps = json.load(f)

weapon_list = []
for w in wps:
    name = T(w.get('NameTextMapHash', 0))
    desc = T(w.get('DescTextMapHash', 0))
    wp_type = w.get('WeaponType', '')
    rank = w.get('RankLevel', 0)
    if name or desc:
        weapon_list.append({
            'id': w['Id'],
            'name': name,
            'description': desc,
            'type': wp_type,
            'rank': rank,
        })

out = os.path.join(RAW, '全量武器文本.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(weapon_list, f, ensure_ascii=False, indent=2)
print(f"  ✅ 全量武器: {len(weapon_list)} 把")

# ============================================================
# 3. 全量圣遗物文本
# ============================================================
print("\n📦 全量圣遗物文本...")
rl_path = dl('ReliquaryExcelConfigData.json')
with open(rl_path) as f:
    rls = json.load(f)

relic_list = []
for r in rls:
    name = T(r.get('NameTextMapHash', 0))
    desc = T(r.get('DescTextMapHash', 0))
    equip_type = r.get('EquipType', '')
    rank = r.get('RankLevel', 0)
    if name or desc:
        relic_list.append({
            'id': r['Id'],
            'name': name,
            'set_id': r.get('SetId', 0),
            'description': desc,
            'equip_type': equip_type,
            'rank': rank,
        })

# Group by set
from collections import defaultdict
sets = defaultdict(list)
for r in relic_list:
    sets[r['set_id']].append(r)

out = os.path.join(RAW, '全量圣遗物文本.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(relic_list, f, ensure_ascii=False, indent=2)
print(f"  ✅ 全量圣遗物: {len(relic_list)} 件 ({len(sets)} 套)")

# ============================================================
# 4. 补充对话提取 - 从所有 Talk 中提取（不限于 COMPLETE_TALK 关联）
# ============================================================
print("\n📦 补充对话提取...")

with open(os.path.join(DOWNLOAD_DIR, 'TalkExcelConfigData.json')) as f:
    talks = json.load(f)
with open(os.path.join(DOWNLOAD_DIR, 'DialogExcelConfigData.json')) as f:
    dialogs = json.load(f)

dialog_by_id = {d['Id']: d for d in dialogs}

def get_chain(start_id, seen=None):
    if seen is None:
        seen = set()
    results = []
    def follow(did):
        if did in seen or did not in dialog_by_id:
            return
        seen.add(did)
        d = dialog_by_id[did]
        results.append({
            'speaker': T(d.get('TalkRoleNameTextMapHash', 0)),
            'content': T(d.get('TalkContentTextMapHash', 0)),
        })
        for nd in d.get('NextDialogs', []):
            if isinstance(nd, int):
                follow(nd)
    follow(start_id)
    return results

# Extract ALL talk dialogues
all_talk_dialogs = []
for t in talks:
    init_d = t.get('InitDialog', 0)
    if init_d and init_d in dialog_by_id:
        chain = get_chain(init_d)
        if chain:
            all_talk_dialogs.append({
                'talk_id': t['Id'],
                'init_dialog': init_d,
                'dialogues': chain,
            })

total_from_talks = sum(len(td['dialogues']) for td in all_talk_dialogs)
print(f"  ✅ 全量Talk对话: {len(all_talk_dialogs)} 组, {total_from_talks} 句")

out = os.path.join(RAW, '全量对话数据(按Talk).json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(all_talk_dialogs, f, ensure_ascii=False, indent=2)

# ============================================================
# 5. 全量角色文本（含天赋、命座）
# ============================================================
print("\n📦 全量角色文本...")
av_path = dl('AvatarExcelConfigData.json')
with open(av_path) as f:
    avatars = json.load(f)

# Also get skill/talent text
skill_path = dl('AvatarSkillExcelConfigData.json')
with open(skill_path) as f:
    skills = json.load(f)

avatar_list = []
for av in avatars:
    avatar_list.append({
        'id': av['Id'],
        'name': T(av.get('NameTextMapHash', 0)),
        'desc': T(av.get('DescTextMapHash', 0)),
    })

out = os.path.join(RAW, '全量角色文本.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(avatar_list, f, ensure_ascii=False, indent=2)
print(f"  ✅ 全量角色: {len(avatar_list)} 名")

# Skill text
skill_list = []
for sk in skills:
    skill_list.append({
        'id': sk['Id'],
        'name': T(sk.get('NameTextMapHash', 0)),
        'desc': T(sk.get('DescTextMapHash', 0)),
    })

out = os.path.join(RAW, '全量技能文本.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(skill_list, f, ensure_ascii=False, indent=2)
print(f"  ✅ 全量技能: {len(skill_list)} 个")

# ============================================================
# Summary
# ============================================================
print(f"\n{'='*50}")
print("📊 补充提取统计")
char_count = 0
for f in sorted(os.listdir(RAW)):
    if f.endswith('.json') and not f.startswith('manifest'):
        fp = os.path.join(RAW, f)
        sz = os.path.getsize(fp)
        char_count += sz
        print(f"  {f:<30} {sz/1024:.0f} KB")

total_mb = sum(os.path.getsize(os.path.join(RAW, f)) for f in os.listdir(RAW) if f.endswith(('.json','.txt')))
print(f"\n📁 raw/ 总量: {total_mb/1024/1024:.1f} MB")
print(f"📂 文件数: {len([f for f in os.listdir(RAW) if f.endswith(('.json','.txt'))])}")
