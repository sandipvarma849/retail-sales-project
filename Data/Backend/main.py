from fastapi import FastAPI, Query
import pandas as pd
from scipy.stats import ttest_ind
from sklearn.linear_model import LinearRegression
import numpy as np

# Initialize FastAPI
app = FastAPI(title="Retail Sales Data Analytics API")

# Load Dataset
try:
    df = pd.read_excel("E-Commerce Retail Sales Dataset.xlsx")
except Exception as e:
    df = pd.DataFrame()
    print("Error loading dataset:", e)

# Data Preprocessing
if not df.empty:
    if "InvoiceDate" in df.columns:df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

# Creating sales
    if "Quantity" in df.columns and "UnitPrice" in df.columns:
        df["sales"] = df["Quantity"] * df["UnitPrice"]
    else:
        df["sales"] = 0

# Train ML Model
model = None
if not df.empty and "sales" in df.columns:
    try:
        X = df[["Quantity", "UnitPrice"]]
        y = df["sales"]
        model = LinearRegression()
        model.fit(X, y)
    except Exception as e:
        print("Model training error:", e)

# Root API
@app.get("/")
def home():
    return {"message": "Backend is running successfully"}

# Prediction API
@app.get("/predict-sales")
def predict_sales(quantity: int, price: float):
    if model is None:
        return {"error": "Model not trained"}
    try:
        input_data = np.array([[quantity, price]])
        prediction = model.predict(input_data)[0]
        return {"predicted_sales": float(prediction)}
    except Exception as e:
        return {"error": str(e)}

# Dataset Info
@app.get("/dataset-info")
def dataset_info():
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns)
    }

# Summary
@app.get("/summary")
def summary():
    return {
        "total_orders": int(df["InvoiceNo"].nunique()) if "InvoiceNo" in df.columns else 0,
        "total_products": int(df["StockCode"].nunique()) if "StockCode" in df.columns else 0,
        "total_sales": float(df["sales"].sum()) if "sales" in df.columns else 0
    }

# Monthly Sales
@app.get("/monthly-sales")
def monthly_sales():
    if "InvoiceDate" not in df.columns:
        return []
    temp_df = df.dropna(subset=["InvoiceDate"]).copy()
    temp_df["month"] = temp_df["InvoiceDate"].dt.to_period("M").astype(str)
    result = (
        temp_df.groupby("month")["sales"]
        .sum()
        .reset_index()
        .sort_values("month")
    )
    return result.to_dict(orient="records")

# Top Products
@app.get("/top-products")
def top_products():
    if "Description" not in df.columns:
        return []
    result = (
        df.groupby("Description")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    result.columns = ["product", "sales"]
    return result.to_dict(orient="records")

# Country Sales
@app.get("/sales-by-country")
def sales_by_country():
    if "Country" not in df.columns:
        return []
    result = (
        df.groupby("Country")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    result.columns = ["country", "sales"]
    return result.to_dict(orient="records")

# Countries List
@app.get("/countries")
def get_countries():
    if "Country" not in df.columns:
        return []
    return sorted(df["Country"].dropna().unique().tolist())

# Filtered Sales
@app.get("/filtered-sales")
def filtered_sales(country: str = Query(None)):
    filtered_df = df.copy()
    if country and country != "All" and "Country" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Country"] == country]
    return {
        "total_orders": int(filtered_df["InvoiceNo"].nunique()) if "InvoiceNo" in filtered_df.columns else 0,
        "total_products": int(filtered_df["StockCode"].nunique()) if "StockCode" in filtered_df.columns else 0,
        "total_sales": float(filtered_df["sales"].sum())
    }

# Hypothesis Testing
@app.get("/hypothesis-test")
def hypothesis_test():
    if "Quantity" not in df.columns or "sales" not in df.columns:
        return {"error": "Required columns not found"}
    temp_df = df.copy()
    high_qty = temp_df[temp_df["Quantity"] > 10]["sales"]
    low_qty = temp_df[temp_df["Quantity"] <= 10]["sales"]
    if len(high_qty) == 0 or len(low_qty) == 0:
        return {"error": "Not enough data for hypothesis testing"}
    stat, p_value = ttest_ind(high_qty, low_qty, equal_var=False)
    result = ("Significant difference found (Reject Null Hypothesis)"
        if p_value < 0.05
        else "No significant difference found"
    )
    return {
        "p_value": float(p_value),
        "result": result
    }
