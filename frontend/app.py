import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Retail Dashboard", layout="wide")

API_URL ="https://retail-backend-j6hd.onrender.com"

# Helper Function
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        return response.json()
    except:
        return {"error": "Unable to fetch data"}

# Title
st.title("E-Commerce Retail Sales Dashboard")

# Sidebar Filter
st.sidebar.header("Filters")
countries = fetch_data("countries")

if isinstance(countries, list):
    selected_country = st.sidebar.selectbox("Select Country", ["All"] + countries)
else:
    selected_country = "All"
    st.sidebar.error("Failed to load countries")

# Summary
if selected_country == "All":
    summary = fetch_data("summary")
else:
    summary = fetch_data(f"filtered-sales?country={selected_country}")

st.subheader("Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Orders", summary.get("total_orders", 0))
col2.metric("Total Products", summary.get("total_products", 0))
col3.metric("Total Sales", round(summary.get("total_sales", 0), 2))

# Monthly Sales
import plotly.express as px

monthly_sales = fetch_data("monthly-sales")

monthly_df = None

if isinstance(monthly_sales, list) and len(monthly_sales) > 0:
    monthly_df = pd.DataFrame(monthly_sales)

    st.subheader("Monthly Sales Trend")

    fig = px.line(
        monthly_df,
        x="month",
        y="sales",
        markers=True, 
        title="Monthly Sales Trend"
    )

    # Hover
    fig.update_traces(
        hovertemplate="<b>Month:</b> %{x}<br><b>Sales:</b> %{y}"
    )
    st.plotly_chart(fig, width='stretch')
else:
    st.warning("Monthly data not available")

# Top Products
import plotly.express as px
st.subheader("Top Selling Products")
top_products = fetch_data("top-products")
if isinstance(top_products, list) and len(top_products) > 0:
    top_df = pd.DataFrame(top_products)
    fig = px.bar(
        top_df,
        x="sales",
        y="product",
        orientation='h',
        title="Top Selling Products"
    )
# Hover 
    fig.update_traces(
        hovertemplate="<b>Product:</b> %{y}<br><b>Sales:</b> %{x}"
    )
    st.plotly_chart(fig, width='stretch')
else:
    st.warning("Top products not available")


# Country Sales
country_sales = fetch_data("sales-by-country")

country_df = None

if isinstance(country_sales, list) and len(country_sales) > 0:
    country_df = pd.DataFrame(country_sales)

    fig, ax = plt.subplots()
    ax.barh(country_df["country"], country_df["sales"])

    st.pyplot(fig)
else:
    st.warning("Country data not available")

# Distribution
import plotly.express as px

if monthly_df is not None:
    st.subheader("Sales Distribution")
    fig = px.histogram(
        monthly_df,
        x="sales",
        nbins=10,
        title="Sales Distribution"
    )
# Hover
    fig.update_traces(
        hovertemplate="<b>Sales Range:</b> %{x}<br><b>Count:</b> %{y}"
    )
    st.plotly_chart(fig, width='stretch')

# Scatter
if monthly_df is not None and not monthly_df.empty:

    fig, ax = plt.subplots()
    ax.scatter(monthly_df.index, monthly_df["sales"])

    st.pyplot(fig)

# Pie Chart
import plotly.express as px

if country_df is not None and not country_df.empty:

    fig = px.pie(
        country_df,
        values="sales",
        names="country",
        title="Sales Share by Country"
    )

    st.plotly_chart(fig, width='stretch')

else:
    st.warning("No country data available for pie chart")
# Growth Chart
if monthly_df is not None and not monthly_df.empty:

    monthly_df["growth"] = monthly_df["sales"].pct_change()

    fig, ax = plt.subplots()
    ax.plot(monthly_df["month"], monthly_df["growth"])

    plt.xticks(rotation=45)

    st.pyplot(fig)

# Data Check
st.subheader("Data Quality Check")
if st.button("Check Errors"):
    errors = fetch_data("check-errors")
    st.write(errors)

# Hypothesis Testing
st.subheader("Hypothesis Testing")
hypo_result = fetch_data("hypothesis-test")
if "error" in hypo_result:
    st.error(hypo_result["error"])
else:
    p_value = hypo_result.get("p_value")
    result = hypo_result.get("result")
    st.write("P-Value:", p_value)
    st.write("Conclusion:", result)
    st.info("Hypothesis: High quantity orders generate higher sales compared to low quantity orders.")
    if p_value is not None:
        if p_value < 0.05:
            st.success("Significant difference found (Reject Null Hypothesis)")
        else:
            st.warning("No significant difference found")

# ML Prediction
st.subheader("Sales Prediction")
col1, col2 = st.columns(2)
q = col1.number_input("Quantity", 1, 100)
p = col2.number_input("Price", 0.1, 100.0)
if st.button("Predict"):
    res = fetch_data(f"predict-sales?quantity={q}&price={p}")
    if "error" in res:
        st.error(res["error"])
    else:
        st.success(f"Predicted Sales: {round(res['predicted_sales'], 2)}")