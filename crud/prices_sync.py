from sqlalchemy.orm import Session
from app.models.prices import Price


def create_price(db: Session, price: Price) -> Price:
    db.add(price)
    db.commit()
    db.refresh(price)
    return price
