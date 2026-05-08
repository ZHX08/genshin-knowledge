#!/usr/bin/env python3
"""Fetch character friendship stories from bilibili wiki (action=raw) and save as JSON."""
import urllib.request
import urllib.parse
import re
import json
import html
import time
import os

BASE_URL = "https://wiki.biligame.com/ys/index.php?title={}&action=raw"
TARGET_FIELDS = ['角色详细', '角色故事1', '角色故事2', '角色故事3', '角色故事4', '角色故事5', '神之眼']


def region_to_file(region):
    mapping = {
        "蒙德": "mondstadt",
        "璃月": "liyue",
        "稻妻": "inazuma",
        "须弥": "sumeru",
        "枫丹": "fontaine",
        "纳塔": "natlan",
        "挪德卡莱": "nod_krai",
        "其他": "other",
    }
    return mapping.get(region, region)


def url_encode_name(name):
    return urllib.parse.quote(name)


def clean_wiki_text(text):
    text = html.unescape(text)
    # Keep display text from common templates before removing remaining templates
    text = re.sub(r'\{\{颜色\|[^|{}]*\|([^{}]+)\}\}', r'\1', text)
    text = re.sub(r'\{\{黑幕\|([^{}]+)\}\}', r'\1', text)
    text = re.sub(r'\{\{图标\|[^|{}]*\|([^{}]+)\}\}', r'\1', text)
    text = re.sub(r'\{\{[^{}]*?\|([^{}|]+)\}\}', r'\1', text)
    while '{{' in text and '}}' in text:
        new_text = re.sub(r'\{\{[^{}]*\}\}', '', text)
        if new_text == text:
            break
        text = new_text
    text = re.sub(r'\[\[([^\]|]*)\|([^\]]*)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    text = re.sub(r"''+", '', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'^\s*\|+', '', text)
    text = re.sub(r'\|+\s*$', '', text)
    text = text.replace('\\n', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def extract_story_template(raw_text):
    start = raw_text.find('{{角色/故事')
    if start == -1:
        return None
    end = raw_text.find('\n}}', start)
    if end == -1:
        end = raw_text.find('}}', start)
        if end == -1:
            return None
        end += 2
    else:
        end += 3
    return raw_text[start:end]


def extract_all_stories(raw_text):
    template = extract_story_template(raw_text)
    if not template:
        return {}
    stories = {}
    current_field = None
    buf = []
    for line in template.splitlines()[1:]:
        if line.strip() == '}}':
            break
        if line.startswith('|'):
            field, sep, value = line[1:].partition('=')
            field = field.strip()
            if sep and field in TARGET_FIELDS:
                if current_field is not None:
                    stories[current_field] = clean_wiki_text('\n'.join(buf))
                current_field = field
                buf = [value]
                continue
            elif sep:
                if current_field is not None:
                    stories[current_field] = clean_wiki_text('\n'.join(buf))
                current_field = None
                buf = []
                continue
        if current_field is not None:
            buf.append(line)
    if current_field is not None:
        stories[current_field] = clean_wiki_text('\n'.join(buf))
    return {k: v for k, v in stories.items() if v}


def fetch_character_raw(name):
    url = BASE_URL.format(url_encode_name(name))
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"  ERROR fetching {name}: {e}")
        return None


def make_friendship_entry(character_name, region, story_type, content):
    return {
        "type": "character_friendship",
        "title": f"{character_name} · {story_type}",
        "content": content,
        "source": f"好感度文本·{character_name}",
        "metadata": {
            "region": region,
            "story_type": story_type
        }
    }


CHARACTERS = {
    "蒙德": [
        ("温迪", "温迪"), ("琴", "琴"), ("凯亚", "凯亚"), ("安柏", "安柏"), ("丽莎", "丽莎"),
        ("迪卢克", "迪卢克"), ("可莉", "可莉"), ("芭芭拉", "芭芭拉"), ("班尼特", "班尼特"), ("诺艾尔", "诺艾尔"),
        ("菲谢尔", "菲谢尔"), ("砂糖", "砂糖"), ("莫娜", "莫娜"), ("雷泽", "雷泽"), ("阿贝多", "阿贝多"),
        ("优菈", "优菈"), ("米卡", "米卡"), ("罗莎莉亚", "罗莎莉亚"), ("法尔伽", "法尔伽"), ("杜林", "杜林"), ("艾莉丝", "艾莉丝"),
        ("迪奥娜", "迪奥娜"),
    ],
    "璃月": [
        ("钟离", "钟离"), ("刻晴", "刻晴"), ("魈", "魈"), ("凝光", "凝光"), ("甘雨", "甘雨"), ("胡桃", "胡桃"),
        ("行秋", "行秋"), ("重云", "重云"), ("香菱", "香菱"), ("北斗", "北斗"), ("七七", "七七"), ("申鹤", "申鹤"),
        ("夜兰", "夜兰"), ("辛焱", "辛焱"), ("云堇", "云堇"), ("白术", "白术"), ("烟绯", "烟绯"), ("瑶瑶", "瑶瑶"),
        ("闲云", "闲云"), ("蓝砚", "蓝砚"),
    ],
    "稻妻": [
        ("雷电将军", "雷电将军"), ("神里绫华", "神里绫华"), ("枫原万叶", "枫原万叶"), ("宵宫", "宵宫"), ("托马", "托马"),
        ("九条裟罗", "九条裟罗"), ("荒泷一斗", "荒泷一斗"), ("珊瑚宫心海", "珊瑚宫心海"), ("五郎", "五郎"), ("八重神子", "八重神子"),
        ("神里绫人", "神里绫人"), ("早柚", "早柚"), ("久岐忍", "久岐忍"), ("鹿野院平藏", "鹿野院平藏"), ("绮良良", "绮良良"),
    ],
    "须弥": [
        ("纳西妲", "纳西妲"), ("赛诺", "赛诺"), ("妮露", "妮露"), ("提纳里", "提纳里"), ("柯莱", "柯莱"), ("多莉", "多莉"),
        ("坎蒂丝", "坎蒂丝"), ("艾尔海森", "艾尔海森"), ("卡维", "卡维"), ("流浪者", "流浪者"), ("珐露珊", "珐露珊"), ("莱依拉", "莱依拉"), ("迪希雅", "迪希雅"),
        ("赛索斯", "赛索斯"),
    ],
    "枫丹": [
        ("芙宁娜", "芙宁娜"), ("那维莱特", "那维莱特"), ("莱欧斯利", "莱欧斯利"), ("希格雯", "希格雯"), ("林尼", "林尼"), ("琳妮特", "琳妮特"),
        ("菲米尼", "菲米尼"), ("娜维娅", "娜维娅"), ("夏沃蕾", "夏沃蕾"), ("克洛琳德", "克洛琳德"), ("千织", "千织"), ("阿蕾奇诺", "阿蕾奇诺"), ("嘉明", "嘉明"), ("桑多涅", "桑多涅"),
        ("夏洛蒂", "夏洛蒂"), ("艾梅莉埃", "艾梅莉埃"),
    ],
    "纳塔": [
        ("玛拉妮", "玛拉妮"), ("卡齐娜", "卡齐娜"), ("基尼奇", "基尼奇"), ("希诺宁", "希诺宁"), ("恰斯卡", "恰斯卡"), ("欧洛伦", "欧洛伦"),
        ("茜特菈莉", "茜特菈莉"), ("玛薇卡", "玛薇卡"), ("瓦雷莎", "瓦雷莎"), ("伊安珊", "伊安珊"), ("伊法", "伊法"), ("丝柯克", "丝柯克"),
    ],
    "挪德卡莱": [
        ("菈乌玛", "菈乌玛"), ("菲林斯", "菲林斯"), ("爱诺", "爱诺"), ("伊涅芙", "伊涅芙"), ("奈芙尔", "奈芙尔"), ("雅珂达", "雅珂达"), ("叶洛亚", "叶洛亚"),
    ],
    "其他": [
        ("哥伦比娅", "哥伦比娅"), ("尼可·莱恩", "尼可·莱恩"),
        ("达达利亚", "达达利亚"), ("埃洛伊", "埃洛伊"),
    ],
}


def process_region(region, characters):
    print(f"\n{'=' * 60}")
    print(f"Region: {region} ({len(characters)} characters)")
    print('=' * 60)
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
    return all_entries


if __name__ == "__main__":
    output_dir = "/root/.openclaw-zhx/workspace/projects/genshin-knowledge/knowledge_data"
    os.makedirs(output_dir, exist_ok=True)
    all_region_data = {}
    total = 0
    for region, characters in CHARACTERS.items():
        entries = process_region(region, characters)
        if entries:
            filename = os.path.join(output_dir, f"character_friendship_{region_to_file(region)}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            all_region_data[region] = filename
            total += len(entries)
            print(f"\n  Saved {len(entries)} entries to {filename}")
    print(f"\n{'=' * 60}")
    print(f"Total: {total} friendship entries across {len(all_region_data)} regions")
    print(f"{'=' * 60}")
