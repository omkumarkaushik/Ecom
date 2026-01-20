import streamlit as st
import requests
import json
import os
from typing import Dict, Any

# Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="E-Commerce API", layout="wide")

# Header
st.title("🛍️ FastAPI E-Commerce Frontend")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a feature:",
    [
        "🏠 Home",
        "📋 View All Products",
        "🔍 Search by Brand",
        "➕ Create Product",
        "✏️ Update Product",
        "🗑️ Delete Product",
    ]
)

# Helper function to make API calls
def api_call(method: str, endpoint: str, data: Dict[Any, Any] = None, params: Dict = None):
    try:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        return response.status_code, response.json()
    except Exception as e:
        return None, str(e)

# Home Page
if page == "🏠 Home":
    st.header("Welcome to E-Commerce API")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Endpoint", "http://127.0.0.1:8000")
    
    with col2:
        st.info("✅ API is running" if requests.get(f"{API_URL}/").status_code == 200 else "❌ API is offline")
    
    with col3:
        st.success("Streamlit Frontend Ready")
    
    st.markdown("---")
    
    st.subheader("📚 Available Features:")
    features = {
        "View All Products": "Browse all products with filtering, sorting, and pagination",
        "Search by Brand": "Find products by their brand name",
        "Create Product": "Add new products to the database",
        "Update Product": "Modify existing product information",
        "Delete Product": "Remove products from the database",
    }
    
    for feature, description in features.items():
        st.write(f"✨ **{feature}**: {description}")

# View All Products
elif page == "📋 View All Products":
    st.header("View All Products")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category = st.text_input("Filter by category (optional):", placeholder="e.g., smartphones")
    
    with col2:
        sort_option = st.selectbox("Sort by price:", ["off", "asc", "desc"])
    
    with col3:
        limit = st.number_input("Items per page:", min_value=1, max_value=100, value=10)
    
    offset = st.number_input("Skip items (offset):", min_value=0, value=0)
    
    if st.button("🔄 Fetch Products"):
        params = {
            "sort": sort_option,
            "limit": limit,
            "offset": offset,
        }
        if category:
            params["category"] = category
        
        status, response = api_call("GET", "/products", params=params)
        
        if status == 200:
            st.success(f"Found {response['length']} products")
            
            if response['products']:
                for product in response['products']:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{product.get('title', 'N/A')}** (ID: {product.get('id')})")
                            st.write(f"Brand: {product.get('brand', 'N/A')}")
                        with col2:
                            st.write(f"💰 ${product.get('price', 'N/A')}")
                        with col3:
                            st.write(f"⭐ {product.get('rating', 'N/A')}")
                    st.divider()
            else:
                st.info("No products found")
        else:
            st.error(f"Error: {response}")

# Search by Brand
elif page == "🔍 Search by Brand":
    st.header("Search Products by Brand")
    
    brand = st.text_input("Enter brand name:", placeholder="e.g., Apple, Samsung")
    
    if st.button("🔎 Search"):
        if brand:
            status, response = api_call("GET", f"/products/{brand}")
            
            if status == 200:
                st.success(f"Found {response['length']} products")
                
                if response['products']:
                    for product in response['products']:
                        with st.container():
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**{product.get('title', 'N/A')}**")
                                st.write(f"Description: {product.get('description', 'N/A')}")
                                st.write(f"Category: {product.get('category', 'N/A')}")
                            with col2:
                                st.write(f"💰 ${product.get('price', 'N/A')}")
                                st.write(f"Stock: {product.get('stock', 'N/A')}")
                        st.divider()
                else:
                    st.info("No products found for this brand")
            else:
                st.error(f"Error: {response}")
        else:
            st.warning("Please enter a brand name")

# Create Product
elif page == "➕ Create Product":
    st.header("Create New Product")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Product Title:", placeholder="iPhone 15")
        price = st.number_input("Price (USD):", min_value=0.0, step=0.01)
        brand = st.text_input("Brand:", placeholder="Apple")
        stock = st.number_input("Stock Quantity:", min_value=0, step=1)
    
    with col2:
        description = st.text_area("Description:", placeholder="Enter product description")
        discount = st.number_input("Discount (%):", min_value=0.0, max_value=100.0, step=0.1)
        category = st.text_input("Category:", placeholder="smartphones")
        rating = st.number_input("Rating:", min_value=0.0, max_value=5.0, step=0.1)
    
    thumbnail = st.text_input("Thumbnail URL:", placeholder="https://example.com/image.jpg")
    images_input = st.text_area("Image URLs (one per line):", placeholder="https://example.com/img1.jpg\nhttps://example.com/img2.jpg")
    
    if st.button("➕ Add Product"):
        images = [img.strip() for img in images_input.split("\n") if img.strip()]
        
        product_data = {
            "title": title,
            "description": description,
            "price": price,
            "discountPercentage": discount,
            "rating": rating,
            "stock": stock,
            "brand": brand,
            "category": category,
            "thumbnail": thumbnail,
            "images": images,
        }
        
        status, response = api_call("POST", "/products", data=product_data)
        
        if status == 200:
            st.success("✅ Product created successfully!")
            st.json(response)
        else:
            st.error(f"Error: {response}")

# Update Product
elif page == "✏️ Update Product":
    st.header("Update Product")
    
    product_id = st.number_input("Product ID:", min_value=1, step=1)
    
    if product_id:
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Product Title:")
            price = st.number_input("Price (USD):", min_value=0.0, step=0.01)
            brand = st.text_input("Brand:")
            stock = st.number_input("Stock Quantity:", min_value=0, step=1)
        
        with col2:
            description = st.text_area("Description:")
            discount = st.number_input("Discount (%):", min_value=0.0, max_value=100.0, step=0.1)
            category = st.text_input("Category:")
            rating = st.number_input("Rating:", min_value=0.0, max_value=5.0, step=0.1)
        
        thumbnail = st.text_input("Thumbnail URL:")
        images_input = st.text_area("Image URLs (one per line):")
        
        if st.button("✏️ Update Product"):
            images = [img.strip() for img in images_input.split("\n") if img.strip()]
            
            product_data = {
                "title": title,
                "description": description,
                "price": price,
                "discountPercentage": discount,
                "rating": rating,
                "stock": stock,
                "brand": brand,
                "category": category,
                "thumbnail": thumbnail,
                "images": images,
            }
            
            status, response = api_call("PUT", f"/products/{product_id}", data=product_data)
            
            if status == 200:
                st.success("✅ Product updated successfully!")
                st.json(response)
            else:
                st.error(f"Error: {response}")

# Delete Product
elif page == "🗑️ Delete Product":
    st.header("Delete Product")
    
    product_id = st.number_input("Enter Product ID to delete:", min_value=1, step=1)
    
    if product_id:
        st.warning(f"⚠️ You are about to delete product ID: {product_id}")
        
        if st.button("🗑️ Delete Product", type="secondary"):
            status, response = api_call("DELETE", f"/items/{product_id}")
            
            if status == 200:
                st.success("✅ Product deleted successfully!")
                st.json(response)
            else:
                st.error(f"Error: {response}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p style="color: gray;">FastAPI E-Commerce Frontend | Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)
