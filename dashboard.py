import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Food Delivery Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced metric cards
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #ff4b4b;
    }
    .stMetric label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load dataset with caching


@st.cache_data
def load_data():
    df = pd.read_csv("ONINE_FOOD_DELIVERY_ANALYSIS.csv")
    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset `ONINE_FOOD_DELIVERY_ANALYSIS.csv`: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Dashboard")

# Date Filter
if "Order_Date" in df.columns and df["Order_Date"].notna().any():
    min_date = df["Order_Date"].min().date()
    max_date = df["Order_Date"].max().date()
    date_range = st.sidebar.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["Order_Date"].dt.date >= start_date)
                & (df["Order_Date"].dt.date <= end_date)]

# City Filter
if "City" in df.columns:
    cities = ["All"] + sorted([str(c) for c in df["City"].dropna().unique()])
    selected_city = st.sidebar.selectbox("City", cities)
    if selected_city != "All":
        df = df[df["City"] == selected_city]

# Cuisine Filter
if "Cuisine_Type" in df.columns:
    cuisines = ["All"] + sorted([str(c)
                                for c in df["Cuisine_Type"].dropna().unique()])
    selected_cuisine = st.sidebar.selectbox("Cuisine Type", cuisines)
    if selected_cuisine != "All":
        df = df[df["Cuisine_Type"] == selected_cuisine]

# Order Status Filter
if "Order_Status" in df.columns:
    statuses = ["All"] + sorted([str(s)
                                for s in df["Order_Status"].dropna().unique()])
    selected_status = st.sidebar.selectbox("Order Status", statuses)
    if selected_status != "All":
        df = df[df["Order_Status"] == selected_status]

# --- MAIN DASHBOARD ---
st.title("🍔 Online Food Delivery Dashboard")
st.markdown(
    "Overview of operational performance, order status, delivery efficiency, and profitability.")

st.divider()

# --- KEY METRICS ---
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

# 1. Total Orders
total_orders = len(df)

# 2. Total Revenue (Using Final_Amount if available, falling back to Order_Value)
delivered_df = df[df["Order_Status"] ==
                  "Delivered"] if "Order_Status" in df.columns else df

if "Final_Amount" in df.columns and df["Final_Amount"].notna().any():
    total_revenue = delivered_df["Final_Amount"].sum()
elif "Order_Value" in df.columns:
    total_revenue = delivered_df["Order_Value"].sum()
else:
    total_revenue = 0

# 3. Average Order Value
if "Order_Value" in df.columns and df["Order_Value"].notna().any():
    avg_order_value = df["Order_Value"].mean()
elif "Final_Amount" in df.columns and df["Final_Amount"].notna().any():
    avg_order_value = df["Final_Amount"].mean()
else:
    avg_order_value = 0

# 4. Average Delivery Time
avg_delivery_time = df["Delivery_Time_Min"].mean(
) if "Delivery_Time_Min" in df.columns else 0

# 5. Cancellation Rate
if "Order_Status" in df.columns and total_orders > 0:
    cancellation_count = (df["Order_Status"] == "Cancelled").sum()
    cancellation_rate = (cancellation_count / total_orders) * 100
else:
    cancellation_rate = 0

# 6. Average Delivery Rating
avg_delivery_rating = df["Delivery_Rating"].mean(
) if "Delivery_Rating" in df.columns else 0

# 7. Profit Margin %
if "Profit_Margin" in df.columns:
    profit_margin_pct = df["Profit_Margin"].mean() * 100
else:
    profit_margin_pct = 0

with col1:
    st.metric(label="Total Orders", value=f"{total_orders:,}")

with col2:
    st.metric(label="Total Revenue", value=f"₹{total_revenue:,.2f}")

with col3:
    st.metric(label="Avg Order Value", value=f"₹{avg_order_value:,.2f}")

with col4:
    st.metric(label="Avg Delivery Time", value=f"{avg_delivery_time:.1f} mins")

with col5:
    st.metric(label="Cancellation Rate", value=f"{cancellation_rate:.2f}%")

with col6:
    st.metric(label="Avg Delivery Rating",
              value=f"{avg_delivery_rating:.2f} ⭐")

with col7:
    st.metric(label="Profit Margin %", value=f"{profit_margin_pct:.2f}%")

st.divider()

# --- VISUALIZATIONS ---
tab1, tab2, tab3 = st.tabs(
    ["📊 Performance & Breakdowns", "🚚 Delivery & Operations", "📋 Raw Data"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Order Status Breakdown")
        if "Order_Status" in df.columns:
            status_counts = df["Order_Status"].value_counts().reset_index()
            status_counts.columns = ["Order Status", "Count"]
            st.bar_chart(status_counts.set_index("Order Status"))
        else:
            st.info("Order Status column not available.")

    with c2:
        st.subheader("Orders by Cuisine Type")
        if "Cuisine_Type" in df.columns:
            cuisine_counts = df["Cuisine_Type"].value_counts().head(10)
            st.bar_chart(cuisine_counts)
        else:
            st.info("Cuisine Type column not available.")

with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Cancellation Reasons")
        if "Cancellation_Reason" in df.columns and df["Cancellation_Reason"].notna().any():
            cancel_reasons = df["Cancellation_Reason"].value_counts().dropna()
            st.bar_chart(cancel_reasons)
        else:
            st.info("No cancellation reasons data available.")

    with c2:
        st.subheader("Revenue by City")
        if "City" in df.columns and "Order_Value" in df.columns:
            city_rev = df.groupby(
                "City")["Order_Value"].sum().sort_values(ascending=False)
            st.bar_chart(city_rev)
        else:
            st.info("City or Order Value data not available.")

with tab3:
    st.subheader("Dataset Preview")
    st.dataframe(df, use_container_width=True)
