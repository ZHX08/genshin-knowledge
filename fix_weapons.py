# -*- coding: utf-8 -*-
"""Fix weapon region classification."""
import json
import os

wd = '/root/.openclaw-zhx/workspace/projects/genshin-knowledge/knowledge_data'

# Reload all files
with open(os.path.join(wd, 'weapons_mondstadt.json')) as f:
    mond = json.load(f)
with open(os.path.join(wd, 'weapons_liyue.json')) as f:
    liyue = json.load(f)
with open(os.path.join(wd, 'weapons_sumeru.json')) as f:
    sumeru = json.load(f)

# Titles that should be in Liyue
liyue_titles = {'以理服人','黑缨枪','琥珀玥','沉玉之弓','翡玉法球','翡玉环','讨龙英杰谭','血玉之环','口袋魔导书','铁尖枪'}
# Titles that should be in Sumeru
sumeru_titles = {'魔导绪论'}

# Move from mondstadt to correct files
moved_to_liyue = []
moved_to_sumeru = []
new_mond = []
for w in mond:
    if w['title'] in liyue_titles:
        liyue.append(w)
        moved_to_liyue.append(w['title'])
    elif w['title'] in sumeru_titles:
        sumeru.append(w)
        moved_to_sumeru.append(w['title'])
    else:
        new_mond.append(w)

mond = new_mond

# Write back
with open(os.path.join(wd, 'weapons_mondstadt.json'), 'w') as f:
    json.dump(mond, f, ensure_ascii=False, indent=2)
with open(os.path.join(wd, 'weapons_liyue.json'), 'w') as f:
    json.dump(liyue, f, ensure_ascii=False, indent=2)
with open(os.path.join(wd, 'weapons_sumeru.json'), 'w') as f:
    json.dump(sumeru, f, ensure_ascii=False, indent=2)

print(f'Moved to Liyue: {moved_to_liyue}')
print(f'Moved to Sumeru: {moved_to_sumeru}')
print(f'Mondstadt now has: {len(mond)} weapons')
print(f'Liyue now has: {len(liyue)} weapons')
print(f'Sumeru now has: {len(sumeru)} weapons')
