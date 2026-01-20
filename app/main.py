from fastapi import FastAPI, Path, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from app import products
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import List,Annotated

app = FastAPI()

class Product(BaseModel):
    title: Annotated[str, 
    Field(
    title="Product title"
    , min_length=1, max_length=100, description="The title of the product", example="iPhone 13")]
    
    
    description:Annotated[str, Field(
    title="Product description",
    min_length=1,
    max_length=500,
    description="A brief description of the product",
    example="The latest iPhone model with advanced features."
    )]

    price:Annotated[float, Field(
    title="Product price",
    gt=0,
    description="The price of the product in USD",
    example=999.99
    )] 

    discountPercentage: Annotated[float, Field(
    title="Discount Percentage",
    ge=0,
    le=100,
    description="The discount percentage for the product",
    example=10.5
    )]
     
    rating:Annotated[float, Field(
    title="Product rating",
    ge=0,
    le=5,
    description="The average rating of the product",
    example=4.5
    )]

    stock:Annotated[int, Field(
    title="Stock quantity",
    ge=0,
    description="The number of items available in stock",
    example=50
    )]

    brand: Annotated[str, Field(
    title="Product brand",
    min_length=1,
    max_length=50,
    description="The brand of the product",
    example="Apple"
    )]

    category:Annotated[str, Field(
    title="Product category",
    min_length=1,
    max_length=50,
    description="The category of the product",
    example="smartphones"
    )]

    thumbnail: str
    images: List[str] = []

    @field_validator("rating", mode="after")
    @classmethod
    def validate_rating(cls, value):
        if not (0 <= value <= 5):
            raise ValueError("Rating must be between 0 and 5")
        return value
    

    @model_validator(mode="after")
    @classmethod
    def check_price_discount(cls, model: "Product"):
        if model.discountPercentage > 0 and model.rating == 0:
            raise ValueError("Discounted products must have a rating")
        return model
    
    @computed_field
    @property
    def discounted_price(self) -> float:
        return round(self.price * (1 - self.discountPercentage / 100),2)

def get_api_info():
    """Dependency that returns API info"""
    return {
        "api_name": "FastAPI E-Commerce",
        "version": "1.0.0",
        "status": "running"
    }

def get_all_products():
    """Dependency that fetches all products from database"""
    return products.get_all_items()

@app.get("/")
def root(api_info: dict = Depends(get_api_info)):
    return {
        "message": "Hello, World!",
        "api_details": api_info
    }


@app.get("/items")
def read_item(all_products: list = Depends(get_all_products)):
    # all_products = products.get_all_items()
    return all_products

@app.get("/products")
def list_products(
    all_products: list = Depends(get_all_products),
    category: str = Query(
        default=None,
        min_length=3,
        max_length=50,
        description="Filter products by category",
    ),
    sort: str = Query(
        default="off",
        pattern="^(off|asc|desc)$",
        description="Sort by price: off (default), asc (ascending), desc (descending)",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Limit the number of products returned",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of products to skip",
    ),
):
    # all_products = products.get_all_items()
    if category:
        needle = category.strip().lower()
        filtered_products = [
            p for p in all_products
            if needle in (
                p.get("category", "").lower() if isinstance(p, dict) else str(p).lower()
            )
        ]        
        if not filtered_products:
            raise HTTPException(status_code=404, detail="No products found with the given category.")
    else:
        filtered_products = all_products
    
    # Sort by price if requested
    if sort == "asc":
        filtered_products = sorted(filtered_products, key=lambda p: p.get("price", 0))
    elif sort == "desc":
        filtered_products = sorted(filtered_products, key=lambda p: p.get("price", 0), reverse=True)
    
    total = len(filtered_products)

    filtered_products = filtered_products[offset : offset + limit]
    
    return {"length": total, "products": filtered_products}


@app.get("/products/{product_brand}")
def get_product_by_brand(
    product_brand: str = Path(
        ...,
        min_length=1,
        max_length=50,
        description="The brand of the product to retrieve",
        example="Apple",
    ),
    all_products: list = Depends(get_all_products),
):
    # all_products = products.get_all_items()
    matches = []
    for product in all_products:
        if isinstance(product, dict):
            brand = product.get("brand")
            if brand and brand.strip().lower() == product_brand.strip().lower():
                matches.append(product)
    if matches:
        return {"length": len(matches), "products": matches}
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products")
def create_product(product: Product):
    # all_products = products.get_all_items()
    
    # Generate new ID
    new_id = max([p.get("id", 0) for p in products.get_all_items() if isinstance(p, dict)], default=0) + 1
    
    # Create new product dict
    new_product = {
        "id": new_id,
        **product.dict()
    }
    
    # all_products.append(new_product)
    products.add_item(new_product)
    return {"message": "Product created successfully", "product": new_product}

@app.post("/items")
def create_item(item: Product):
    new_item = products.add_item(item.dict())
    return {"message": "Item added successfully", "item": new_item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int = Path(    
    ...,
    ge=1,
    description="The ID of the item to delete",
)):
    success = products.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    # return {"message": "Item deleted successfully"}
    return JSONResponse(
        status_code=200,
        content={"message": "Item deleted successfully", "item_id": item_id}
    )

@app.put("/products/{product_id}")
def update_product(
    product_id: int = Path(..., ge=1, description="The ID of the product to update"),
    product: Product = None
):
    if not product:
        raise HTTPException(status_code=400, detail="Product data is required")
    
    updated = products.update_item(product_id, product.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully", "product": updated}