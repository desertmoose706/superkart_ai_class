import os
import streamlit as st
import requests

# API key for the backend, supplied through the environment
API_KEY = os.environ.get("API_KEY", "")

st.set_page_config(page_title="SuperKart Sales Predictor", layout="wide")

st.title("🛒 SuperKart Sales Predictor")
st.markdown("Adjust the product and store options below to predict the total sales.")

# Product types the model was trained on
PRODUCT_TYPES = [
    "Baking Goods", "Breads", "Breakfast", "Canned", "Dairy", "Frozen Foods",
    "Fruits and Vegetables", "Hard Drinks", "Health and Hygiene", "Household",
    "Meat", "Others", "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods",
]

# Input fields for prediction
col1, col2 = st.columns(2)

with col1:
    st.header("Product Details")
    product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
    product_sugar_content = st.selectbox("Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    product_allocated_area = st.number_input("Allocated Area Ratio", min_value=0.0, max_value=1.0, value=0.027)
    product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08)
    product_type = st.selectbox("Product Type", PRODUCT_TYPES, index=PRODUCT_TYPES.index("Dairy"))

with col2:
    st.header("Store Details")
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    store_location_city_type = st.selectbox("City Tier", ["Tier 1", "Tier 2", "Tier 3"])
    store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Food Mart", "Departmental Store"])
    store_establishment_year = st.number_input("Store Establishment Year", min_value=1900, max_value=2100, value=2009, step=1)

# Backend URL configuration (useful for Docker networking)
backend_url = st.text_input("Backend API Endpoint", "http://backend:7860/v1/predict", help="Use 'http://backend:7860/v1/predict' if running via Docker Compose")

if not API_KEY:
    st.warning("API_KEY is not set for this container; the backend will reject requests.")

if st.button("Predict Sales", type="primary"):
    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar_content,
        "Product_Allocated_Area": product_allocated_area,
        "Product_Type": product_type,
        "Product_MRP": product_mrp,
        "Store_Establishment_Year": int(store_establishment_year),
        "Store_Size": store_size,
        "Store_Location_City_Type": store_location_city_type,
        "Store_Type": store_type
    }
    
    with st.spinner("Predicting..."):
        try:
            response = requests.post(backend_url, json=payload, headers={"X-API-Key": API_KEY})
            if response.status_code == 200:
                prediction = response.json().get('predicted_sales', 0)
                st.success(f"### Predicted Store Sales: ${prediction:.2f}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
