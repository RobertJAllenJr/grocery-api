from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .db import Base, engine, get_db
from .models import Item
from .auth import require_api_key

# Create database tables (runs on startup)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grocery List API")


# ----------------------------
# Pydantic Schemas (validation)
# ----------------------------
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=1, le=999)
    category: Optional[str] = Field(default=None, max_length=50)


class ItemUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=1, le=999)
    category: Optional[str] = Field(default=None, max_length=50)
    is_purchased: bool = False


class ItemOut(BaseModel):
    id: int
    name: str
    quantity: int
    category: Optional[str]
    is_purchased: bool

    class Config:
        from_attributes = True


# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def root():
    return {
        "message": "Grocery List API is running",
        "docs": "/redoc",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_api_key),
):
    item = Item(
        name=payload.name.strip(),
        quantity=payload.quantity,
        category=payload.category.strip() if payload.category else None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/items", response_model=list[ItemOut])
def list_items(
    purchased: Optional[bool] = None,
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    _auth=Depends(require_api_key),
):
    query = db.query(Item)

    if purchased is not None:
        query = query.filter(Item.is_purchased == purchased)

    if category:
        query = query.filter(Item.category == category.strip())

    if q:
        text = f"%{q.strip()}%"
        query = query.filter(or_(Item.name.like(text), Item.category.like(text)))

    return query.order_by(Item.id.desc()).all()


@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_api_key),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_api_key),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.name = payload.name.strip()
    item.quantity = payload.quantity
    item.category = payload.category.strip() if payload.category else None
    item.is_purchased = payload.is_purchased

    db.commit()
    db.refresh(item)
    return item


@app.patch("/items/{item_id}/purchase", response_model=ItemOut)
def toggle_purchase(
    item_id: int,
    purchased: bool,
    db: Session = Depends(get_db),
    _auth=Depends(require_api_key),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_purchased = purchased
    db.commit()
    db.refresh(item)
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_api_key),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return None