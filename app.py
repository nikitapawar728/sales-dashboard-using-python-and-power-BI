"""
Advanced Sales Analytics & Business Intelligence Platform
Enterprise Intelligence Portal Built with Python, SQL, Machine Learning & Power BI.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Ensure project root and its parent are in sys.path for deployment environments
# that mount the repo under a different directory structure.
BASE_DIR = Path(__file__).resolve().parent
for candidate in (BASE_DIR, BASE_DIR.parent):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

try:
    from src.config import PROCESSED_DATA_DIR, EXPORTS_DIR, SALES_REQUIRED_COLUMNS, ensure_demo_data
except ModuleNotFoundError:
    import importlib.util

    config_candidates = [
        BASE_DIR / "src" / "config.py",
        BASE_DIR.parent / "src" / "config.py",
    ]
    config_path = next((p for p in config_candidates if p.exists()), None)
    if config_path is None:
        raise

    spec = importlib.util.spec_from_file_location("compat_config", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    PROCESSED_DATA_DIR = config_module.PROCESSED_DATA_DIR
    EXPORTS_DIR = config_module.EXPORTS_DIR
    SALES_REQUIRED_COLUMNS = config_module.SALES_REQUIRED_COLUMNS
    ensure_demo_data = config_module.ensure_demo_data

ensure_demo_data()

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Advanced Sales Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Clean Executive CSS Styling
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }

    /* Modern KPI Metric Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-badge {
        display: inline-flex;
        align-items: center;
        margin-top: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 6px;
    }
    .badge-blue { background: #EFF6FF; color: #2563EB; }
    .badge-green { background: #ECFDF5; color: #059669; }
    .badge-purple { background: #FAF5FF; color: #7C3AED; }
    .badge-amber { background: #FFFBEB; color: #D97706; }
    .badge-red { background: #FEF2F2; color: #DC2626; }

    /* Clean Insight Alert Box */
    .insight-card {
        background: #FFFFFF;
        border-left: 4px solid #3B82F6;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .insight-positive { border-left-color: #10B981; }
    .insight-warning { border-left-color: #F59E0B; }
    .insight-alert { border-left-color: #EF4444; }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 4px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 14px;
        font-weight: 600;
        color: #64748B;
        font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom: 2px solid #2563EB !important;
    }
</style>
""", unsafe_allow_html=True)


PROFILE_FILE = BASE_DIR / "data" / "user_profiles.csv"
PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)


def ensure_profile_file():
    if not PROFILE_FILE.exists():
        empty_df = pd.DataFrame(columns=[
            "username", "full_name", "email", "password", "role", "created_at"
        ])
        empty_df.to_csv(PROFILE_FILE, index=False)


def load_profiles():
    ensure_profile_file()
    profiles_df = pd.read_csv(PROFILE_FILE)
    if profiles_df.empty:
        return profiles_df
    for required_col in ["username", "full_name", "email", "password", "role", "created_at"]:
        if required_col not in profiles_df.columns:
            profiles_df[required_col] = ""
    return profiles_df


def save_profiles(profiles_df):
    profiles_df = profiles_df.copy()
    profiles_df.to_csv(PROFILE_FILE, index=False)


if "user" not in st.session_state:
    st.session_state.user = None
if "guest_mode" not in st.session_state:
    st.session_state.guest_mode = False
if "auth_open" not in st.session_state:
    st.session_state.auth_open = False


