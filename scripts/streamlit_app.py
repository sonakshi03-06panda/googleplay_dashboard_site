import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime
import pytz

# -------------------- App Configuration --------------------
st.set_page_config(layout="wide")
st.title("📱 Google Play Store Dashboard")

# -------------------- Load & Preprocess Dataset --------------------
CSV_FILE = "google_playstore.csv"

@st.cache_data
def load_and_clean_data(filepath):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        return None

    df.columns = df.columns.str.strip()
    required_cols = ['App', 'Category', 'Last Updated', 'Installs', 'Price', 'Reviews']
    if not all(col in df.columns for col in required_cols):
        return None

    df.dropna(subset=required_cols, inplace=True)

    # Clean and convert
    df['Installs'] = (
        df['Installs']
        .astype(str)
        .str.replace(r'[+,]', '', regex=True)
        .str.strip()
        .replace('Free', np.nan)
    )
    df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

    df['Price'] = (
        df['Price']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.strip()
        .replace('Free', '0')
    )
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

    df['Reviews'] = (
        df['Reviews']
        .astype(str)
        .str.replace(r'[+,]', '', regex=True)
        .str.strip()
    )
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')

    # Drop rows with any failed conversions
    df.dropna(subset=['Installs', 'Price', 'Last Updated', 'Reviews'], inplace=True)

    # Add Revenue
    df['Revenue'] = df['Installs'] * df['Price']

    return df

df = load_and_clean_data(CSV_FILE)

if df is None:
    st.error(f"❌ '{CSV_FILE}' not found or missing required columns.")
    st.stop()

ist_now = datetime.now(pytz.timezone("Asia/Kolkata")).time()

def within_time(start, end):
    return start <= ist_now <= end

# -------------------- Chart 1: Revenue vs Installs --------------------
st.subheader("💰 Revenue vs Installs (Paid Apps Only) with Trendline")

paid_apps = df[df['Price'] > 0]

st.write("✅ Total apps:", len(df))
st.write("💰 Paid apps:", len(paid_apps))

if not paid_apps.empty:
    model = LinearRegression().fit(paid_apps[['Installs']], paid_apps['Revenue'])
    paid_apps = paid_apps.assign(Trendline=model.predict(paid_apps[['Installs']]))

    fig1 = px.scatter(
        paid_apps, x="Installs", y="Revenue", color="Category",
        hover_data=["App", "Price", "Reviews"],
        title="Revenue vs Installs for Paid Apps",
        opacity=0.7,
        color_discrete_sequence=px.colors.qualitative.Set3,
        height=600
    )

    fig1.add_trace(go.Scatter(
            x=paid_apps["Installs"], y=paid_apps["Trendline"],
            mode="lines", name="Trendline",
            line=dict(color="black", width=2))
    )

    fig1.update_layout(
        plot_bgcolor='white',
        legend=dict(title="Category", x=1.02, y=1, xanchor='left', yanchor='top'),
        margin=dict(r=180)
    )

    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("⚠️ No paid apps available.")

# -------------------- Chart 2: Choropleth Map (6–8 PM IST) --------------------
if within_time(datetime.strptime("18:00", "%H:%M").time(), datetime.strptime("20:00", "%H:%M").time()):
    st.subheader("🗺️ Global Installs by Category (6–8 PM IST)")

    chorodata = df[
    ~df['Category'].astype(str).str.startswith(('A', 'C', 'G', 'S')) &
    (df['Installs'] > 1_000_000)].copy()

    top5_categories = chorodata['Category'].value_counts().nlargest(5).index
    chorodata = chorodata[chorodata['Category'].isin(top5_categories)].copy()
    chorodata['Country'] = np.random.choice(['USA', 'IND', 'GBR', 'CAN', 'AUS'], size=len(chorodata))

    selected_category = st.radio("Select Category to View:", top5_categories)
    agg_data = (
        chorodata[chorodata['Category'] == selected_category]
        .groupby('Country', as_index=False)['Installs'].sum()
    )

    fig2 = px.choropleth(
        agg_data, locations='Country', locationmode='ISO-3', color='Installs',
        hover_name='Country', title=f'Choropleth Map for {selected_category} Apps',
        color_continuous_scale='Plasma', height=600
    )
    fig2.update_layout(margin=dict(r=50, l=50, t=50, b=50))
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("🌐 Choropleth map is available only between 6 PM and 8 PM IST.")

# -------------------- Chart 3: Time-Series (6–9 PM IST) --------------------
if within_time(datetime.strptime("18:00", "%H:%M").time(), datetime.strptime("21:00", "%H:%M").time()):
    st.subheader("📈 Time-Series of Installs by Category (6–9 PM IST)")

    ts_df = df[
    ~df['App'].astype(str).str.lower().str.startswith(tuple('xyz')) &
    ~df['App'].astype(str).str.contains('S', case=False, na=False) &
    (df['Reviews'] > 500) &
    df['Category'].astype(str).str.startswith(tuple('ECB'))].copy()

    ts_df['Category'] = ts_df['Category'].replace({
        'Beauty': 'सौंदर्य', 
        'Business': 'வணிகம்', 
        'Dating': 'Partnersuche'})
    ts_df['Month'] = ts_df['Last Updated'].dt.to_period('M').dt.to_timestamp()

    grouped_ts = ts_df.groupby(['Month', 'Category'])['Installs'].sum().reset_index()

    fig3 = px.line(
        grouped_ts, x='Month', y='Installs', color='Category',
        title='Time-Series Trend of Installs by Category',
        markers=True,
        color_discrete_sequence=px.colors.qualitative.D3,
        height=600
    )

    fig3.update_layout(
        legend=dict(x=1.02, y=1, xanchor='left'),
        margin=dict(r=160)
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("📆 Time-Series chart is available only between 6 PM and 9 PM IST.")
