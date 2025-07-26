import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime
import pytz
import os
import statsmodels.api as sm  

# ------------------ Page Config ------------------
st.set_page_config(page_title="Google Play Dashboard", page_icon="📱", layout="wide")

# ------------------ Utility: IST Time Checker ------------------
def is_ist_time_between(start_hour, end_hour):
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    return now, start_hour <= now.hour < end_hour

# ------------------ Display IST Time ------------------
now_ist, _ = is_ist_time_between(0, 24)
st.markdown(f"<div style='text-align:right; font-size:14px;'>🕒 Current IST Time: <b>{now_ist.strftime('%I:%M %p')}</b></div>", unsafe_allow_html=True)

# ------------------ Load and Clean Data ------------------
@st.cache_data
def load_data():
    if not os.path.exists("google_playstore.csv"):
        st.error("❌ File 'google_playstore.csv' not found.")
        return pd.DataFrame()

    try:
        df = pd.read_csv("google_playstore.csv")

        df["Last Updated"] = pd.to_datetime(df["Last Updated"], errors="coerce")

        df["Price"] = (
            df["Price"].astype(str)
            .str.replace("$", "", regex=False)
            .str.replace("Free", "0", regex=False)
            .str.strip()
        )
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0.0)

        df["Installs"] = (
            df["Installs"].astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("+", "", regex=False)
            .str.strip()
        )
        df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce").fillna(0.0)

        df["Revenue"] = df["Price"] * df["Installs"]

        return df

    except Exception as e:
        st.error(f"❌ Failed to load dataset: {e}")
        return pd.DataFrame()

df = load_data()
paid_apps = df[df["Price"] > 0] if not df.empty else pd.DataFrame()

# ------------------ Navigation ------------------
st.sidebar.title("Dashboard Menu")
section = st.sidebar.radio("Go to", [
    "🏠 Home",
    "📈 Revenue vs Installs",
    "🌍 Choropleth Map",
    "📆 Time Series Chart",
    "📬 Contact"
])
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")

# ------------------ 🏠 Home ------------------
if section == "🏠 Home":
    st.title("📱 Google Play Store Dashboard")

    st.subheader("ℹ️ About the Project")
    st.write("""
        This interactive data visualization dashboard was built using Python and Streamlit to analyze trends from the Google Play Store dataset.
        
        The goal of this project is to help users and stakeholders explore mobile app market trends, identify category-wise popularity, analyze revenue from paid apps, and understand global distribution patterns.

        **Key Features:**
        - 📊 **Revenue vs Installs Analysis** for Paid Apps: Understand how paid apps perform in terms of installs and revenue generation.
        - 🌍 **Country-wise Install Distribution**: Visualize how different app categories are installed across countries using a global map (active during specific hours).
        - 📈 **Time Series Trends**: Explore how app installs have changed over time across categories with interactive filters and multi-language support.
        - 🔎 **Dynamic Filters**: Users can filter by app category, install thresholds, and more to customize the insights they see.
        - 🧠 **Trendline Insights**: Automatically-generated trendlines offer additional business intelligence at a glance.

        The dashboard is designed to be visually intuitive, informative, and responsive for both technical and non-technical users.

        > All charts are interactive, and the application runs entirely on the web—no local setup needed. It is ideal for business analysts, app developers, or anyone exploring app store performance metrics.
    """)

# ------------------ 📈 Revenue vs Installs ------------------
elif section == "📈 Revenue vs Installs":
    st.header("💰 Revenue vs Installs (Paid Apps Only)")

     if df.empty:
        st.warning("Dataset is empty or failed to load.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Apps", f"{len(df):,}")
        col2.metric("Paid Apps", f"{len(paid_apps):,}")
        col3.metric("Categories", df["Category"].nunique())

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
            title="Revenue vs Installs (Paid Apps)"
        )
        fig.update_layout(legend=dict(x=1.02, y=1))
        st.plotly_chart(fig, use_container_width=True)

