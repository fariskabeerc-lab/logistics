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

    # clean column names
    purchase_df.columns = purchase_df.columns.str.strip()
    item_df.columns = item_df.columns.str.strip()

    # Convert to numeric (remove commas, spaces)
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

    # Pre-compute a sales value column in the item dataframe
    item_df["Total Sales Value"] = item_df["Selling"] * item_df["Total Sales QTY"]

    # Merge data (keep as inner as you had)
    merged_df = pd.merge(
        purchase_df,
        item_df,
        left_on="Item Code",
        right_on="Item Bar Code",
        how="inner"
    )

    # Also compute derived values on merged df for consistency
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

# Category filter (use merged_df to get categories/brand list)
category_options = ["All"] + sorted(merged_df["Category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", category_options)

brand_options = ["All"] + sorted(merged_df["Brand"].dropna().unique().tolist())
selected_brand = st.sidebar.selectbox("Select Brand", brand_options)

# ==========================
# APPLY FILTERS (on merged_df so table shows joined info)
# ==========================
filtered_df = merged_df.copy()

if supplier_search:
    filtered_df = filtered_df[
        filtered_df["LP Supplier"].fillna("").str.lower().str.contains(supplier_search)
    ]

if item_search:
    filtered_df = filtered_df[
        filtered_df["Items"].fillna("").str.lower().str.contains(item_search)
    ]

if barcode_search:
    filtered_df = filtered_df[
        filtered_df["Item Code"].astype(str).str.contains(barcode_search, case=False, na=False)
        | filtered_df["Item Bar Code"].astype(str).str.contains(barcode_search, case=False, na=False)
    ]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

if selected_brand != "All":
    filtered_df = filtered_df[filtered_df["Brand"] == selected_brand]

# ==========================
# KEY INSIGHTS
# ==========================
# 1) Totals from the original Excel sheets (these are the "Excel sums" you expect)
total_purchase_excel = purchase_df["Total Purchase"].sum()
total_sales_qty_excel = item_df["Total Sales QTY"].sum()
total_sales_value_excel = item_df["Total Sales Value"].sum()
total_items_excel = purchase_df["Item Code"].nunique()

# 2) Totals from the currently filtered merged dataframe (what dashboard filters produce)
total_purchase_filtered = filtered_df["Total Purchase"].sum()
total_sales_qty_filtered = filtered_df["Total Sales QTY"].sum()
total_sales_value_filtered = filtered_df["Total Sales Value"].sum()
total_items_filtered = filtered_df["Item Code"].nunique()

st.markdown("### 📊 Key Insights — Excel totals vs Filtered totals (merged)")
excel_col1, excel_col2, excel_col3, excel_col4 = st.columns(4)
excel_col1.metric("💰 Total Purchase (Excel)", f"{total_purchase_excel:,.2f}")
excel_col2.metric("📦 Total Sales Qty (Excel)", f"{total_sales_qty_excel:,.0f}")
excel_col3.metric("💵 Total Sales Value (Excel)", f"{total_sales_value_excel:,.2f}")
excel_col4.metric("🧾 Total Items (Excel)", f"{total_items_excel:,}")

st.markdown("### 📊 Filtered / Merged totals (reflecting current filters)")
f_col1, f_col2, f_col3, f_col4 = st.columns(4)
f_col1.metric("💰 Total Purchase (Filtered)", f"{total_purchase_filtered:,.2f}")
f_col2.metric("📦 Total Sales Qty (Filtered)", f"{total_sales_qty_filtered:,.0f}")
f_col3.metric("💵 Total Sales Value (Filtered)", f"{total_sales_value_filtered:,.2f}")
f_col4.metric("🧾 Total Items (Filtered)", f"{total_items_filtered:,}")

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
        ]
    ],
    use_container_width=True,
    height=600
)
