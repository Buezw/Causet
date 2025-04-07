from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Card
from pathlib import Path
from datetime import datetime

engine = create_engine("sqlite:///knowledge.db", echo=True)
Session = sessionmaker(bind=engine)

def init():
    Base.metadata.create_all(engine)
    print("✅ 数据表已创建")

    base_path = Path("cards")
    session = Session()

    # 每个分类单独编号
    category_order_map = {}

    for file in sorted(base_path.glob("*/*.md")):
        title = file.stem
        category = file.parent.name
        rel_path = str(file.as_posix())
        last_modified = datetime.fromtimestamp(file.stat().st_mtime)

        # 初始化计数器
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
            order_in_category=order  # ✅ 排序值
        )
        session.add(card)
        print(f"➕ 导入卡片：{title}（{category}，顺序：{order}）")

    session.commit()
    session.close()
    print("✅ 所有卡片已写入数据库")

if __name__ == "__main__":
    init()
