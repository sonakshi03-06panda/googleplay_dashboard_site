# 📱 Google Play Store Dashboard

A fully interactive, real-time dashboard built with **Streamlit** for exploring and visualizing Google Play Store data. 
This project helps uncover trends across app categories, revenue models, global install patterns, and multilingual user bases — making app market insights more accessible and intuitive.

## 📊 Features

- **Scatter Plot**: Visualizes revenue vs installs for paid apps, color-coded by category with trendlines.
- **Choropleth Map**: Displays top 5 app categories (excluding A, C, G, S) by global installs (>1M). *Visible only between 6–8 PM IST.*
- **Time Series Chart**: Shows install trends by category with multilingual axis labels. *Visible only from 6–9 PM IST.*
- **Dynamic Filters**: Category and install count filters for tailored insights.
- **Responsive Layout**: Optimized for wide screens using `wide` layout in Streamlit.

## 📚 Tech Stack

- Frontend/UI: Streamlit
- Data Handling: Pandas, Numpy
- Visualization: Seaborn, Plotly Express, Matplotlib
- Time/Geo Filtering: datetime, pytz, and Plotly map

## 🎯 Use Cases
- Identify top-performing app categories
- Explore revenue vs install trends
- Study time-based and region-based download patterns
- Analyze user preferences across different time zones
