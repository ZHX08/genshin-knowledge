import json, glob

wd = '/root/.openclaw-zhx/workspace/projects/genshin-knowledge'
data_dir = wd + '/knowledge_data'

all_data = []
seen = set()  # track (type, title) pairs

for f in sorted(glob.glob(data_dir + '/*.json')):
    bn = f.split('/')[-1]
    if bn in ('kb_complete.json', 'graph_data.json'):
        continue
    with open(f) as fp:
        data = json.load(fp)
    count_before = len(data)
    unique_items = []
    for item in data:
        key = (item.get('type',''), item.get('title',''))
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    all_data.extend(unique_items)
    deduped = count_before - len(unique_items)
    print(f'{bn}: {len(unique_items)} items (removed {deduped} dupes)')

with open(data_dir + '/kb_complete.json', 'w') as fp:
    json.dump(all_data, fp, ensure_ascii=False, indent=2)

print(f'\nTotal: {len(all_data)} items')
