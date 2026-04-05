from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app import crud, schemas
from app.database import SessionLocal

router = APIRouter(prefix="/products", tags=["products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Product, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    existing_product = crud.get_product_by_name(db, product.name)
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    return crud.create_product(db, product)

@router.get("/", response_model=List[schemas.Product])
def get_products(
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price filter"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all products with optional filters"""
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price must be <= max_price")
    
    products = crud.get_products(
        db, skip=skip, limit=limit, 
        min_price=min_price, max_price=max_price, in_stock=in_stock
    )
    return products

@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """Full update of a product"""
    existing_product = crud.get_product(db, product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check name uniqueness
    name_exists = crud.get_product_by_name(db, product.name)
    if name_exists and name_exists.id != product_id:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    
    updated_product = crud.update_product(db, product_id, product)
    return updated_product

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return None