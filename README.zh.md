# Causet 知识卡片学习系统

本项目是一个基于 **FastAPI** + **SQLite** + **Markdown** 的知识卡片学习系统原型，包含以下主要功能：

1. **用户系统**：注册 / 登录 / JWT 鉴权  
2. **知识卡片同步**：从 `cards/` 文件夹自动同步至数据库  
3. **推荐算法**：根据用户已关注主题及已学记录进行推荐  
4. **学习记录**：记录用户对卡片的学习并提供持续打卡功能  
5. **前端页面**：  
   - `login.html` / `register.html` / `homepage.html` / `preferences.html` 等原生 HTML + JS  
   - 提供注册登录、查看推荐、勾选关注主题等交互

---

## 目录结构

```bash
Causet/
├── main.py
├── requirements.txt
├── templates/
│   ├── login.html          # 登录页面
│   ├── register.html       # 注册页面
│   ├── homepage.html       # 首页 - 推荐列表
│   ├── preferences.html    # 用户关注主题页面
├── routes/
│   ├── auth.py             # 用户注册/登录路由
│   ├── cards.py            # 查询卡片路由（公开 or 需鉴权）
│   ├── recommend.py        # 推荐路由（需鉴权）
│   ├── learn.py            # 用户学习记录路由（需鉴权）
│   ├── preferences.py      # 用户关注主题路由（需鉴权）
├── database/
│   ├── __init__.py         # engine, SessionLocal, get_db()
│   ├── init_db.py          # 数据库初始化脚本
│   ├── models.py           # SQLAlchemy 模型定义（User、Card、UserCard）
├── utils/
│   ├── hash.py             # 密码哈希 & 验证
│   ├── jwt.py              # JWT 生成 & 解析
│   └── auth_utils.py       # 获取当前用户 / token 解析
├── watch_cards.py          # Watchdog 同步 Markdown -> 数据库
└── cards/
    ├── physic/
    │   └── 牛顿第二定律.md
    └── ai/
        └── Transformer.md
```

---

## 功能概述

1. **注册 / 登录**  
   - 用户名唯一，密码使用 bcrypt 加盐哈希  
   - 登录成功后返回 JWT token，用于后续接口鉴权  

2. **知识卡片**  
   - 存放于 `cards/` 文件夹中，按分类放入子目录（如 `physic/`, `ai/` 等）  
   - `watch_cards.py` 监听文件变动，自动将卡片信息（标题、分类、路径等）同步至 `cards` 表  

3. **推荐**  
   - 用户只会看到自己 **未学习** 且 **关注主题** 的卡片  
   - 依据 `order_in_category` 字段进行排序  
   - 前端首页 `/homepage.html` 通过请求 `/api/recommend` 获取推荐卡片  

4. **学习记录**  
   - `/api/learn` 接口可向 `user_cards` 表插入学习记录  
   - 同时更新 `users` 表中的学习数、连续学习天数等信息（可选）  

5. **主题关注**  
   - `/preferences.html` 页面列出数据库中所有分类（去重）  
   - 用户可勾选存储到 `users.followed_categories`（JSON 字段）  
   - 推荐接口只返回这些关注分类下的卡片  

---

## 环境 & 依赖

- Python 3.10+  
- FastAPI  
- uvicorn  
- SQLAlchemy  
- bcrypt  
- Jinja2  
- watchgod 或 watchdog (监听 Markdown 改动)
  
安装依赖（若使用 `requirements.txt`）：
```bash
pip install -r requirements.txt
```

---

## 快速开始

1. **克隆本项目**  
   ```bash
   git clone https://github.com/buezw/Causet.git
   cd Causet
   ```

2. **安装依赖**  
   ```bash
   pip install -r requirements.txt
   ```
   或者手动 `pip install fastapi uvicorn sqlalchemy bcrypt watchgod ...`

3. **初始化数据库**  
   ```bash
   python database/init_db.py
   ```
   > 如果已经有旧数据库，可以先 `rm knowledge.db` 再执行以上命令

4. **运行项目**  
   ```bash
   uvicorn main:app --reload
   ```
   > 默认监听 `http://127.0.0.1:8000`

5. **开启 Watchdog 同步（可选）**  
   打开一个新终端：  
   ```bash
   python watch_cards.py
   ```
   > 这样你在 `cards/` 下增删改 `.md` 文件会自动更新到数据库