def login_flow():
    st.subheader("🔐 Login / Create Profile")
    st.caption("Sign in to manage your profile, or continue with the dashboard as a guest.")

    login_tab, signup_tab = st.tabs(["Login", "Create Profile"])

    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        col_login, col_guest = st.columns([1, 1])
        with col_login:
            if st.button("Login", use_container_width=True):
                if not username.strip() or not password.strip():
                    st.warning("Please enter both username and password.")
                else:
                    profiles = load_profiles()
                    match = profiles[profiles["username"].astype(str).str.lower() == username.strip().lower()]
                    if match.empty:
                        st.error("No account found for this username.")
                    elif str(match.iloc[0]["password"]).strip() != password:
                        st.error("Incorrect password.")
                    else:
                        profile_row = match.iloc[0].to_dict()
                        st.session_state.user = {
                            "username": profile_row.get("username", username.strip()),
                            "full_name": profile_row.get("full_name", username.strip()),
                            "email": profile_row.get("email", ""),
                            "role": profile_row.get("role", "Viewer"),
                        }
                        st.session_state.guest_mode = False
                        st.success(f"Welcome back, {profile_row.get('full_name', username.strip())}!")
                        st.rerun()

        with col_guest:
            if st.button("Continue as Guest", use_container_width=True):
                st.session_state.user = None
                st.session_state.guest_mode = True
                st.rerun()

    with signup_tab:
        full_name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        new_username = st.text_input("Create Username", key="signup_username")
        new_password = st.text_input("Create Password", type="password", key="signup_password")
        role = st.selectbox("Role", ["Viewer", "Manager", "Analyst"], index=0, key="signup_role")

        if st.button("Create Profile", use_container_width=True):
            errors = []
            if not full_name.strip():
                errors.append("Full name is required.")
            if not new_username.strip():
                errors.append("Username is required.")
            if not new_password.strip():
                errors.append("Password is required.")
            if not email.strip():
                errors.append("Email is required.")

            if errors:
                for msg in errors:
                    st.warning(msg)
            else:
                profiles = load_profiles()
                exists = profiles[profiles["username"].astype(str).str.lower() == new_username.strip().lower()]
                if not exists.empty:
                    st.error("This username is already taken. Please choose a different one.")
                else:
                    new_row = {
                        "username": new_username.strip(),
                        "full_name": full_name.strip(),
                        "email": email.strip(),
                        "password": new_password.strip(),
                        "role": role,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    profiles = pd.concat([profiles, pd.DataFrame([new_row])], ignore_index=True)
                    save_profiles(profiles)
                    st.session_state.user = {
                        "username": new_username.strip(),
                        "full_name": full_name.strip(),
                        "email": email.strip(),
                        "role": role,
                    }
                    st.session_state.guest_mode = False
                    st.success("Profile created successfully. You are now signed in.")
                    st.rerun()


# -----------------------------------------------------------------------------
# Data Loader (Cached for fast interactive exploration)
# -----------------------------------------------------------------------------
def read_csv_safely(path, columns=None):
    """Return an empty DataFrame for missing or empty CSVs instead of crashing."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=columns or [])
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns or [])
    if columns:
        for col in columns:
            if col not in df.columns:
                df[col] = pd.Series(dtype="object")
    return df


@st.cache_data(ttl=600)
def load_analytics_datasets():
    """Loads cleaned master data, customer segments, forecasting, anomalies, and insights."""
    master_path = PROCESSED_DATA_DIR / "cleaned_sales_master.csv"
    rfm_path = PROCESSED_DATA_DIR / "ml_customer_segments.csv"
    forecast_path = PROCESSED_DATA_DIR / "ml_sales_forecast.csv"
    metrics_path = PROCESSED_DATA_DIR / "forecast_model_metrics.csv"
    anomalies_path = PROCESSED_DATA_DIR / "ml_sales_anomalies.csv"
    insights_path = PROCESSED_DATA_DIR / "business_insights.csv"

    master_df = read_csv_safely(master_path, columns=SALES_REQUIRED_COLUMNS)
    rfm_df = read_csv_safely(rfm_path)
    forecast_df = read_csv_safely(forecast_path)
    metrics_df = read_csv_safely(metrics_path)
    anomalies_df = read_csv_safely(anomalies_path)
    insights_df = read_csv_safely(insights_path)

    if not master_df.empty and "Order_Date" in master_df.columns:
        master_df["Order_Date"] = pd.to_datetime(master_df["Order_Date"])
        master_df["Year"] = master_df["Order_Date"].dt.year
        master_df["Month"] = master_df["Order_Date"].dt.month
        master_df["YearMonth"] = master_df["Order_Date"].dt.to_period("M").astype(str)
        master_df["Month_Name"] = master_df["Order_Date"].dt.strftime("%b %Y")
        master_df["Day_Name"] = master_df["Order_Date"].dt.day_name()
        master_df["Quarter"] = "Q" + master_df["Order_Date"].dt.quarter.astype(str)

    if not forecast_df.empty and "forecast_date" in forecast_df.columns:
        forecast_df["forecast_date"] = pd.to_datetime(forecast_df["forecast_date"])

    return master_df, rfm_df, forecast_df, metrics_df, anomalies_df, insights_df


df_sales, df_rfm, df_forecast, df_metrics, df_anomalies, df_insights = load_analytics_datasets()

if df_sales.empty or "Order_Date" not in df_sales.columns:
    st.error("⚠️ Sales dataset is missing or incomplete. A demo dataset has been created; if you want production data, run `python src/etl_pipeline.py`.")
    st.stop()


# -----------------------------------------------------------------------------
# Sidebar: Slicers & Global Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("📊 Sales Analytics")
    if st.session_state.user:
        st.caption(f"Signed in as: {st.session_state.user['full_name']} ({st.session_state.user['role']})")
    else:
        st.caption("Guest mode")
    st.markdown("---")

    if not st.session_state.user and not st.session_state.guest_mode:
        auth_cols = st.columns([1, 1])
        with auth_cols[0]:
            if st.button("Login", key="sidebar_login_small", use_container_width=True):
                st.session_state.auth_open = True
        with auth_cols[1]:
            if st.button("Guest", key="sidebar_guest_small", use_container_width=True):
                st.session_state.guest_mode = True
                st.rerun()
    elif st.session_state.user:
        st.subheader("👤 Profile")
        st.write(f"**Name:** {st.session_state.user['full_name']}")
        st.write(f"**Username:** {st.session_state.user['username']}")
        st.write(f"**Email:** {st.session_state.user['email']}")
        st.write(f"**Role:** {st.session_state.user['role']}")

        with st.expander("Update profile"):
            profiles = load_profiles()
            profile_match = profiles[profiles["username"].astype(str).str.lower() == st.session_state.user["username"].strip().lower()]
            if not profile_match.empty:
                current = profile_match.iloc[0]
                updated_name = st.text_input("Full Name", value=current.get("full_name", ""), key="sidebar_name")
                updated_email = st.text_input("Email", value=current.get("email", ""), key="sidebar_email")
                updated_role = st.selectbox("Role", ["Viewer", "Manager", "Analyst"], index=["Viewer", "Manager", "Analyst"].index(current.get("role", "Viewer")), key="sidebar_role")
                if st.button("Save profile changes", use_container_width=True):
                    user_idx = profiles.index[profiles["username"].astype(str).str.lower() == st.session_state.user["username"].strip().lower()].tolist()
                    if user_idx:
                        profiles.loc[user_idx[0], "full_name"] = updated_name.strip()
                        profiles.loc[user_idx[0], "email"] = updated_email.strip()
                        profiles.loc[user_idx[0], "role"] = updated_role
                        save_profiles(profiles)
                        st.session_state.user = {
                            "username": st.session_state.user["username"],
                            "full_name": updated_name.strip(),
                            "email": updated_email.strip(),
                            "role": updated_role,
                        }
                        st.success("Profile updated successfully.")
                        st.rerun()

        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.guest_mode = False
            st.session_state.auth_open = False
            st.rerun()
    else:
        auth_cols = st.columns([1, 1])
        with auth_cols[0]:
            if st.button("Login", use_container_width=True):
                st.session_state.auth_open = True
        with auth_cols[1]:
            if st.button("Exit", use_container_width=True):
                st.session_state.guest_mode = False
                st.rerun()

    st.markdown("---")

    # Currency format switcher
    currency = st.radio("Currency Format", ["₹ (INR)", "$ (USD)"], horizontal=True)

    if st.session_state.auth_open:
        st.markdown("---")
        login_flow()
        if st.button("Close login", use_container_width=True):
            st.session_state.auth_open = False
            st.rerun()


if st.session_state.user is not None:
    st.caption(f"Signed in as: {st.session_state.user['full_name']} • {st.session_state.user['role']}")
else:
    st.caption("Dashboard preview mode: you can explore the dashboard. Sign in any time to create and manage your profile.")
    if st.button("🔐 Login / Create Profile", use_container_width=False):
        st.session_state.auth_open = True

curr_symbol = "₹" if "INR" in currency else "$"
curr_rate = 1.0 if "INR" in currency else 0.012


def format_money(val):
    """Formats numbers into clean readable currency."""
    if pd.isna(val) or val is None:
        return f"{curr_symbol}0"
    val = float(val) * curr_rate
    if abs(val) >= 1e7 and curr_symbol == "₹":
        return f"₹{val / 1e7:.2f} Cr"
    elif abs(val) >= 1e5 and curr_symbol == "₹":
        return f"₹{val / 1e5:.2f} L"
    elif abs(val) >= 1e6:
        return f"{curr_symbol}{val / 1e6:.2f}M"
    elif abs(val) >= 1e3:
        return f"{curr_symbol}{val / 1e3:.1f}k"
    return f"{curr_symbol}{val:,.0f}"


if st.session_state.auth_open:
    st.markdown("---")
    login_flow()

st.markdown("### 🎛️ Interactive Filters")

# Date Range Slicer
min_date = df_sales["Order_Date"].min().date()
max_date = df_sales["Order_Date"].max().date()

date_selection = st.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if isinstance(date_selection, (tuple, list)) and len(date_selection) == 2:
    start_date, end_date = date_selection
else:
    start_date, end_date = min_date, max_date

# Region Slicer
all_regions = sorted(df_sales["Region"].dropna().unique().tolist())
selected_regions = st.multiselect("Region", options=all_regions, default=all_regions)

# Category Slicer
all_categories = sorted(df_sales["Category"].dropna().unique().tolist())
selected_categories = st.multiselect("Category", options=all_categories, default=all_categories)

# Sales Channel Slicer
all_channels = sorted(df_sales["Sales_Channel"].dropna().unique().tolist()) if "Sales_Channel" in df_sales.columns else []
selected_channels = st.multiselect("Sales Channel", options=all_channels, default=all_channels)

# Sales Rep Slicer
all_reps = sorted(df_sales["Sales_Representative"].dropna().unique().tolist()) if "Sales_Representative" in df_sales.columns else []
selected_reps = st.multiselect("Sales Representative", options=all_reps, default=all_reps)

st.markdown("---")
st.caption(f"📅 Active Range: {min_date} to {max_date}")
st.caption(f"⚡ Total Records: {len(df_sales):,}")


# -----------------------------------------------------------------------------
# Filter Master Data
# -----------------------------------------------------------------------------
filtered_df = df_sales[
    (df_sales["Order_Date"].dt.date >= start_date) &
    (df_sales["Order_Date"].dt.date <= end_date) &
    (df_sales["Region"].isin(selected_regions if selected_regions else all_regions)) &
    (df_sales["Category"].isin(selected_categories if selected_categories else all_categories)) &
    (df_sales["Sales_Channel"].isin(selected_channels if selected_channels else all_channels)) &
    (df_sales["Sales_Representative"].isin(selected_reps if selected_reps else all_reps))
]

if filtered_df.empty:
    st.warning("No transactions match the selected filters. Please adjust your selections.")
    st.stop()


# -----------------------------------------------------------------------------
# Global Executive KPIs (Summary Ribbon)
# -----------------------------------------------------------------------------
total_revenue = filtered_df["Net_Sales"].sum()
total_profit = filtered_df["Profit"].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
total_orders = filtered_df["Order_ID"].nunique()
total_customers = filtered_df["Customer_ID"].nunique()
total_units = filtered_df["Quantity"].sum()
aov = (total_revenue / total_orders) if total_orders > 0 else 0

st.title("📊 Advanced Sales Analytics & Business Intelligence")
st.caption(f"🏢 Enterprise Analytics Platform • Filtered Dataset: **{len(filtered_df):,}** Transactions across **{total_orders:,}** Orders")

# 5 Top KPI Metric Cards
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 Total Revenue</div>
        <div class="kpi-value">{format_money(total_revenue)}</div>
        <div class="kpi-badge badge-blue">📦 {total_orders:,} Orders</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📈 Total Net Profit</div>
        <div class="kpi-value">{format_money(total_profit)}</div>
        <div class="kpi-badge badge-green">🎯 {profit_margin:.1f}% Margin</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🛒 Total Units Sold</div>
        <div class="kpi-value">{total_units:,.0f}</div>
        <div class="kpi-badge badge-purple">🛍️ Across {filtered_df['Product_ID'].nunique()} Products</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">👥 Active Customers</div>
        <div class="kpi-value">{total_customers:,}</div>
        <div class="kpi-badge badge-amber">👤 Accounts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💳 Average Order Value</div>
        <div class="kpi-value">{format_money(aov)}</div>
        <div class="kpi-badge badge-blue">AOV / Order</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 9 Core Pages (Tabs matching the complete MSc IT specification)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "1️⃣ Executive Overview",
    "2️⃣ Sales Performance",
    "3️⃣ Product Analytics",
    "4️⃣ Customer Intelligence",
    "5️⃣ Regional Analytics",
    "6️⃣ Sales Rep Performance",
    "7️⃣ AI Forecasting",
    "8️⃣ Business Insights",
    "9️⃣ Anomaly Detection",
    "📁 Data Explorer & Export"
])


# =============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =============================================================================
with tab1:
    st.subheader("1. Executive Overview")

    # Monthly Sales Revenue & Profit Combo Trend
    monthly_df = filtered_df.groupby("YearMonth").agg(
        Revenue=("Net_Sales", "sum"),
        Profit=("Profit", "sum")
    ).reset_index()

    fig_exec = go.Figure()
    fig_exec.add_trace(go.Bar(
        x=monthly_df["YearMonth"],
        y=monthly_df["Revenue"] * curr_rate,
        name="Total Revenue",
        marker_color="#3B82F6"
    ))
    fig_exec.add_trace(go.Scatter(
        x=monthly_df["YearMonth"],
        y=monthly_df["Profit"] * curr_rate,
        name="Net Profit",
        mode="lines+markers",
        line=dict(color="#10B981", width=3),
        marker=dict(size=7)
    ))
    fig_exec.update_layout(
        title="<b>Monthly Sales Revenue vs. Net Profit Trend</b>",
        xaxis_title="Month",
        yaxis_title=f"Amount ({curr_symbol})",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_exec, use_container_width=True)

    col1_1, col1_2 = st.columns(2)
    with col1_1:
        cat_df = filtered_df.groupby("Category").agg(
            Revenue=("Net_Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index().sort_values("Revenue", ascending=True)

        fig_cat = px.bar(
            cat_df,
            y="Category",
            x=cat_df["Revenue"] * curr_rate,
            orientation="h",
            title="<b>Category-Wise Revenue & Profit</b>",
            labels={"x": f"Revenue ({curr_symbol})", "Category": "Category"},
            color="Profit",
            color_continuous_scale="Blues",
            template="plotly_white"
        )
        fig_cat.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col1_2:
        reg_df = filtered_df.groupby("Region")["Net_Sales"].sum().reset_index()
        fig_reg = px.pie(
            reg_df,
            names="Region",
            values="Net_Sales",
            title="<b>Regional Sales Share</b>",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold,
            template="plotly_white"
        )
        fig_reg.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_reg, use_container_width=True)

    # Top 10 vs Bottom 10 Products
    col_t10, col_b10 = st.columns(2)
    prod_agg = filtered_df.groupby(["Product_Name", "Category"]).agg(
        Revenue=("Net_Sales", "sum"),
        Profit=("Profit", "sum"),
        Units=("Quantity", "sum")
    ).reset_index()
    prod_agg["Margin_%"] = (prod_agg["Profit"] / prod_agg["Revenue"] * 100).round(1)

    with col_t10:
        top10 = prod_agg.sort_values("Revenue", ascending=False).head(10)
        fig_t10 = px.bar(
            top10.sort_values("Revenue", ascending=True),
            y="Product_Name",
            x=top10.sort_values("Revenue", ascending=True)["Revenue"] * curr_rate,
            orientation="h",
            title="<b>🏆 Top 10 Revenue Generating Products</b>",
            labels={"x": f"Revenue ({curr_symbol})", "Product_Name": "Product"},
            color="Profit",
            color_continuous_scale="Greens",
            template="plotly_white"
        )
        fig_t10.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_t10, use_container_width=True)

    with col_b10:
        bot10 = prod_agg.sort_values("Revenue", ascending=True).head(10)
        fig_b10 = px.bar(
            bot10,
            y="Product_Name",
            x=bot10["Revenue"] * curr_rate,
            orientation="h",
            title="<b>⚠️ Bottom 10 Revenue Products</b>",
            labels={"x": f"Revenue ({curr_symbol})", "Product_Name": "Product"},
            color="Margin_%",
            color_continuous_scale="Reds",
            template="plotly_white"
        )
        fig_b10.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_b10, use_container_width=True)


# =============================================================================
# PAGE 2: SALES PERFORMANCE
# =============================================================================
with tab2:
    st.subheader("2. Detailed Sales Performance & Channel Analysis")

    col2_1, col2_2 = st.columns(2)
    with col2_1:
        # Sales by Channel
        channel_df = filtered_df.groupby("Sales_Channel").agg(
            Revenue=("Net_Sales", "sum"),
            Orders=("Order_ID", "nunique")
        ).reset_index().sort_values("Revenue", ascending=False)

        fig_chan = px.bar(
            channel_df,
            x="Sales_Channel",
            y=channel_df["Revenue"] * curr_rate,
            color="Sales_Channel",
            title="<b>Revenue by Sales Channel</b>",
            labels={"y": f"Revenue ({curr_symbol})", "Sales_Channel": "Channel"},
            template="plotly_white"
        )
        fig_chan.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
        st.plotly_chart(fig_chan, use_container_width=True)

    with col2_2:
        # Yearly / Quarterly Sales Growth
        yq_df = filtered_df.groupby(["Year", "Quarter"]).agg(
            Revenue=("Net_Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        yq_df["Period"] = yq_df["Year"].astype(str) + " " + yq_df["Quarter"]

        fig_yq = px.line(
            yq_df,
            x="Period",
            y=yq_df["Revenue"] * curr_rate,
            markers=True,
            title="<b>Quarterly Sales Growth Trajectory</b>",
            labels={"y": f"Revenue ({curr_symbol})", "Period": "Quarter"},
            template="plotly_white"
        )
        fig_yq.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_yq, use_container_width=True)

    # Daily Sales Volatility
    daily_sales = filtered_df.groupby("Order_Date")["Net_Sales"].sum().reset_index()
    fig_daily = px.line(
        daily_sales,
        x="Order_Date",
        y=daily_sales["Net_Sales"] * curr_rate,
        title="<b>Daily Sales Revenue Velocity</b>",
        labels={"y": f"Daily Sales ({curr_symbol})", "Order_Date": "Date"},
        template="plotly_white"
    )
    fig_daily.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_daily, use_container_width=True)


# =============================================================================
# PAGE 3: PRODUCT ANALYTICS
# =============================================================================
with tab3:
    st.subheader("3. Product & Brand Intelligence")

    col3_1, col3_2 = st.columns(2)
    with col3_1:
        # Subcategory Breakdown
        sub_df = filtered_df.groupby(["Category", "SubCategory"]).agg(
            Revenue=("Net_Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index().sort_values("Revenue", ascending=False)

        fig_sub = px.bar(
            sub_df,
            x="SubCategory",
            y=sub_df["Revenue"] * curr_rate,
            color="Category",
            title="<b>Revenue by Sub-Category</b>",
            labels={"y": f"Revenue ({curr_symbol})", "SubCategory": "Sub-Category"},
            template="plotly_white"
        )
        fig_sub.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_sub, use_container_width=True)

    with col3_2:
        # Brand Performance
        brand_df = filtered_df.groupby("Brand").agg(
            Revenue=("Net_Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index().sort_values("Revenue", ascending=False).head(10)

        fig_brand = px.bar(
            brand_df,
            x="Brand",
            y=brand_df["Revenue"] * curr_rate,
            title="<b>Top 10 Brands by Sales Revenue</b>",
            labels={"y": f"Revenue ({curr_symbol})", "Brand": "Brand"},
            color="Profit",
            color_continuous_scale="Teal",
            template="plotly_white"
        )
        fig_brand.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_brand, use_container_width=True)

    # Product Profitability Scatter Quadrant (Sales vs Profit Margin)
    st.markdown("#### 🎯 Product Profitability Matrix (Revenue vs. Margin %)")
    fig_scatter = px.scatter(
        prod_agg,
        x=prod_agg["Revenue"] * curr_rate,
        y="Margin_%",
        size="Units",
        color="Category",
        hover_name="Product_Name",
        labels={"x": f"Total Revenue ({curr_symbol})", "Margin_%": "Profit Margin (%)"},
        template="plotly_white"
    )
    # Add quadrant reference lines
    avg_rev = (prod_agg["Revenue"] * curr_rate).mean()
    avg_margin = prod_agg["Margin_%"].mean()
    fig_scatter.add_vline(x=avg_rev, line_dash="dot", line_color="#94A3B8")
    fig_scatter.add_hline(y=avg_margin, line_dash="dot", line_color="#94A3B8")
    fig_scatter.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)


# =============================================================================
# PAGE 4: CUSTOMER INTELLIGENCE
# =============================================================================
with tab4:
    st.subheader("4. Customer Analytics & RFM K-Means Segmentation")

    cust_perf = filtered_df.groupby("Customer_ID").agg(
        Name=("Customer_Name", "first"),
        Segment=("Customer_Segment", "first"),
        City=("City", "first"),
        Orders=("Order_ID", "nunique"),
        Spend=("Net_Sales", "sum")
    ).reset_index()

    cust_perf["Type"] = np.where(cust_perf["Orders"] > 1, "Returning Customer", "New Customer")

    col4_1, col4_2 = st.columns(2)
    with col4_1:
        type_summary = cust_perf.groupby("Type")["Spend"].sum().reset_index()
        fig_ctype = px.pie(
            type_summary,
            names="Type",
            values="Spend",
            title="<b>Revenue Contribution: New vs. Returning Customers</b>",
            hole=0.45,
            color_discrete_sequence=["#3B82F6", "#10B981"],
            template="plotly_white"
        )
        fig_ctype.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_ctype, use_container_width=True)

    with col4_2:
        fig_hist = px.histogram(
            cust_perf,
            x="Orders",
            nbins=12,
            title="<b>Customer Order Frequency Distribution</b>",
            labels={"Orders": "Order Count", "count": "Customers"},
            color_discrete_sequence=["#8B5CF6"],
            template="plotly_white"
        )
        fig_hist.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

    # RFM K-Means Persona Breakdown
    st.markdown("#### 👥 Machine Learning RFM Customer Clusters")
    if not df_rfm.empty:
        col_rfm_p, col_rfm_t = st.columns([1, 1])

        rfm_sum = df_rfm.groupby("Segment_Label").agg(
            Count=("Customer_ID", "count"),
            Spend=("Monetary", "sum"),
            Avg_Orders=("Frequency", "mean")
        ).reset_index()

        with col_rfm_p:
            fig_rpie = px.pie(
                rfm_sum,
                names="Segment_Label",
                values="Spend",
                title="<b>Revenue by Customer Persona</b>",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_white"
            )
            fig_rpie.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_rpie, use_container_width=True)

        with col_rfm_t:
            st.markdown("##### 🏆 Top 5 VIP Client Accounts")
            top_vip = cust_perf.sort_values("Spend", ascending=False).head(5)[
                ["Name", "Segment", "City", "Orders", "Spend"]
            ].copy()
            top_vip["Spend"] = top_vip["Spend"].apply(format_money)
            top_vip.columns = ["Customer Name", "Segment", "City", "Orders", "Total Spend"]
            st.dataframe(top_vip, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 5: REGIONAL ANALYTICS
# =============================================================================
with tab5:
    st.subheader("5. Regional & State Sales Dynamics")

    col5_1, col5_2 = st.columns(2)
    with col5_1:
        reg_stat = filtered_df.groupby("Region").agg(
            Sales=("Net_Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        reg_stat["Margin_%"] = (reg_stat["Profit"] / reg_stat["Sales"] * 100).round(1)

        fig_reg_b = px.bar(
            reg_stat,
            x="Region",
            y=reg_stat["Sales"] * curr_rate,
            color="Margin_%",
            title="<b>Regional Sales & Profit Margin</b>",
            labels={"y": f"Sales ({curr_symbol})", "Region": "Region"},
            color_continuous_scale="Viridis",
            template="plotly_white"
        )
        fig_reg_b.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_reg_b, use_container_width=True)

    with col5_2:
        state_df = filtered_df.groupby("State").agg(
            Sales=("Net_Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index().sort_values("Sales", ascending=False).head(10)

        fig_state = px.bar(
            state_df.sort_values("Sales", ascending=True),
            y="State",
            x=state_df.sort_values("Sales", ascending=True)["Sales"] * curr_rate,
            orientation="h",
            title="<b>Top 10 States by Sales Revenue</b>",
            labels={"x": f"Sales ({curr_symbol})", "State": "State"},
            color="Profit",
            color_continuous_scale="Blues",
            template="plotly_white"
        )
        fig_state.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_state, use_container_width=True)


# =============================================================================
# PAGE 6: SALES REPRESENTATIVE ANALYTICS
# =============================================================================
with tab6:
    st.subheader("6. Sales Representative Performance & Target Achievement")

    if "Sales_Representative" in filtered_df.columns:
        rep_df = filtered_df.groupby(["Sales_Representative", "Sales_Team", "Region"]).agg(
            Revenue=("Net_Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order_ID", "nunique")
        ).reset_index().sort_values("Revenue", ascending=False)

        # Baseline Targets
        target_map = {
            "Aarav Sharma": 45000000, "Pooja Mehta": 40000000, "Karan Singhal": 35000000,
            "Siddharth Rao": 55000000, "Divya Nambiar": 48000000, "Gautam Reddy": 42000000,
            "Rohan Deshmukh": 52000000, "Sneha Patel": 46000000, "Amit Shah": 38000000,
            "Debanjan Banerjee": 36000000, "Tanushree Das": 32000000, "Manoj Tiwari": 28000000
        }
        rep_df["Target"] = pd.to_numeric(
            rep_df["Sales_Representative"].map(lambda r: target_map.get(r, 40000000)),
            errors="coerce"
        ).fillna(40000000).astype(float)
        rep_df["Target"] = rep_df["Target"].replace(0, np.nan)
        rep_df["Attainment_%"] = (
            rep_df["Revenue"].astype(float).div(rep_df["Target"].replace(0, np.nan)).mul(100)
        ).round(1)

        fig_rep = px.bar(
            rep_df,
            x="Sales_Representative",
            y=rep_df["Revenue"] * curr_rate,
            color="Attainment_%",
            title="<b>Salesperson Revenue vs. Target Attainment %</b>",
            labels={"y": f"Revenue ({curr_symbol})", "Sales_Representative": "Sales Rep"},
            color_continuous_scale="Greens",
            template="plotly_white"
        )
        fig_rep.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_rep, use_container_width=True)

        st.markdown("#### 👔 Sales Rep Scorecard")
        rep_display = rep_df.copy()
        rep_display["Revenue"] = rep_display["Revenue"].apply(format_money)
        rep_display["Profit"] = rep_display["Profit"].apply(format_money)
        rep_display["Target"] = rep_display["Target"].apply(format_money)
        rep_display["Attainment_%"] = rep_display["Attainment_%"].map("{:.1f}%".format)
        rep_display.columns = ["Sales Representative", "Sales Team", "Region", "Revenue Generated", "Net Profit", "Closed Orders", "Annual Target", "Attainment %"]
        st.dataframe(rep_display, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 7: AI FORECASTING
# =============================================================================
with tab7:
    st.subheader("7. Machine Learning Sales Time-Series Forecasting")

    if not df_forecast.empty:
        hist_s = df_forecast[df_forecast["is_forecast"] == 0].sort_values("forecast_date").tail(180)
        fut_s = df_forecast[df_forecast["is_forecast"] == 1].sort_values("forecast_date")

        next30 = fut_s.head(30)["projected_sales"].sum()
        next60 = fut_s.head(60)["projected_sales"].sum()
        next90 = fut_s["projected_sales"].sum()

        fc_col1, fc_col2, fc_col3 = st.columns(3)
        with fc_col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📅 Next 30-Day Forecast</div>
                <div class="kpi-value">{format_money(next30)}</div>
                <div class="kpi-badge badge-blue">Expected 1-Month Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        with fc_col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📅 Next 60-Day Forecast</div>
                <div class="kpi-value">{format_money(next60)}</div>
                <div class="kpi-badge badge-green">Expected 2-Month Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        with fc_col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🔮 Next 90-Day Forecast</div>
                <div class="kpi-value">{format_money(next90)}</div>
                <div class="kpi-badge badge-purple">Quarterly ML Projection</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=fut_s["forecast_date"],
            y=fut_s["upper_confidence_bound"] * curr_rate,
            mode="lines",
            line=dict(width=0),
            showlegend=False
        ))
        fig_fc.add_trace(go.Scatter(
            x=fut_s["forecast_date"],
            y=fut_s["lower_confidence_bound"] * curr_rate,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(37, 99, 235, 0.15)",
            name="95% Confidence Interval"
        ))
        fig_fc.add_trace(go.Scatter(
            x=hist_s["forecast_date"],
            y=hist_s["actual_sales"] * curr_rate,
            mode="lines",
            line=dict(color="#64748B", width=2),
            name="Historical Daily Actuals"
        ))
        fig_fc.add_trace(go.Scatter(
            x=fut_s["forecast_date"],
            y=fut_s["projected_sales"] * curr_rate,
            mode="lines+markers",
            line=dict(color="#2563EB", width=2.5, dash="dash"),
            marker=dict(size=4),
            name="AI ML Projected Sales"
        ))
        fig_fc.update_layout(
            title="<b>Historical Daily Sales vs. 90-Day ML Projection</b>",
            xaxis_title="Date",
            yaxis_title=f"Sales ({curr_symbol})",
            template="plotly_white",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_fc, use_container_width=True)

        # Model Benchmark Table
        if not df_metrics.empty:
            st.markdown("#### 🤖 Machine Learning Model Benchmark Comparison")
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 8: BUSINESS INSIGHTS
# =============================================================================
with tab8:
    st.subheader("8. Automated Business Insights & Diagnostic Engine")
    st.caption("Algorithmically generated executive takeaways and risk alerts.")

    if not df_insights.empty:
        for _, row in df_insights.iterrows():
            severity_class = "insight-positive" if row["Severity"] == "Positive" else ("insight-warning" if row["Severity"] == "Warning" else "insight-alert")
            st.markdown(f"""
            <div class="insight-card {severity_class}">
                <div style="font-size:0.8rem; font-weight:700; color:#64748B; text-transform:uppercase;">[{row['Category']}]</div>
                <div style="font-size:1.05rem; font-weight:700; color:#0F172A; margin: 2px 0 6px 0;">{row['Title']}</div>
                <div style="font-size:0.92rem; color:#334155; line-height:1.5;">{row['Insight']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Run `python src/etl_pipeline.py` to generate automated business insights.")


# =============================================================================
# PAGE 9: ANOMALY DETECTION
# =============================================================================
with tab9:
    st.subheader("9. Machine Learning Anomaly Detection (Isolation Forest)")
    st.caption("Identifies multivariate pricing outliers, negative margin spikes, and excessive discounts.")

    if not df_anomalies.empty and "is_anomaly" in df_anomalies.columns:
        anomalies_only = df_anomalies[df_anomalies["is_anomaly"] == 1]
        
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🚨 Detected Anomalies</div>
                <div class="kpi-value">{len(anomalies_only):,}</div>
                <div class="kpi-badge badge-red">{(len(anomalies_only)/len(df_anomalies)*100):.1f}% of Dataset</div>
            </div>
            """, unsafe_allow_html=True)
        with a_col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🤖 Detection Algorithm</div>
                <div class="kpi-value" style="font-size:1.3rem;">Isolation Forest</div>
                <div class="kpi-badge badge-purple">Contamination: 3.0%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Anomaly Scatter Plot
        fig_anom = px.scatter(
            df_anomalies.sample(min(3000, len(df_anomalies))),
            x="Net_Sales",
            y="Profit_Margin_Pct",
            color="is_anomaly",
            color_discrete_map={0: "#94A3B8", 1: "#EF4444"},
            hover_data=["Order_ID", "Product_Name", "anomaly_reason"],
            title="<b>Transaction Anomaly Map (Sales vs. Profit Margin %)</b>",
            labels={"Net_Sales": f"Net Sales ({curr_symbol})", "Profit_Margin_Pct": "Profit Margin (%)", "is_anomaly": "Is Anomaly"},
            template="plotly_white"
        )
        fig_anom.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_anom, use_container_width=True)

        st.markdown("#### 🚨 Flagged Anomaly Transactions Table")
        anomaly_disp = anomalies_only[[
            "Order_ID", "Order_Date", "Customer_Name", "Product_Name",
            "Quantity", "Discount_Pct", "Net_Sales", "Profit", "Profit_Margin_Pct", "anomaly_reason"
        ]].head(100).copy()
        anomaly_disp["Net_Sales"] = anomaly_disp["Net_Sales"].apply(format_money)
        anomaly_disp["Profit"] = anomaly_disp["Profit"].apply(format_money)
        anomaly_disp["Discount_Pct"] = (anomaly_disp["Discount_Pct"] * 100).map("{:.1f}%".format)
        anomaly_disp["Profit_Margin_Pct"] = anomaly_disp["Profit_Margin_Pct"].map("{:.1f}%".format)
        st.dataframe(anomaly_disp, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 10: DATA EXPLORER & POWER BI EXPORT
# =============================================================================
with tab10:
    st.subheader("10. Data Explorer & Power BI Ready Marts")
    st.caption("Search, inspect, and export your filtered Star Schema datasets.")

    search_t = st.text_input("🔍 Quick Search (Customer, Product, City, or Order ID)", placeholder="Type to filter...")

    raw_disp = filtered_df[[
        "Order_ID", "Order_Date", "Customer_Name", "Customer_Segment",
        "Product_Name", "Category", "SubCategory", "Region", "City",
        "Quantity", "Unit_Price", "Discount_Pct", "Net_Sales", "Profit", "Payment_Method"
    ]].copy()

    if search_t:
        mask = (
            raw_disp["Order_ID"].astype(str).str.contains(search_t, case=False, na=False) |
            raw_disp["Customer_Name"].astype(str).str.contains(search_t, case=False, na=False) |
            raw_disp["Product_Name"].astype(str).str.contains(search_t, case=False, na=False) |
            raw_disp["City"].astype(str).str.contains(search_t, case=False, na=False)
        )
        raw_disp = raw_disp[mask]

    st.write(f"Showing **{len(raw_disp):,}** matching transaction records:")
    st.dataframe(raw_disp.head(250), use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        csv_exp = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Transactions to CSV",
            data=csv_exp,
            file_name=f"sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    with c2:
        st.info("💡 **Power BI Connection**: All processed datasets are saved in `data/exports/` and the SQLite database `database/sales_analytics.db` is ready for instant Power BI import.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("📊 Sales Dashboard Using Python and Power BI • Data Analytics • SQLite • Power BI • Machine Learning")
