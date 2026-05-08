# 原神全量原文

> 从游戏客户端数据直接提取的原始文本，**非总结/浓缩内容**。
> 仅推送 GitHub，不参与前端构建。

## 数据

| 文件 | 内容 | 数量 |
|------|------|:----:|
| 全量Dialog原文.json | 全部游戏对话原文 | **42,568 条** |
| 角色台词统计.json | 各角色台词数 | 756 个说话人 |
| 主要角色台词.json | 派蒙/温迪/钟离等 9 名主要角色台词 | 7,701 句 |
| 全量材料描述.json | 游戏内所有材料描述 | 1,491 条 |
| 全量圣遗物文本.json | 圣遗物数据 | 3,003 件 |
| 全量武器文本.json | 武器数据 | 109 把 |
| 全量角色文本.json | 角色数据 | 68 名 |
| 全量技能文本.json | 技能天赋文本 | 294 个 |
| 角色好感故事.json | 角色故事原文 | 818 篇 |
| 角色语音.json | 语音文本 | 4,005 条 |
| 完整任务对话.json | 任务对话（Quest-Talk 链） | 23,317 句 |
| 主线世界任务对话.json | 主线+世界任务对话 | 10,764 句 |

**总计: 42,568 条对话, 90.4 万字**

## 架构隔离

```
knowledge_data/ → merge_all → kb_complete.json → import_data → Qdrant (后端搜索)
knowledge_data/ → prepare_encyclopedia.py → encyclopedia_data.json → public/index.html (前端)
raw/                                                                        → GitHub 仅用
```

`raw/` 从未被 `prepare_encyclopedia.py` 或任何前端构建脚本引用。
