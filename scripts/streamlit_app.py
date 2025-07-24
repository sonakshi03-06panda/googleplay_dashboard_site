import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import requests

# ------------------ Page Config ------------------
st.set_page_config(page_title="Google Play Dashboard", page_icon="📱", layout="wide")

# ------------------ Load and Clean Data ------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("google_playstore.csv")

        # Clean and convert columns
        df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")
        df["Price"] = (
            df["Price"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace("Free", "0", regex=False)
            .str.strip()
            .astype(float)
        )
        df["Installs"] = (
            df["Installs"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("+", "", regex=False)
            .str.strip()
            .astype(float)
        )
        df["Revenue"] = df["Price"] * df["Installs"]

        return df

    except Exception as e:
        st.error(f"❌ Failed to load dataset: {e}")
        return pd.DataFrame()

df = load_data()
paid_apps = df[df["Price"] > 0]

# ------------------ Navigation ------------------
st.sidebar.title("📊 Dashboard Menu")
section = st.sidebar.radio("Go to", [
    "🏠 Home",
    "📈 Revenue vs Installs",
    "🌍 Choropleth Map",
    "📆 Time Series Chart",
    "📬 About & Contact"
])
st.sidebar.markdown("---")

# ------------------ 🏠 Home ------------------
if section == "🏠 Home":
    st.title("📱 Google Play Store Dashboard")

    if df.empty:
        st.warning("Dataset is empty or failed to load.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Apps", f"{len(df):,}")
        col2.metric("Paid Apps", f"{len(paid_apps):,}")
        col3.metric("Categories", df["Category"].nunique())

        with st.expander("ℹ️ About the Dataset"):
            st.write("""
                This dashboard visualizes insights from Google Play Store data:
                - Revenue vs Installs
                - Global Install Distribution
                - Install Trends Over Time
            """)

# ------------------ 📈 Revenue vs Installs ------------------
elif section == "📈 Revenue vs Installs":
    st.header("💰 Revenue vs Installs (Paid Apps Only)")

    if paid_apps.empty:
        st.warning("No paid apps available in dataset.")
    else:
        model = LinearRegression().fit(paid_apps[["Installs"]], paid_apps["Revenue"])
        paid_apps["Trendline"] = model.predict(paid_apps[["Installs"]])

        fig = px.scatter(
            paid_apps,
            x="Installs",
            y="Revenue",
            color="Category",
            trendline="ols",
            title="Revenue vs Installs"
        )
        fig.update_layout(legend=dict(x=1.02, y=1))
        st.plotly_chart(fig, use_container_width=True)

# ------------------ 🌍 Choropleth Map ------------------
elif section == "🌍 Choropleth Map":
    st.header("🌍 Global Installs by Country (Top Categories)")

    if "Country" not in df.columns:
        st.error("❌ Dataset must include a 'Country' column for this map.")
    else:
        filtered = df[~df["Category"].str.startswith(("A", "C", "G", "S"))]
        top5 = filtered.groupby("Category")["Installs"].sum().nlargest(5).index.tolist()
        filtered_df = df[df["Category"].isin(top5) & (df["Installs"] > 1_000_000)]

        map_df = filtered_df.groupby("Country")["Installs"].sum().reset_index()

        fig = px.choropleth(
            map_df,
            locations="Country",
            locationmode="country names",
            color="Installs",
            hover_name="Country",
            color_continuous_scale="Plasma",
            title="Total Installs by Country (Top Categories)"
        )
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)

# ------------------ 📆 Time Series Chart ------------------
elif section == "📆 Time Series Chart":
    st.header("📈 Install Trends Over Time by Category")

    time_df = df.dropna(subset=["Last Updated", "Installs", "Category"])
    categories = sorted(time_df["Category"].unique())
    selected = st.multiselect("Select Categories", categories, default=categories[:5])

    filtered_df = time_df[time_df["Category"].isin(selected)]

    monthly_installs = (
        filtered_df.groupby([pd.Grouper(key="Last Updated", freq="M"), "Category"])
        .agg({"Installs": "sum"})
        .reset_index()
    )

    fig = px.line(
        monthly_installs,
        x="Last Updated",
        y="Installs",
        color="Category",
        title="Install Trends by Category Over Time"
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Installs", legend_title="Category")
    st.plotly_chart(fig, use_container_width=True)

# ------------------ 📬 About & Contact ------------------
elif section == "📬 About & Contact":
    st.header("📬 About this Project")
    st.write("""
    This interactive dashboard was created using Streamlit to explore Google Play Store app trends.
    It covers installs, paid app revenue, country-wise distributions, and time-series trends.
    """)

    st.subheader("👩‍💻 Developer")
    st.markdown("**Sonakshi Panda**")
    st.markdown("🔗 [GitHub](https://github.com/sonakshi03-06panda)")

    with st.form("contact_form"):
        st.write("📨 Send a Message")
        name = st.text_input("Your Name")
        message = st.text_area("Your Message")
        submitted = st.form_submit_button("Send")
        if submitted:
            st.success("✅ Message sent. Thanks for reaching out!")

