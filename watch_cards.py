import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# === 数据库设置 ===
Base = declarative_base()
engine = create_engine("sqlite:///knowledge.db", echo=False)
Session = sessionmaker(bind=engine)

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    path = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    last_modified = Column(DateTime, nullable=False)
    order_in_category = Column(Integer, nullable=True)  # ✅ 别忘了这个
  # 文件最后修改时间（mtime）

# 初始化数据库表
Base.metadata.create_all(engine)

# === 同步函数：更新或创建卡片记录 ===
def sync_single_card(file_path: str):
    path_obj = Path(file_path)
    if not path_obj.suffix == ".md":
        return

    category = path_obj.parent.name
    title = path_obj.stem
    rel_path = str(path_obj.as_posix())
    last_modified = datetime.fromtimestamp(path_obj.stat().st_mtime)

    session = Session()
    existing = session.query(Card).filter_by(path=rel_path).first()

    if existing:
        existing.title = title
        existing.category = category
        existing.last_modified = last_modified
        existing.is_active = True
        print(f"📝 更新卡片：{title}")
    else:
        # ✅ 只有在新增卡片时才需要分配顺序编号
        existing_cards = session.query(Card).filter_by(category=category).all()
        order = len(existing_cards) + 1

        new_card = Card(
            title=title,
            category=category,
            path=rel_path,
            last_modified=last_modified,
            is_active=True,
            order_in_category=order  # ✅ 加上顺序
        )
        session.add(new_card)
        print(f"➕ 新增卡片：{title}（顺序：{order}）")

    session.commit()
    session.close()


# === 删除函数 ===
def remove_card_by_path(file_path: str):
    """
    从数据库中移除指定路径的卡片记录（对应 Markdown 文件删除事件）
    """
    session = Session()
    rel_path = str(Path(file_path).as_posix())
    card = session.query(Card).filter_by(path=rel_path).first()
    if card:
        session.delete(card)
        session.commit()
        print(f"🗑️ 删除卡片记录：{card.title}")
    session.close()

# === 文件系统监听器 ===
class CardEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            sync_single_card(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            sync_single_card(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            remove_card_by_path(event.src_path)

# === 启动监听器 ===
def start_watch_cards():
    path_to_watch = "cards"
    print(f"📂 正在监听目录变化：{path_to_watch}/ ...")
    event_handler = CardEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("👋 停止监听")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watch_cards()
