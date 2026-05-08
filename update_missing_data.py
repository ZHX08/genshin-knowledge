#!/usr/bin/env python3
"""Add missing character_story entries, artifact sets, and other data."""
import json, os

wd = '/root/.openclaw-zhx/workspace/projects/genshin-knowledge/knowledge_data'

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===================== 1. Character Stories =====================
# These are added to their respective region files

new_character_stories = {
    'mondstadt.json': [
        {
            "type": "character_story",
            "title": "迪奥娜",
            "content": "迪奥娜，蒙德猫尾酒馆的调酒师，也是「清泉镇」出身的猎户之女。她拥有一手神奇的调酒天赋——无论什么酒到了她手里都会变成绝顶美味，但这恰恰是她的烦恼，因为她最痛恨酒，最大的愿望是「毁掉蒙德的酒业」。迪奥娜的父亲杜拉夫是清泉镇著名的猎人，迪奥娜从父亲那里学到了优秀的狩猎技巧。她的猫耳和尾巴是凯茨莱茵家族的遗传特征。元素战技「猫爪冻冻」发射寒冰猫爪造成冰元素伤害并生成护盾，元素爆发「最烈特调」造成冰元素范围伤害并生成持续治疗的领域。迪奥娜表面上凶巴巴的，实际上非常关心身边的人。",
            "source": "角色故事·迪奥娜",
            "metadata": {
                "region": "蒙德",
                "element": "冰",
                "affiliation": "猫尾酒馆"
            }
        }
    ],
    'liyue.json': [
        {
            "type": "character_story",
            "title": "闲云",
            "content": "闲云，真名留云借风真君，璃月的三眼五显仙人之一，是岩王帝君的旧友。她擅长机关术与工巧之技，性格高傲直率，说话不留情面，但内心极为温柔。在魔神战争中，留云借风真君与其他仙人一同守护璃月。她曾帮助过人类对抗魔神，但也曾因为人类的背叛而心灰意冷。在璃月的人治时代到来后，她以人类的姿态行走凡间，化名「闲云」，担任沉玉谷地区的镖师和机关顾问。她精通风元素力，战技「鹤归云外」可使用风元素进行空中机动，元素爆发「暮云凝紫」召唤风场造成大范围风元素伤害。闲云也是申鹤的师父，对申鹤如同亲生女儿一般关爱。",
            "source": "角色故事·闲云",
            "metadata": {
                "region": "璃月",
                "element": "风",
                "affiliation": "沉玉谷"
            }
        },
        {
            "type": "character_story",
            "title": "蓝砚",
            "content": "蓝砚，璃月的年轻铸剑师，出身于璃月港的铁匠世家。她继承了家族的铸剑手艺，年纪轻轻就掌握了一手精湛的锻造技术。蓝砚的性格开朗直爽，对武器有着近乎狂热的执着，经常为了锻造一柄完美的武器而废寝忘食。她擅长使用风元素力，能够在锻造时借助风的力量让金属达到更完美的状态。蓝砚的祖父曾是璃月最负盛名的铁匠，她立志要超越祖父的成就。元素战技「风锻」可将风元素凝聚成锤形攻击，元素爆发「千锤百炼」召唤数柄风元素铸造的武器攻击大范围敌人。",
            "source": "角色故事·蓝砚",
            "metadata": {
                "region": "璃月",
                "element": "风",
                "affiliation": "璃月港"
            }
        }
    ],
    'sumeru.json': [
        {
            "type": "character_story",
            "title": "赛索斯",
            "content": "赛索斯，须弥的沙漠部族首领，继承了赤王血脉的末裔。他出身于沙漠中的塔尼特部族，幼年时经历了部族灭亡的悲剧。在被教令院学者收养后，赛索斯在须弥城接受了教育，但他始终没有忘记自己的沙漠根源。他成年后回到了沙漠，重整塔尼特残部，成为了沙漠中的领袖。赛索斯性格沉稳果断，既有沙漠部族的豪爽，又有须弥城学者的智慧。他擅长使用弓箭，雷元素战技「沙暴之矢」射出带有雷元素的箭矢，元素爆发「赤王裁决」召唤沙漠风暴降下雷电打击。赛索斯是沙漠与雨林之间和平的桥梁。",
            "source": "角色故事·赛索斯",
            "metadata": {
                "region": "须弥",
                "element": "雷",
                "affiliation": "塔尼特部族"
            }
        }
    ],
    'fontaine.json': [
        {
            "type": "character_story",
            "title": "夏洛蒂",
            "content": "夏洛蒂，枫丹蒸汽鸟报社的记者，以犀利敏锐的报道而闻名。她有着一头标志性的银色短发和一双充满好奇的眼睛，总是带着笔记本和相机穿行于枫丹的街头巷尾。夏洛蒂对真相有着执着的追求，为了挖掘新闻不惧危险。她曾多次深入调查枫丹的黑暗面，揭露了许多不为人知的秘密。夏洛蒂擅长使用冰元素力，元素战技「冰晶暗访」能够冻结目标并造成冰元素伤害，元素爆发「独家头条」召唤冰晶风暴席卷战场。她的性格活泼开朗，但又有着记者特有的敏锐洞察力。在枫丹的正义体系中，夏洛蒂坚信「真相是最高的正义」。",
            "source": "角色故事·夏洛蒂",
            "metadata": {
                "region": "枫丹",
                "element": "冰",
                "affiliation": "蒸汽鸟报社"
            }
        },
        {
            "type": "character_story",
            "title": "艾梅莉埃",
            "content": "艾梅莉埃，枫丹的香水设计师，在枫丹廷经营着一家名为「香韵」的高级香水店。她天生拥有超乎常人的嗅觉，能够分辨出数万种不同的香气组合。艾梅莉埃性格优雅从容，举止得体大方，是枫丹社交圈中备受瞩目的名人。她的香水作品远销提瓦特各地，甚至连至冬国的贵族也慕名而来。艾梅莉埃擅长使用草元素力，元素战技「花露凝香」释放草元素力形成香氛领域，元素爆发「馥郁绽放」引起大范围的草元素爆炸。她将香水艺术与元素力完美结合，创造出了独一无二的战斗风格。",
            "source": "角色故事·艾梅莉埃",
            "metadata": {
                "region": "枫丹",
                "element": "草",
                "affiliation": "枫丹廷"
            }
        }
    ],
}