# ------------------ 🌍 Choropleth Map (6–8 PM IST) ------------------
elif section == "🌍 Choropleth Map":
    now_ist, show_map = is_ist_time_between(18, 20)

    if show_map:
        st.header("🌍 Global Installs by Country (Filtered Categories)")

        if "Country" not in df.columns:
            st.warning("Dataset must include a 'Country' column.")
        else:
            filtered = df[
                ~df["Category"].str.startswith(("A", "C", "G", "S")) &
                (df["Installs"] > 1_000_000)
            ]
            top_categories = filtered.groupby("Category")["Installs"].sum().nlargest(5).index.tolist()
            filtered_df = filtered[filtered["Category"].isin(top_categories)]

            map_df = filtered_df.groupby(["Country", "Category"])["Installs"].sum().reset_index()

            fig = px.choropleth(
                map_df,
                locations="Country",
                locationmode="country names",
                color="Installs",
                hover_name="Category",
                animation_frame="Category",
                color_continuous_scale="Turbo",
                title="Top 5 Categories (Installs > 1M) by Country"
            )
            fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⏳ Choropleth Map is visible only between 6 PM and 8 PM IST.")

# ------------------ 📆 Time Series Chart (6–9 PM IST) ------------------
elif section == "📆 Time Series Chart":
    now_ist, show_chart = is_ist_time_between(18, 21)

    if show_chart:
        st.header("📈 Install Trends Over Time by Category (Filtered)")

        required_columns = {"App", "Category", "Reviews", "Rating", "Last Updated", "Installs"}
        if not required_columns.issubset(df.columns):
            st.warning(f"Dataset must include the following columns: {', '.join(required_columns)}.")
        else:
            # Convert Reviews and Rating to numeric if needed
            df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce")
            df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")

            # Drop rows with missing values in critical columns
            df_cleaned = df.dropna(subset=["Reviews", "Rating", "App", "Category", "Last Updated", "Installs"]).copy()

            # Apply filters safely
            filtered_df = df_cleaned[
                (df_cleaned["Reviews"] > 500) &
                (df_cleaned["Rating"] > 4.0) &
                (~df_cleaned["App"].str.contains("s", case=False, regex=True))].copy()

            # Translate selected categories
            translations = {
                "Beauty": "सौंदर्य",       # Hindi
                "Business": "வணிகம்",     # Tamil
                "Dating": "Partnersuche"  # German
            }
            filtered_df["Category"] = filtered_df["Category"].replace(translations)

            # Parse 'Last Updated' to datetime
            filtered_df["Last Updated"] = pd.to_datetime(filtered_df["Last Updated"], errors="coerce")

            # Group by month and category
            monthly = (
                filtered_df.dropna(subset=["Last Updated"])
                .groupby([pd.Grouper(key="Last Updated", freq="M"), "Category"])
                .agg({"Installs": "sum"})
                .reset_index()
            )

            # Calculate growth rate
            monthly["Previous"] = monthly.groupby("Category")["Installs"].shift(1)
            monthly["Growth"] = ((monthly["Installs"] - monthly["Previous"]) / monthly["Previous"]) * 100

            # Plot line chart
            fig = px.line(
                monthly,
                x="Last Updated",
                y="Installs",
                color="Category",
                title="Install Trends by Category (Filtered & Translated)"
            )

            # Highlight strong growth areas
            highlight_df = monthly[monthly["Growth"] > 20]
            for cat in highlight_df["Category"].unique():
                df_area = highlight_df[highlight_df["Category"] == cat]
                fig.add_scatter(
                    x=df_area["Last Updated"],
                    y=df_area["Installs"],
                    mode='lines',
                    name=f"{cat} Growth > 20%",
                    line=dict(width=0),
                    fill='tozeroy',
                    fillcolor='rgba(255,0,0,0.2)'
                )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⏳ Time Series Chart is visible only between 6 PM and 9 PM IST.")

# ------------------ 📬 About & Contact ------------------
elif section == "📬 Contact":
    
    st.subheader("👩‍💻 Developer")
    st.markdown("**Sonakshi Panda**")
    st.markdown("🔗 [GitHub](https://github.com/sonakshi03-06panda)")
    st.markdown("✉️ [sonakshi0306panda@outlook.com](mailto:sonakshi0306panda@outlook.com)")

    st.info("For any queries or support related to this dashboard, please reach out to the developer via the email above.")