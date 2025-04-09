> 📄 License: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## 📄 [中文说明请点击这里](README.zh.md)

# Causet - Knowledge Card Learning System

This project is a prototype of a knowledge card learning system based on **FastAPI** + **SQLite** + **Markdown**, featuring:

1. **User system**: registration, login, JWT authentication  
2. **Knowledge card synchronization**: automatically sync cards from the `cards/` folder into the database  
3. **Recommendation algorithm**: recommend cards based on user preferences and learning history  
4. **Learning record**: track user progress and continuous learning streak  
5. **Frontend pages**:  
   - Includes `login.html`, `register.html`, `homepage.html`, `preferences.html` written in HTML + JS  
   - Supports login, viewing recommendations, and selecting interest topics

---

## Project Structure

```bash
Causet/
├── main.py
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── homepage.html
│   └── preferences.html
├── routes/
│   ├── auth.py
│   ├── cards.py
│   ├── recommend.py
│   ├── learn.py
│   └── preferences.py
├── database/
│   ├── __init__.py
│   ├── init_db.py
│   └── models.py
├── utils/
│   ├── hash.py
│   ├── jwt.py
│   └── auth_utils.py
├── watch_cards.py
└── cards/
    ├── physic/
    │   └── Newton_Second_Law.md
    └── ai/
        └── Transformer.md
```

---

## Features

1. **Registration / Login**  
   - Unique username, password stored using bcrypt with salt  
   - Returns JWT token after successful login

2. **Knowledge Cards**  
   - Stored under `cards/` folder, grouped by topic like `physic/`, `ai/`  
   - `watch_cards.py` listens to file changes and syncs into the database

3. **Recommendation**  
   - Recommend cards that are not yet learned and match followed topics  
   - Ordered by `order_in_category`  
   - Frontend calls `/api/recommend` to fetch cards

4. **Learning Record**  
   - `/api/learn` logs a new record to `user_cards` table  
   - Optionally updates `users` table's learned count and streak days

5. **Topic Preferences**  
   - `/preferences.html` shows all distinct categories from DB  
   - User preferences are stored in `users.followed_categories`  
   - Recommendations filter by these topics

---

## Environment & Dependencies

- Python 3.10+  
- FastAPI  
- uvicorn  
- SQLAlchemy  
- bcrypt  
- Jinja2  
- watchgod or watchdog

Install:
```bash
pip install -r requirements.txt
```

---

## Quick Start

1. **Clone the project**
```bash
git clone https://github.com/buezw/Causet.git
cd Causet
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize the database**
```bash
python database/init_db.py
```

4. **Run the server**
```bash
uvicorn main:app --reload
```

5. **Start Watchdog (optional)**
```bash
python watch_cards.py
```

6. **Visit pages**
- `/register` - Register new user  
- `/login` - Login  
- `/preferences` - Select topics  
- `/` - Homepage (recommendations)

---

## API Overview

1. **Register**: `POST /api/register`
```json
{ "username": "alice", "password": "123456" }
```

2. **Login**: `POST /api/login`
```json
{ "username": "alice", "password": "123456" }
```

3. **Get Recommendations**: `GET /api/recommend`  
Header:
```
Authorization: Bearer <token>
```
Response:
```json
{
  "user_id": 1,
  "username": "alice",
  "learned_count": 5,
  "streak_days": 2,
  "cards": [
    { "id": 11, "title": "Newton's Second Law", "category": "physic" }
  ]
}
```

4. **Mark as Learned**: `POST /api/learn`
```json
{ "card_id": 11 }
```

5. **Get / Update Preferences**
- `GET /api/preferences`
```json
{ "preferences": ["physic", "ai"] }
```
- `POST /api/preferences`
```json
["physic", "ai"]
```

6. **Get All Categories**: `GET /api/categories`

---

## Database Models

- **users**
  | Field | Description |
  |-------|-------------|
  | id | Primary key |
  | username | Unique |
  | password_hash | Hashed password |
  | created_at | Timestamp |
  | followed_categories | JSON array |
  | learned_count | Total learned |
  | streak_days | Continuous days |

- **cards**
  | Field | Description |
  |-------|-------------|
  | id | Primary key |
  | title | Card title |
  | category | Category |
  | path | Relative path |
  | is_active | Boolean |
  | last_modified | Timestamp |
  | order_in_category | Sort order |

- **user_cards**
  | Field | Description |
  |-------|-------------|
  | id | Primary key |
  | user_id | Foreign key |
  | card_id | Foreign key |
  | category | Category |
  | learned_at | Timestamp |

---

## Watchdog Sync Logic

- Monitors the `cards/` directory using `watchgod` or `watchdog`  
- On file create/update/delete:
  1. Parse `category` from folder name  
  2. Insert new cards  
  3. Update timestamps  
  4. Mark deleted cards as inactive

---

## FAQ

1. **`get_db` not defined?**  
   Define it in `database/__init__.py` or import it properly in routes.

2. **New fields not showing up in DB?**  
   SQLite does not auto migrate. Delete and recreate DB or use Alembic.

3. **No cards recommended if no topics selected?**  
   This is expected; change logic to show all if `preferred_categories` is empty.

4. **Display Markdown on frontend?**  
   Add API to return `.md` content and render it with `marked.js` or `showdown.js`.

5. **Deployment?**  
   Use `uvicorn` or production combo like `gunicorn + uvicorn.workers`.

---

## Future Plans

- Markdown rendering for card details  
- Learning data visualization  
- Difficulty level tags  
- Mobile version  
- Social sharing & collaboration

---

## License

Licensed under the **Apache License 2.0 (AL2.0)**.  
You may freely use, modify, merge, publish, and distribute this project. See [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for full text.
