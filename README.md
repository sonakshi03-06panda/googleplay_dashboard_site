# 📱 Google Play Store Dashboard

A fully interactive, real-time dashboard built with **Streamlit** to explore and visualize Google Play Store data.  
This project reveals trends across app categories, revenue generation, global install patterns, and multilingual insights — making market intelligence accessible for everyone.

🚀 **Live Demo**:  
[▶️ Click here to open the dashboard](https://appplaydashboardsite-loqff8eeaec5i7ba5lnuhk.streamlit.app/)

---

## 📊 Features

- **💰 Revenue vs Installs**  
  Scatter plot for paid apps showing revenue vs installs, color-coded by category. Includes an OLS trendline to visualize overall performance.

- **🌍 Choropleth Map**  
  Visualizes global installs by country for the **top 5 app categories** (with more than 1M installs), excluding those starting with **A, C, G, or S**.  
  _🕒 Available only between **6 PM and 8 PM IST**._

- **📈 Time Series Chart**  
  Displays install trends over time, segmented by **categories starting with B, C, or E**.  
  Filters out apps that:
  - Have less than 500 reviews
  - Start with **X, Y, or Z**
  - Contain the letter **"S"**  
  Highlights **>20% month-over-month growth** with shaded areas under the curve.  
  Includes translated category labels:
  - `"Beauty"` → `"सौंदर्य"` (Hindi)  
  - `"Business"` → `"வணிகம்"` (Tamil)  
  - `"Dating"` → `"Partnersuche"` (German)  
  _🕒 Available only between **6 PM and 9 PM IST**._

- **⚙️ Dynamic Filtering & Translation**  
  Translates select categories and enables intelligent filtering based on installs, ratings, reviews, app name, and time.

- **🖥️ Responsive Layout**  
  Optimized for wider screens using Streamlit's `"wide"` page configuration.

---

## 📚 Tech Stack

- **Frontend/UI**: Streamlit, Netlify
- **Data Handling**: Pandas, NumPy
- **Visualization**: Plotly Express, Seaborn (backup), Matplotlib (fallback)
- **Time/Geo Filtering**: `datetime`, `pytz`, and Plotly's Choropleth map

## 🎯 Use Cases

- Identify high-growth app categories and regions
- Analyze install patterns across time, category, and geography
- Explore the relationship between installs, revenue, and ratings
- Support data-driven decisions for app development, marketing, or investment
