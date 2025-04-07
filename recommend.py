from sqlalchemy.orm import Session
from database.models import Card

def get_today_cards(db: Session, learned_titles: set, max_cards=3):
    """
    遍历所有分类，从每类中按顺序选一张未学卡片
    """
    cards = db.query(Card).filter(Card.is_active == True).all()

    # 分类 -> [卡片列表]
    category_map = {}
    for card in cards:
        category_map.setdefault(card.category, []).append(card)

    # 每类排序
    for card_list in category_map.values():
        card_list.sort(key=lambda c: c.order_in_category or 0)

    result = []
    for cat, card_list in category_map.items():
        for card in card_list:
            if card.title not in learned_titles:
                result.append(card)
                break
        if len(result) >= max_cards:
            break

    return result
