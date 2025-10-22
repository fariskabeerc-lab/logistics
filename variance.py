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
    item_df = pd.read_excel("ItemSearchList.xlsx")

    purchase_df.columns = purchase_df.columns.str.strip()
    item_df.columns = item_df.columns.str.strip()

    # Convert to numeric
    purchase_df["Total Purchase"] = pd.to_numeric(
        purchase_df["Total Purchase"].astype(str).str.replace(",", "").str.strip(),
        errors="coerce"
    )
    purchase_df["Qty Purchased"] = pd.to_numeric(
        purchase_df["Qty Purchased"].astype(str).str.replace(",", "").str.strip(),
        errors="coerce"
    )
    item_df["Selling"] = pd.to_numeric(
        item_df["Selling"].astype(str).str.replace(",", "").str.strip(),
        errors="coerce"
    )
    item_df["Total Sales QTY"] = pd.to_numeric(
        item_df["Total Sales QTY"].astype(str).str.replace(",", "").str.strip(),
        errors="coerce"
    )

    # Merge data
    merged_df = pd.merge(
        purchase_df,
        item_df,
        left_on="Item Code",
        right_on="Item Bar Code",
        how="inner"
    )

    # Compute derived values
    merged_df["Total Sales Value"] = merged_df["Selling"] * merged_df["Total Sales QTY"]
    return merged_df

merged_df = load_data()

# ==========================
# SIDEBAR FILTERS
# ==========================
st.sidebar.header("🔍 Filters")

supplier_search = st.sidebar.text_input("Search Supplier").strip().lower()
item_search = st.sidebar.text_input("Search Item Name").strip().lower()
barcode_search = st.sidebar.text_input("Search Item Code / Barcode").strip().lower()

# Category filter
category_options = ["All"] + sorted(merged_df["Category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", category_options)

# Brand filter
brand_options = ["All"] + sorted(merged_df["Brand"].dropna().unique().tolist())
selected_brand = st.sidebar.selectbox("Select Brand", brand_options)

# ==========================
# APPLY FILTERS
# ==========================
filtered_df = merged_df.copy()

# Supplier search filter
if supplier_search:
    filtered_df = filtered_df[
        filtered_df["LP Supplier"].fillna("").str.lower().str.contains(supplier_search)
    ]

# Item search filter
if item_search:
    filtered_df = filtered_df[
        filtered_df["Items"].fillna("").str.lower().str.contains(item_search)
    ]

# Barcode/Item Code filter
if barcode_search:
    filtered_df = filtered_df[
        filtered_df["Item Code"].astype(str).str.contains(barcode_search, case=False, na=False)
        | filtered_df["Item Bar Code"].astype(str).str.contains(barcode_search, case=False, na=False)
    ]

# Category filter
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# Brand filter
if selected_brand != "All":
    filtered_df = filtered_df[filtered_df["Brand"] == selected_brand]

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
# DISPLAY TABLE
# ==========================
st.markdown("### 🧮 Filtered Item Details")
st.dataframe(
    filtered_df[
        [
            "Item Code",
            "Items",
            "Category",
            "Brand",
            "LP Supplier",
            "Qty Purchased",
            "Total Purchase",
            "Selling",
            "Total Sales QTY",
            "Total Sales Value",
            "Cost",
            "Selling"
        ]
    ],
    use_container_width=True,
    height=600
)
