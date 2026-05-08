#!/usr/bin/env python3
"""Fetch ONLY the 8 missing characters' friendship stories."""
import json, sys, os, re, html, urllib.request, urllib.parse, time

BASE_URL = "https://wiki.biligame.com/ys/index.php?title={}&action=raw"
TARGET_FIELDS = ['角色详细', '角色故事1', '角色故事2', '角色故事3', '角色故事4', '角色故事5', '神之眼']

# Prepend fetch_stories.py directory to import its functions
sys.path.insert(0, os.path.dirname(__file__))
from fetch_stories import (clean_wiki_text, extract_story_template, 
                           extract_all_stories, fetch_character_raw, 
                           make_friendship_entry, region_to_file)

# Only the 8 missing characters
NEW_CHARACTERS = {
    "蒙德": [("迪奥娜", "迪奥娜")],
    "璃月": [("闲云", "闲云"), ("蓝砚", "蓝砚")],
    "须弥": [("赛索斯", "赛索斯")],
    "枫丹": [("夏洛蒂", "夏洛蒂"), ("艾梅莉埃", "艾梅莉埃")],
    "其他": [("达达利亚", "达达利亚"), ("埃洛伊", "埃洛伊")],
}

output_dir = "/root/.openclaw-zhx/workspace/projects/genshin-knowledge/knowledge_data"

for region, characters in NEW_CHARACTERS.items():
    print(f"\n{'='*60}")
    print(f"Region: {region} ({len(characters)} characters)")
    print('='*60)
    all_entries = []
    for display_name, wiki_name in characters:
        print(f"\n  Fetching: {display_name} ({wiki_name})...")
        raw_text = fetch_character_raw(wiki_name)
        if not raw_text:
            print(f"  SKIPPED: {display_name}")
            continue
        stories = extract_all_stories(raw_text)
        if not stories:
            print(f"  NO STORIES FOUND for {display_name}")
            continue
        print(f"  Found {len(stories)} story fields: {list(stories.keys())}")
        for story_type in TARGET_FIELDS:
            content = stories.get(story_type)
            if content and len(content) > 20:
                all_entries.append(make_friendship_entry(display_name, region, story_type, content))
                print(f"    {story_type}: {len(content)} chars")
        time.sleep(0.25)
    
    if all_entries:
        # Append to existing file
        fname = os.path.join(output_dir, f"character_friendship_{region_to_file(region)}.json")
        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            existing.extend(all_entries)
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            print(f"  Added {len(all_entries)} entries to {fname} (total: {len(existing)})")
        else:
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, ensure_ascii=False, indent=2)
            print(f"  Created {fname} with {len(all_entries)} entries")

print(f"\n{'='*60}")
print("Done fetching missing characters!")
