import streamlit as st
import pandas as pd

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(page_title="Purchase & Sales Insights Dashboard", layout="wide")
st.title("📦 Purchase & Sales Insights Dashboard")

# ==========================
# LOAD DATA ONCE
# ==========================
@st.cache_data
def load_data():
    purchase_df = pd.read_excel("supplier jan to sep.Xlsx")
    item_df = pd.read_excel("item analysis jan to sep.xlsx")

    purchase_df.columns = purchase_df.columns.str.strip()
    item_df.columns = item_df.columns.str.strip()

    # Merge once
    merged_df = pd.merge(
        purchase_df,
        item_df,
        left_on="Item Code",
        right_on="Item Bar Code",
        how="inner"
    )

    # Calculate Total Sales Value
    merged_df["Total Sales Value"] = merged_df["Selling"] * merged_df["Total Sales QTY"]
    return merged_df

merged_df = load_data()

# ==========================
# SIDEBAR FILTERS
# ==========================
st.sidebar.header("🔍 Filters")

supplier_options = ["All"] + sorted(merged_df["LP Supplier"].dropna().unique().tolist())
category_options = ["All"] + sorted(merged_df["Category"].dropna().unique().tolist())

# Single-select dropdowns
selected_supplier = st.sidebar.selectbox("Select LP Supplier", supplier_options)
selected_category = st.sidebar.selectbox("Select Category", category_options)

# ==========================
# APPLY FILTERS
# ==========================
filtered_df = merged_df.copy()

if selected_supplier != "All":
    filtered_df = filtered_df[filtered_df["LP Supplier"] == selected_supplier]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# ==========================
# KEY INSIGHTS
# ==========================
total_purchase_value = filtered_df["Total Purchase"].sum()
total_sales_qty = filtered_df["Total Sales QTY"].sum()
total_sales_value = filtered_df["Total Sales Value"].sum()
total_items = filtered_df["Item Code"].nunique()

st.markdown("### 📊 Key Insights")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Purchase Value", f"{total_purchase_value:,.2f}")
col2.metric("📦 Total Sales Qty", f"{total_sales_qty:,.0f}")
col3.metric("💵 Total Sales Value", f"{total_sales_value:,.2f}")
col4.metric("🧾 Total Items Purchased", total_items)

# ==========================
# DISPLAY FILTERED TABLE
# ==========================
st.markdown("### 🧮 Filtered Item Details")
st.dataframe(
    filtered_df[
        [
            "Item Code",
            "Items",
            "Category",
            "LP Supplier",
            "Qty Purchased",
            "Total Purchase",
            "Selling",
            "Total Sales QTY",
            "Total Sales Value",
        ]
    ],
    use_container_width=True,
    height=600
)
