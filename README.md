# 原神知识百科

> Genshin Impact Knowledge Encyclopedia — 知识库 + 语义搜索 + 知识图谱

## 项目结构

```
genshin-knowledge/
├── full/                              # 全量原始文本
│   ├── 角色好感故事.json              # 角色好感原文（818条）
│   ├── 武器.json                      # 武器故事原文（221条）
│   ├── 材料.json                      # 材料描述原文（741条）
│   ├── 敌人.json                      # 敌人图鉴原文（308条）
│   ├── 书籍.json                      # 书籍全文（61条）
│   ├── 角色档案.json                  # 角色档案/地区故事（304条）
│   └── README.md                      # 全量数据说明
├── knowledge_data/                    # 知识源数据（JSON）
│   ├── character_friendship_*.json    # 角色好感文本
│   ├── weapons_*.json                 # 武器数据
│   ├── materials.json                 # 材料数据
│   ├── enemies.json                   # 敌人数据
│   ├── books.json                     # 书籍全文
│   ├── fontaine.json / liyue.json / … # 角色故事（按地区）
│   ├── graph_data.json                # 关系图谱数据
│   └── kb_complete.json               # 合并后的全量知识库（gitignored）
├── public/                            # 前端页面
│   ├── index.html                     # 百科搜索页（单页应用）
│   ├── knowledge-graph.html           # 知识图谱可视化
│   ├── graph_data.json                # 图谱数据（gitignored，由 build 生成）
│   ├── encyclopedia_data.json         # 百科数据（gitignored，由构建生成）
│   └── prepare_encyclopedia.py        # 百科数据构建脚本
├── genshin_search_service.py          # LLM + 语义搜索服务（Flask）
├── embed_server.js / .mjs            # 向量嵌入服务（Node.js）
├── import_data.py                     # 数据导入 Qdrant
├── merge_all.py                       # 合并知识源 → kb_complete.json
├── build_encyclopedia.py              # 构建前端百科数据
├── build_graph_data.py                # 构建关系图谱
├── build_metadata.py                  # 构建元数据索引
├── fetch_stories.py                   # 抓取角色故事
├── fetch_missing_characters.py        # 补抓缺失角色
├── update_missing_data.py             # 更新缺失数据
├── stats_text.py                      # 文本量统计
└── start.sh / keep_alive.sh          # 服务管理脚本
```

## 数据概览

| 类别 | 条目数 | 说明 |
|------|-------|------|
| 角色好感文本 | 811 | 8 地区分文件，含角色故事 1-5、角色详细、神之眼 |
| 武器 | 219 | 按地区分文件，含星级、类型 |
| 材料 | 741 | 含材料类型、来源 |
| 角色故事 | 118 | 按地区，含元素、地区归属 |
| 支线任务 | 93 | 传说任务 + 世界任务 |
| 书籍 | 61 | 游戏内书籍全文 |
| 圣遗物 | 60 | 含套装信息 |
| 主线任务 | 26 | 魔神任务全章节 |
| 敌人 | 308 | 含 Boss、精英、普通敌人 |
| **合计** | **2437** | **~70.5 万字** |

> 数据说明：角色好感、武器、材料、敌人、书籍为**游戏原文**；主线/支线任务为**剧情概要**（非完整对话）。全量原文汇集于 `full/` 目录。

## 技术栈

- **语义搜索**: Qdrant (向量数据库) + gemma-embedding-300m (嵌入模型)
- **搜索服务**: Python Flask (`genshin_search_service.py`)
- **嵌入服务**: Node.js `embed_server.js` → llama-server
- **前端**: 纯 HTML/CSS/JS 单页应用，无框架依赖
- **图谱**: D3.js 力导向图

## 启动

```bash
# 1. 安装依赖
npm install
pip install -r requirements.txt  # Flask, qdrant-client, requests

# 2. 启动服务
./start.sh

# 3. 前端访问
# 打开 public/index.html 或部署到静态服务器
```

## 数据导入

```bash
# 合并知识源
python3 merge_all.py

# 全量导入 Qdrant（需先启动 llama-server :8080）
python3 import_data.py knowledge_data/kb_complete.json
```

## 前端构建

```bash
cd public
python3 prepare_encyclopedia.py   # 从 graph_data.json 生成展示数据
```

## 许可证

MIT
