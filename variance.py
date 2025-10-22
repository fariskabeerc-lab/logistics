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

    # Clean column names
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

    # Derived column
    item_df["Total Sales Value"] = item_df["Selling"] * item_df["Total Sales QTY"]

    # Merge
    merged_df = pd.merge(
        purchase_df,
        item_df,
        left_on="Item Code",
        right_on="Item Bar Code",
        how="inner"
    )

    # Derived column in merged df
    merged_df["Total Sales Value"] = merged_df["Selling"] * merged_df["Total Sales QTY"]

    return purchase_df, item_df, merged_df


purchase_df, item_df, merged_df = load_data()

# ==========================
# SIDEBAR FILTERS
# ==========================
st.sidebar.header("🔍 Filters")

supplier_search = st.sidebar.text_input("Search LP Supplier").strip().lower()
item_search = st.sidebar.text_input("Search Item Name").strip().lower()
barcode_search = st.sidebar.text_input("Search Item Code / Barcode").strip().lower()

# Check available columns
available_columns = [c.strip().lower() for c in merged_df.columns]

# Identify category and brand column names automatically
category_col = None
brand_col = None

for c in merged_df.columns:
    cname = c.strip().lower()
    if cname in ["category", "item category", "cat"]:
        category_col = c
    if cname in ["brand", "brand name", "brd"]:
        brand_col = c

# --- Category filter ---
if category_col:
    category_options = ["All"] + sorted(merged_df[category_col].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", category_options)
else:
    st.sidebar.warning("⚠️ No 'Category' column found in file.")
    selected_category = "All"

# --- Brand filter ---
if brand_col:
    brand_options = ["All"] + sorted(merged_df[brand_col].dropna().unique().tolist())
    selected_brand = st.sidebar.selectbox("Select Brand", brand_options)
else:
    st.sidebar.warning("⚠️ No 'Brand' column found in file.")
    selected_brand = "All"

# ==========================
# APPLY FILTERS
# ==========================
filtered_df = merged_df.copy()

# LP Supplier search
if supplier_search:
    filtered_df = filtered_df[
        filtered_df["LP Supplier"].fillna("").str.lower().str.contains(supplier_search)
    ]

# Item name search
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
if category_col and selected_category != "All":
    filtered_df = filtered_df[filtered_df[category_col] == selected_category]

# Brand filter
if brand_col and selected_brand != "All":
    filtered_df = filtered_df[filtered_df[brand_col] == selected_brand]

# ==========================
# KEY INSIGHTS
# ==========================
# 1️⃣ Excel totals (direct from original files)
total_purchase_excel = purchase_df["Total Purchase"].sum()
total_sales_qty_excel = item_df["Total Sales QTY"].sum()
total_sales_value_excel = item_df["Total Sales Value"].sum()
total_items_excel = purchase_df["Item Code"].nunique()

# 2️⃣ Filtered totals (after applying sidebar filters)
total_purchase_filtered = filtered_df["Total Purchase"].sum()
total_sales_qty_filtered = filtered_df["Total Sales QTY"].sum()
total_sales_value_filtered = filtered_df["Total Sales Value"].sum()
total_items_filtered = filtered_df["Item Code"].nunique()

# Display Excel and filtered totals
st.markdown("### 📊 Key Insights — Excel Totals (Full Data)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Purchase (Excel)", f"{total_purchase_excel:,.2f}")
col2.metric("📦 Total Sales Qty (Excel)", f"{total_sales_qty_excel:,.0f}")
col3.metric("💵 Total Sales Value (Excel)", f"{total_sales_value_excel:,.2f}")
col4.metric("🧾 Total Items (Excel)", f"{total_items_excel:,}")

st.markdown("### 🔎 Key Insights — Filtered Totals (After Applying Filters)")
fcol1, fcol2, fcol3, fcol4 = st.columns(4)
fcol1.metric("💰 Total Purchase (Filtered)", f"{total_purchase_filtered:,.2f}")
fcol2.metric("📦 Total Sales Qty (Filtered)", f"{total_sales_qty_filtered:,.0f}")
fcol3.metric("💵 Total Sales Value (Filtered)", f"{total_sales_value_filtered:,.2f}")
fcol4.metric("🧾 Total Items (Filtered)", f"{total_items_filtered:,}")

# ==========================
# DISPLAY TABLE
# ==========================
st.markdown("### 🧮 Filtered Item Details")

# Display columns dynamically (ignore missing)
display_cols = [
    c for c in [
        "Item Code",
        "Items",
        category_col,
        brand_col,
        "LP Supplier",
        "Qty Purchased",
        "Total Purchase",
        "Selling",
        "Total Sales QTY",
        "Total Sales Value",
    ] if c in filtered_df.columns
]

st.dataframe(filtered_df[display_cols], use_container_width=True, height=600)

# Optional: show available columns for debugging
with st.expander("🧾 Show All Columns in Data"):
    st.write(list(merged_df.columns))