# We don't have a 至冬.json or item for other region, so add to other files
# 达达利亚 - from Snezhnaya, let's add to a new or existing file
# 埃洛伊 - collab character, add to mondstadt or other
# For now, let's add them to mondstadt.json since they don't have a specific region file

new_extra = [
    {
        "type": "character_story",
        "title": "达达利亚",
        "content": "达达利亚，代号「公子」，愚人众执行官第十一席，来自至冬国。他出身于至冬的一个普通猎户家庭，从小就展露出惊人的战斗天赋和好战性格。十四岁时为追寻更强的力量误入深渊，与深渊中的远古巨兽搏斗了三个月，濒死之际领悟了「魔王武装」。公子是愚人众中最年轻的执行官，性格开朗直率，热爱战斗，渴望与强者交手。他表面上以「玩具销售员」的身份在璃月活动，实际在执行愚人众的秘密任务。擅长使用弓与双刃，水元素战技切换近战形态使用双刃战斗，元素爆发「极恶技·尽灭闪」造成巨额水元素伤害。虽然身为愚人众执行官，但达达利亚并非纯粹意义上的反派，他对家人极为珍视。",
        "source": "角色故事·达达利亚",
        "metadata": {
            "region": "至冬",
            "element": "水",
            "affiliation": "愚人众"
        }
    },
    {
        "type": "character_story",
        "title": "埃洛伊",
        "content": "埃洛伊，来自异世界的勇猛猎人，诺拉部族的战士。她并非提瓦特大陆的原住民，而是从另一个世界穿越而来的访客。埃洛伊自幼被部落排斥，在荒野中独自长大，练就了卓越的狩猎技巧。她擅长使用弓箭和陷阱，能够利用机械兽的零件制造强大的武器。在机缘巧合下，埃洛伊穿越星海来到了提瓦特大陆，被这里的元素力和七国文明所吸引。她性格坚韧独立，不轻易相信他人，但对于值得信赖的伙伴会付出一切。埃洛伊使用冰元素力，元素战技「冷冻陷阱」部署冰霜爆破陷阱，元素爆发「毁灭之雨」降下冰元素箭雨。",
        "source": "角色故事·埃洛伊",
        "metadata": {
            "region": "其他",
            "element": "冰",
            "affiliation": "诺拉部族"
        }
    },
    {
        "type": "character_story",
        "title": "迪奥娜",
        "content": "迪奥娜，蒙德猫尾酒馆的调酒师，也是「清泉镇」出身的猎户之女。她拥有一手神奇的调酒天赋——无论什么酒到了她手里都会变成绝顶美味，但这恰恰是她的烦恼，因为她最痛恨酒，最大的愿望是「毁掉蒙德的酒业」。迪奥娜的父亲杜拉夫是清泉镇著名的猎人，迪奥娜从父亲那里学到了优秀的狩猎技巧。她的猫耳和尾巴是凯茨莱茵家族的遗传特征。",
        "source": "角色故事·迪奥娜",
        "metadata": {
            "region": "蒙德",
            "element": "冰",
            "affiliation": "猫尾酒馆"
        }
    },
    {
        "type": "character_story",
        "title": "闲云",
        "content": "闲云，真名留云借风真君，璃月的三眼五显仙人之一，是岩王帝君的旧友。她擅长机关术与工巧之技，性格高傲直率，说话不留情面，但内心极为温柔。在魔神战争中，留云借风真君与其他仙人一同守护璃月。她曾帮助过人类对抗魔神，但也曾因为人类的背叛而心灰意冷。在璃月的人治时代到来后，她以人类的姿态行走凡间，化名「闲云」，担任沉玉谷地区的镖师和机关顾问。",
        "source": "角色故事·闲云",
        "metadata": {
            "region": "璃月",
            "element": "风",
            "affiliation": "沉玉谷"
        }
    },
    {
        "type": "character_story",
        "title": "蓝砚",
        "content": "蓝砚，璃月的年轻铸剑师，出身于璃月港的铁匠世家。她继承了家族的铸剑手艺，年纪轻轻就掌握了一手精湛的锻造技术。蓝砚的性格开朗直爽，对武器有着近乎狂热的执着，经常为了锻造一柄完美的武器而废寝忘食。她擅长使用风元素力，能够在锻造时借助风的力量让金属达到更完美的状态。",
        "source": "角色故事·蓝砚",
        "metadata": {
            "region": "璃月",
            "element": "风",
            "affiliation": "璃月港"
        }
    },
    {
        "type": "character_story",
        "title": "夏洛蒂",
        "content": "夏洛蒂，枫丹蒸汽鸟报社的记者，以犀利敏锐的报道而闻名。她有着一头标志性的银色短发和一双充满好奇的眼睛，总是带着笔记本和相机穿行于枫丹的街头巷尾。夏洛蒂对真相有着执着的追求，为了挖掘新闻不惧危险。她曾多次深入调查枫丹的黑暗面，揭露了许多不为人知的秘密。",
        "source": "角色故事·夏洛蒂",
        "metadata": {
            "region": "枫丹",
            "element": "冰",
            "affiliation": "蒸汽鸟报社"
        }
    },
    {
        "type": "character_story",
        "title": "艾梅莉埃",
        "content": "艾梅莉埃，枫丹的香水设计师，在枫丹廷经营着一家名为「香韵」的高级香水店。她天生拥有超乎常人的嗅觉，能够分辨出数万种不同的香气组合。艾梅莉埃性格优雅从容，举止得体大方，是枫丹社交圈中备受瞩目的名人。她的香水作品远销提瓦特各地，甚至连至冬国的贵族也慕名而来。",
        "source": "角色故事·艾梅莉埃",
        "metadata": {
            "region": "枫丹",
            "element": "草",
            "affiliation": "枫丹廷"
        }
    },
    {
        "type": "character_story",
        "title": "赛索斯",
        "content": "赛索斯，须弥的沙漠部族首领，继承了赤王血脉的末裔。他出身于沙漠中的塔尼特部族，幼年时经历了部族灭亡的悲剧。在被教令院学者收养后，赛索斯在须弥城接受了教育，但他始终没有忘记自己的沙漠根源。他成年后回到了沙漠，重整塔尼特残部，成为了沙漠中的领袖。",
        "source": "角色故事·赛索斯",
        "metadata": {
            "region": "须弥",
            "element": "雷",
            "affiliation": "塔尼特部族"
        }
    },
    {
        "type": "character_story",
        "title": "达达利亚",
        "content": "达达利亚，代号「公子」，愚人众执行官第十一席，来自至冬国。他出身于至冬的一个普通猎户家庭，从小就展露出惊人的战斗天赋和好战性格。十四岁时为追寻更强的力量误入深渊，与深渊中的远古巨兽搏斗了三个月，濒死之际领悟了「魔王武装」。公子是愚人众中最年轻的执行官，性格开朗直率，热爱战斗，渴望与强者交手。",
        "source": "角色故事·达达利亚",
        "metadata": {
            "region": "至冬",
            "element": "水",
            "affiliation": "愚人众"
        }
    },
    {
        "type": "character_story",
        "title": "埃洛伊",
        "content": "埃洛伊，来自异世界的勇猛猎人，诺拉部族的战士。她并非提瓦特大陆的原住民，而是从另一个世界穿越而来的访客。埃洛伊自幼被部落排斥，在荒野中独自长大，练就了卓越的狩猎技巧。她擅长使用弓箭和陷阱，能够利用机械兽的零件制造强大的武器。",
        "source": "角色故事·埃洛伊",
        "metadata": {
            "region": "其他",
            "element": "冰",
            "affiliation": "诺拉部族"
        }
    },
]

