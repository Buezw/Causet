# database/init_db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
from hashlib import sha256  # 开发用的简易密码加密

from models import Base, Card, User  # ✅ 新增 User 引入

# 创建 SQLite 引擎
engine = create_engine("sqlite:///knowledge.db", echo=True)
Session = sessionmaker(bind=engine)

def init():
    # ✅ 创建所有数据表（包括 cards / users / user_cards）
    Base.metadata.create_all(engine)
    print("✅ 数据表已创建")

    session = Session()

    # ✅ 1. 导入卡片内容
    base_path = Path("cards")
    category_order_map = {}

    for file in sorted(base_path.glob("*/*.md")):
        title = file.stem
        category = file.parent.name
        rel_path = str(file.as_posix())
        last_modified = datetime.fromtimestamp(file.stat().st_mtime)

        # 顺序计数器（按分类）
        if category not in category_order_map:
            category_order_map[category] = 1
        else:
            category_order_map[category] += 1

        order = category_order_map[category]

        card = Card(
            title=title,
            category=category,
            path=rel_path,
            is_active=True,
            last_modified=last_modified,
            order_in_category=order
        )
        session.add(card)
        print(f"➕ 导入卡片：{title}（{category}，顺序：{order}）")

    # ✅ 2. 添加初始用户（如不存在）
    users_to_add = [
        ("小李", "password1"),
        ("小王", "password2")
    ]

    for username, raw_password in users_to_add:
        if not session.query(User).filter_by(username=username).first():
            password_hash = sha256(raw_password.encode()).hexdigest()
            session.add(User(username=username, password_hash=password_hash))
            print(f"👤 添加用户：{username}")

    # ✅ 提交所有更改
    session.commit()
    session.close()
    print("✅ 所有数据已写入数据库")

if __name__ == "__main__":
    init()
