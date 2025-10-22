import streamlit as st
import pandas as pd

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(page_title="Purchase & Sales Insights Dashboard", layout="wide")
st.title("📦 Purchase & Sales Insights Dashboard")

# ==========================
# READ LOCAL FILES
# ==========================
# 🔹 Replace with your actual file paths
purchase_file = "supplier jan to sep.Xlsx"
item_file = "item analysis jan to sep.xlsx"

# Read Excel files
purchase_df = pd.read_excel(purchase_file)
item_df = pd.read_excel(item_file)

# ==========================
# CLEAN & MERGE DATA
# ==========================
purchase_df.columns = purchase_df.columns.str.strip()
item_df.columns = item_df.columns.str.strip()

merged_df = pd.merge(
    purchase_df,
    item_df,
    left_on="Item Code",
    right_on="Item Bar Code",
    how="inner"
)

# ==========================
# CALCULATIONS
# ==========================
merged_df["Total Sales Value"] = merged_df["Selling"] * merged_df["Total Sales QTY"]

# ==========================
# SIDEBAR FILTERS
# ==========================
st.sidebar.header("🔍 Filters")

all_suppliers = sorted(merged_df["LP Supplier"].dropna().unique().tolist())
all_categories = sorted(merged_df["Category"].dropna().unique().tolist())

selected_suppliers = st.sidebar.multiselect(
    "Select LP Supplier(s)",
    options=["All"] + all_suppliers,
    default=["All"]
)

selected_categories = st.sidebar.multiselect(
    "Select Category(ies)",
    options=["All"] + all_categories,
    default=["All"]
)

filtered_df = merged_df.copy()

# Apply supplier filter
if "All" not in selected_suppliers:
    filtered_df = filtered_df[filtered_df["LP Supplier"].isin(selected_suppliers)]

# Apply category filter
if "All" not in selected_categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

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