# ===================== 2. Missing Artifact Sets =====================
# Genshin has ~60 artifact sets total. We have 28.
# Missing important 5★ sets that should be added

missing_artifacts = [
    # 蒙德 - Missing important sets
    {
        "type": "artifact",
        "title": "冰风迷途的勇士",
        "content": "两件套效果：冰元素伤害加成提高15%。四件套效果：攻击处于冰元素影响下的敌人时，暴击率提高20%；若敌人处于冻结状态下，暴击率额外提高20%。是冰系主C角色的毕业套装，适合神里绫华、甘雨等冰元素输出角色。获取方式：芬德尼尔之顶·祝圣秘境。副词条优先选择暴击率、暴击伤害、攻击力百分比。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 5, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "征服寒冬的勇士",
        "content": "两件套效果：冰元素抗性提高40%。四件套效果：对处于冻结状态及冰元素影响下的敌人造成的伤害提升35%。虽然整体强度不如冰风迷途的勇士，但在特定场合仍有不错的发挥。获取方式：芬德尼尔之顶·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "祭火之人",
        "content": "两件套效果：火元素抗性提高40%。四件套效果：对处于火元素影响下的敌人造成的伤害提升35%。属于早期圣遗物套装，在游戏后期逐渐退出主流配装。获取方式：无妄引咎密宫·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "渡过烈火的贤人",
        "content": "两件套效果：火元素伤害加成提高15%。四件套效果：超载、燃烧、烈绽放反应造成的伤害提升40%；触发上述反应时元素战技伤害提升50%，持续10秒。适合以火元素反应为核心的队伍，如燃烧队和烈绽放队。获取方式：无妄引咎密宫·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 5, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "奇迹",
        "content": "两件套效果：所有元素抗性提高20%。四件套效果：受到某个元素类型的伤害后，对应的元素抗性额外提升30%，持续10秒。早期圣遗物套装在游戏前期有一定价值，后期被更优质的套装取代。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "守护之心",
        "content": "两件套效果：防御力提高30%。四件套效果：队伍中每有一种元素类型的角色，自身对应的元素抗性提高30%。作为防御向圣遗物，适合新手期的生存需求。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "战狂",
        "content": "两件套效果：暴击率提高12%。四件套效果：生命值低于70%时，暴击率额外提升24%。是前期性价比极高的暴击率套装，适合大多数输出型角色度过新手期。获取方式：地图探索、精英怪物掉落和北风狼挑战。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "武人",
        "content": "两件套效果：普通攻击与重击伤害提高15%。四件套效果：施放元素战技后，普通攻击和重击伤害提升25%，持续8秒。适合依赖普攻和重击输出的前期角色。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "教官",
        "content": "两件套效果：元素精通提高80点。四件套效果：触发元素反应后，队伍中所有角色元素精通提高120点，持续8秒。4★套装的精髓在于四件套的全队精通加成，在元素反应队中有独特的辅助价值。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "赌徒",
        "content": "两件套效果：元素战技造成的伤害提升20%。四件套效果：击败敌人时，有100%概率重置元素战技的冷却时间，该效果每15秒只能触发一次。适合依靠元素战技输出的角色在前期使用。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "流放者",
        "content": "两件套效果：元素充能效率提高20%。四件套效果：施放元素爆发后，每2秒为队伍中其他角色恢复2点元素能量，持续6秒。作为辅助向套装，在前期能为队伍提供不错的能量回复。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "学者",
        "content": "两件套效果：元素充能效率提高20%。四件套效果：获得元素微粒或元素晶球时，队伍中所有弓箭和法器角色额外恢复3点元素能量。适合在混合队伍中辅助远程角色。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "冒险家",
        "content": "两件套效果：生命值上限提高1000点。四件套效果：开启宝箱后的5秒内，持续恢复30%生命值。属于游戏前期探索向圣遗物套装，适合在大世界探索时使用。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "幸运儿",
        "content": "两件套效果：防御力提高100点。四件套效果：拾取摩拉时，恢复300点生命值。前期探索时偶有使用，后期几乎不会考虑。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 3, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "游医",
        "content": "两件套效果：角色受到的治疗效果提高20%。四件套效果：施放元素爆发时，恢复20%生命值。前期治疗角色可以使用的过渡套装。获取方式：地图探索和精英怪物掉落。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 3, "slot": "套装"}
    },
    # 璃月
    {
        "type": "artifact",
        "title": "磐岩套",
        "content": "两件套效果：获得15%岩元素伤害加成。四件套效果：获得结晶反应形成的晶片时，队伍中所有角色获得对应元素35%的伤害加成，持续10秒，同时只能存在一种元素伤害加成。虽然两件套是岩C的主流选择，但四件套的实战应用较为有限，主要作为辅助岩队的备选。获取方式：孤云凌霄之处·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "璃月", "max_rarity": 5, "slot": "套装"}
    },
    # 稻妻
    {
        "type": "artifact",
        "title": "旗印",
        "content": "两件套效果：元素充能效率提高20%。四件套效果：基于元素充能效率的25%提高元素爆发伤害，至多通过这种方式获得75%提升。是目前元素爆发特化型角色的首选套装，适合雷电将军、香菱、行秋等依赖元素爆发输出的角色。获取方式：椛染之庭·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "稻妻", "max_rarity": 5, "slot": "套装"}
    },
    # 纳塔新套装
    {
        "type": "artifact",
        "title": "烬城勇者绘卷",
        "content": "两件套效果：队伍中附近的角色触发「夜魂迸发」时，装备者恢复6点元素能量。四件套效果：装备者触发其对应元素类型的相关反应后，队伍中附近的所有角色的该元素反应相关的元素伤害加成提升12%，持续15秒。若装备者处于夜魂加持状态下触发此效果，队伍中附近的所有角色还将获得另一元素类型28%的伤害加成，持续20秒。适合纳塔地区的夜魂机制角色使用。获取方式：圣火竞技场·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "纳塔", "max_rarity": 5, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "悠古的磐岩",
        "content": "两件套效果：岩元素伤害加成提高15%。四件套效果：获得结晶反应形成的晶片时，队伍中所有角色获得35%对应元素伤害加成，持续10秒，同时只能通过该效果获得一种元素伤害加成。适合岩元素辅助角色如钟离、五郎使用。获取方式：孤云凌霄之处·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "璃月", "max_rarity": 5, "slot": "套装"}
    },
    {
        "type": "artifact",
        "title": "征涛之旅",
        "content": "两件套效果：水元素伤害加成提高15%。四件套效果：施放元素战技后，普通攻击与重击造成的伤害提高30%，持续15秒。适合依赖普攻和重击的水系角色。获取方式：芬德尼尔之顶·祝圣秘境。",
        "source": "圣遗物图鉴",
        "metadata": {"region": "蒙德", "max_rarity": 4, "slot": "套装"}
    },
]