6. **访问页面**  
   - [http://127.0.0.1:8000/register](http://127.0.0.1:8000/register)  注册  
   - [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)     登录  
   - [http://127.0.0.1:8000/preferences](http://127.0.0.1:8000/preferences)  勾选感兴趣的主题  
   - [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  主页 (可查看推荐卡片)

---

## 常用接口

1. **注册**: `POST /api/register`  
   请求体：
   ```json
   { "username": "alice", "password": "123456" }
   ```
   返回：
   ```json
   { "success": true, "message": "注册成功" }
   ```

2. **登录**: `POST /api/login`  
   请求体：
   ```json
   { "username": "alice", "password": "123456" }
   ```
   返回：
   ```json
   { "success": true, "token": "...", "message": "登录成功" }
   ```
   > 前端需保存 `token`，在后续请求加上 `Authorization: Bearer <token>`

3. **获取推荐**: `GET /api/recommend` (需要登录)  
   Headers:
   ```
   Authorization: Bearer <token>
   ```
   返回：
   ```json
   {
     "user_id": 1,
     "username": "alice",
     "learned_count": 5,     // (可选)
     "streak_days": 2,      // (可选)
     "cards": [
       {"id": 11, "title": "牛顿第二定律", "category": "physic"},
       ...
     ]
   }
   ```

4. **学习记录**: `POST /api/learn` (需要登录)  
   请求体：
   ```json
   { "card_id": 11 }
   ```
   返回：
   ```json
   { "success": true, "message": "学习记录已保存" }
   ```
   > 后端会在 `user_cards` 表写一条学习记录

5. **查询分类**: `GET /api/categories`  
   返回：
   ```json
   ["physic", "ai", "math", ...]
   ```

6. **获取/更新关注主题**  
   - `GET /api/preferences` (需要登录)  
     ```json
     { "preferences": ["physic", "ai"] }
     ```
   - `POST /api/preferences` (需要登录)  
     请求体：
     ```json
     ["physic", "ai"]
     ```
     返回：
     ```json
     { "success": true, "message": "关注主题已更新" }
     ```

---

## 数据库设计

- **users**  
  | 字段                   | 含义                |
  |------------------------|---------------------|
  | id (int)               | 主键               |
  | username (str)         | 唯一用户名         |
  | password_hash (str)    | bcrypt 加密密码    |
  | created_at (datetime)  | 注册时间           |
  | followed_categories (JSON) | 用户关注的主题 (如 ["physic","ai"]) |
  | learned_count (int)    | (可选) 已学卡片总数 |
  | streak_days (int)      | (可选) 连续学习天数 |

- **cards**  
  | 字段             | 含义                   |
  |------------------|------------------------|
  | id (int)         | 主键                  |
  | title (str)      | 卡片标题              |
  | category (str)   | 分类 (例如 physic)    |
  | path (str)       | 文件路径 (相对 `cards/`) |
  | is_active (bool) | 是否启用             |
  | last_modified (datetime)| 上次修改时间   |
  | order_in_category (int) | 分类内顺序      |

- **user_cards**  
  | 字段                | 含义             |
  |---------------------|------------------|
  | id (int)            | 主键            |
  | user_id (int)       | 外键 => users.id|
  | card_id (int)       | 外键 => cards.id|
  | category (str)      | 冗余存卡片分类   |
  | learned_at (datetime)| 学习时间       |

---

## Watchdog 同步逻辑

- `watch_cards.py` 使用 `watchgod` 或 `watchdog` 库监听 `cards/` 目录  
- 当检测到 `.md` 文件的增 / 改 / 删：  
  1. 解析出 `category`（通过上级文件夹名）  
  2. 若是新文件就插入 `cards` 表  
  3. 若是已有文件就更新 `last_modified`  
  4. 若删除就对 `cards` 表里对应记录做 `is_active = False` (或直接删表记录)  

---

## 常见问题

1. **`get_db` 未定义**  
   - 在 `database/__init__.py` 或 `init_db.py` 中定义 `get_db()` 函数  
   - 在需要的路由文件顶部用 `from database import get_db` (或 `from database.init_db import get_db`)  

2. **加了新字段后数据库不变**  
   - SQLite 无法自动增加字段，需要手动删库重建或使用 Alembic 做迁移  
   - 开发阶段常用 `rm knowledge.db` + `python database/init_db.py`  

3. **用户未选任何关注主题时没有卡片推荐**  
   - 逻辑是 `Card.category.in_(preferred_categories)`，如果 `preferred_categories` 为空，建议提示或改成全部分类  

4. **如何在前端显示 Markdown**  
   - 后端可提供 `/api/card/{id}/content` 返回 `.md` 文本  
   - 前端用 `marked.js` 或 `showdown.js` 渲染 Markdown  

5. **如何部署**  
   - 最简单：`uvicorn main:app --host 0.0.0.0 --port 8000`  
   - 更专业：使用 `gunicorn` + `uvicorn.workers.UvicornWorker`  
   - 静态文件可交给 Nginx 代理

---

## 后续可扩展

- **卡片详情页**：支持 Markdown 渲染  
- **数据可视化**：展示每日/每周学习数据  
- **难度标签 / 评分**：卡片难度、优先级  
- **移动端适配**：封装为移动 App  
- **多用户协作 / 社交功能**：共享卡片、讨论等

---

## 许可证

本项目使用 **Apache License 2.0 (AL2.0)** 授权。  
你可以自由地使用、复制、修改、合并、发布、分发本项目的源码，详情请见 [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) 文件内容。

```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION...
   (省略若干行，可将全部协议内容粘贴至 LICENSE 文件中)
```

> 如需了解完整条款，请参阅 [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

祝使用愉快！如果对本项目有任何问题或改进建议，欢迎在 Issues 区讨论。  
**Causet** —— 一站式知识卡片学习系统。