from fastapi import FastAPI
from app.database import engine, Base
from app.routers import products

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Products Catalog API",
    description="API for managing product catalog",
    version="1.0.0"
)

app.include_router(products.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Products Catalog API",
        "docs": "/docs",
        "endpoints": [
            "POST /products",
            "GET /products",
            "GET /products/{id}",
            "PUT /products/{id}",
            "DELETE /products/{id}"
        ]
    }