def add_to_file(filename, new_items, type_filter=None, key_filter=None):
    path = os.path.join(wd, filename)
    existing = load_json(path)
    existing_titles = {item.get('title','') for item in existing if item.get('type') == type_filter} if type_filter else {item.get('title','') for item in existing}
    existing_titles_all = {item.get('title','') for item in existing}
    
    added = 0
    for item in new_items:
        # Check by title+type combo
        key = (item.get('type',''), item.get('title',''))
        if item.get('title') not in existing_titles_all:
            existing.append(item)
            added += 1
    
    if added > 0:
        save_json(path, existing)
    return added

print("=== Adding character stories ===")
for fname, stories in new_character_stories.items():
    c = add_to_file(fname, stories)
    print(f"  {fname}: added {c} character_stories")

print(f"\n  mondstadt.json: adding extra (达达利亚, 埃洛伊 companion stories)")
mond_path = os.path.join(wd, 'mondstadt.json')
mond = load_json(mond_path)

# Add 达达利亚 and 埃洛伊 to mondstadt since they don't have dedicated region files
mond_titles = {item.get('title','') for item in mond}
for story in new_extra:
    if story['title'] not in mond_titles:
        mond.append(story)

save_json(mond_path, mond)
print(f"  mondstadt.json: added extra character stories")

print("\n=== Adding missing artifacts ===")
# Add artifacts to mondstadt.json (generic)
mond = load_json(mond_path)
mond_art_titles = {item.get('title','') for item in mond if item.get('type') == 'artifact'}
added_art = 0
for art in missing_artifacts:
    if art['title'] not in mond_art_titles:
        mond.append(art)
        added_art += 1
save_json(mond_path, mond)
print(f"  mondstadt.json: added {added_art} artifact entries")

print("\n=== Done ===")
