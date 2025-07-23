import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime
import pytz

# -------------------- App Configuration --------------------
st.set_page_config(layout="wide")
st.title("📱 Google Play Store Dashboard")

# -------------------- Load Dataset --------------------
CSV_FILE = "google_playstore.csv"

@st.cache_data
def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        return None

df = load_data(CSV_FILE)
if df is None:
    st.error(f"❌ '{CSV_FILE}' not found.")
    st.stop()

# -------------------- Preprocess Data --------------------
df.columns = df.columns.str.strip()
required_cols = ['App', 'Category', 'Last Updated', 'Installs', 'Price', 'Reviews']
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# Clean data
df.dropna(subset=required_cols, inplace=True)
df['Installs'] = df['Installs'].str.replace(r'[+,]', '', regex=True).astype(float)
df['Price'] = df['Price'].str.replace('$', '', regex=False).astype(float)
df['Reviews'] = df['Reviews'].str.replace(r'[+,]', '', regex=True).astype(float)
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')

# Drop rows with NaN after conversion
df.dropna(subset=['Installs', 'Price', 'Last Updated'], inplace=True)

# Feature engineering
df['Revenue'] = df['Installs'] * df['Price']
ist_now = datetime.now(pytz.timezone("Asia/Kolkata")).time()


# -------------------- Chart 1: Revenue vs Installs --------------------
st.subheader("💰 Revenue vs Installs (Paid Apps Only) with Trendline")
paid_apps = df[df['Price'] > 0]

st.write("✅ Total apps:", len(df))
st.write("💰 Paid apps:", len(paid_apps))

if not paid_apps.empty:
    X = paid_apps[['Installs']]
    y = paid_apps['Revenue']
    model = LinearRegression().fit(X, y)
    paid_apps['Trendline'] = model.predict(X)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.scatterplot(data=paid_apps, x='Installs', y='Revenue', hue='Category', palette='tab20', alpha=0.7, ax=ax)
    ax.plot(paid_apps['Installs'], paid_apps['Trendline'], color='black', linewidth=2, label='Trendline')
    ax.set(title='Revenue vs Installs for Paid Apps', xlabel='Number of Installs', ylabel='Estimated Revenue (USD)')
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("⚠️ No paid apps available.")


# -------------------- Chart 2: Choropleth Map (6–8 PM IST) --------------------
if datetime.strptime("18:00", "%H:%M").time() <= ist_now <= datetime.strptime("20:00", "%H:%M").time():
    st.subheader("🗺️ Global Installs by Category (6–8 PM IST)")

    chorofilter = df[
        ~df['Category'].str.startswith(tuple("ACGS")) & (df['Installs'] > 1_000_000)
    ]
    top5_categories = chorofilter['Category'].value_counts().nlargest(5).index
    chorodata = chorofilter[chorofilter['Category'].isin(top5_categories)].copy()
    chorodata['Country'] = np.random.choice(['USA', 'IND', 'GBR', 'CAN', 'AUS'], size=len(chorodata))

    selected_category = st.radio("Select Category to View:", top5_categories)
    agg_data = (
        chorodata[chorodata['Category'] == selected_category]
        .groupby('Country', as_index=False)['Installs']
        .sum()
    )

    fig2 = px.choropleth(
        agg_data, locations='Country', locationmode='ISO-3', color='Installs',
        hover_name='Country', title=f'Choropleth Map for {selected_category} Apps',
        color_continuous_scale='Plasma', height=600
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("🌐 Choropleth map is available only between 6 PM and 8 PM IST.")


# -------------------- Chart 3: Time-Series (6–9 PM IST) --------------------
if datetime.strptime("18:00", "%H:%M").time() <= ist_now <= datetime.strptime("21:00", "%H:%M").time():
    st.subheader("📈 Time-Series of Installs by Category (6–9 PM IST)")

    mask = (
        ~df['App'].str.lower().str.startswith(tuple('xyz')) &
        ~df['App'].str.contains('S', case=False) &
        (df['Reviews'] > 500) &
        df['Category'].str.startswith(tuple("ECB"))
    )
    timeseries_df = df[mask].copy()
    timeseries_df['Category'] = timeseries_df['Category'].replace({
        'Beauty': 'सौंदर्य', 'Business': 'வணிகம்', 'Dating': 'Partnersuche'
    })
    timeseries_df['Month'] = timeseries_df['Last Updated'].dt.to_period('M').dt.to_timestamp()

    grouped = timeseries_df.groupby(['Month', 'Category'])['Installs'].sum().unstack(fill_value=0)

    fig3 = px.line(grouped, title='Time-Series Trend of Installs by Category', height=600)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("📆 Time-Series chart is available only between 6 PM and 9 PM IST.")