import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from datetime import datetime
import pytz
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# -------------------- App Configuration --------------------
st.set_page_config(layout="wide")
st.title("📱 Google Play Store Dashboard")

# -------------------- Load Dataset --------------------
try:
    df = pd.read_csv("google_playstore.csv")
except FileNotFoundError:
    st.error("❌ 'google_playstore.csv' not found.")
    st.stop()

# -------------------- Preprocess & Clean Data --------------------
df.columns = df.columns.str.strip()
required_cols = ['App', 'Category', 'Last Updated', 'Installs', 'Price', 'Reviews']
if missing := [col for col in required_cols if col not in df.columns]:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

df = df.dropna(subset=required_cols)
df['Installs'] = df['Installs'].str.replace('[+,]', '', regex=True)
df['Price'] = df['Price'].str.replace('$', '', regex=False)
df['Reviews'] = df['Reviews'].str.replace('[+,]', '', regex=True)

for col in ['Installs', 'Price', 'Reviews']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Final clean and feature creation
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df = df.dropna(subset=['Installs', 'Price', 'Last Updated'])
df['Revenue'] = df['Installs'] * df['Price']
ist_now = datetime.now(pytz.timezone("Asia/Kolkata")).time()


# -------------------- Chart 1: Revenue vs Installs --------------------
st.subheader("💰 Revenue vs Installs (Paid Apps Only) with Trendline")
paid = df[df['Price'] > 0]
st.write("✅ Total apps:", len(df))
st.write("💰 Paid apps:", len(paid))

if not paid.empty:
    reg = LinearRegression().fit(paid[['Installs']], paid['Revenue'])
    paid['Trendline'] = reg.predict(paid[['Installs']])

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.scatterplot(data=paid, x='Installs', y='Revenue', hue='Category', palette='tab20', alpha=0.7, ax=ax)
    ax.plot(paid['Installs'], paid['Trendline'], color='black', linewidth=2, label='Trendline')
    ax.set(title='Revenue vs Installs for Paid Apps', xlabel='Number of Installs', ylabel='Estimated Revenue (USD)')
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("⚠️ No paid apps available.")


# -------------------- Chart 2: Choropleth Map (6–8 PM IST) --------------------
if datetime.strptime("18:00", "%H:%M").time() <= ist_now <= datetime.strptime("20:00", "%H:%M").time():
    st.subheader("🗺️ Global Installs by Category (6–8 PM IST)")
    filtered = df[(~df['Category'].str.startswith(tuple("ACGS"))) & (df['Installs'] > 1_000_000)]
    top5 = filtered['Category'].value_counts().nlargest(5).index
    chorodata = filtered[filtered['Category'].isin(top5)].copy()
    chorodata['Country'] = np.random.choice(['USA', 'IND', 'GBR', 'CAN', 'AUS'], size=len(chorodata))

    selected_category = st.radio("Select Category to View:", top5)
    selected_data = chorodata[chorodata['Category'] == selected_category]
    agg_data = selected_data.groupby('Country')['Installs'].sum().reset_index()

    fig2 = px.choropleth(
        agg_data, locations='Country', locationmode='ISO-3', color='Installs',
        hover_name='Country', title=f'Choropleth Map for {selected_category} Apps', color_continuous_scale='Plasma'
    )
    fig2.update_layout(height=600)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("🌐 Choropleth map is available only between 6 PM and 8 PM IST.")


# -------------------- Chart 3: Time-Series (6–9 PM IST) --------------------
if datetime.strptime("18:00", "%H:%M").time() <= ist_now <= datetime.strptime("21:00", "%H:%M").time():
    st.subheader("📈 Time-Series of Installs by Category (6–9 PM IST)")
    df_filtered = df[
        (~df['App'].str.lower().str.startswith(tuple('xyz')))
        & (~df['App'].str.contains('S', case=False))
        & (df['Reviews'] > 500)
        & (df['Category'].str.startswith(tuple("ECB"))) ].copy()

    translate = {'Beauty': 'सौंदर्य', 'Business': 'வணிகம்', 'Dating': 'Partnersuche'}
    df_filtered['Category'] = df_filtered['Category'].replace(translate)
    df_filtered['Month'] = df_filtered['Last Updated'].dt.to_period('M').dt.to_timestamp()
    grouped = df_filtered.groupby(['Month', 'Category'])['Installs'].sum().unstack().fillna(0).sort_index()

    fig3 = px.line(grouped, title='Time-Series Trend of Installs by Category')
    fig3.update_layout(height=600)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("📆 Time-Series chart is available only between 6 PM and 9 PM IST.")