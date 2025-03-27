import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Set Streamlit Page Config (Must be the first Streamlit command)
st.set_page_config(page_title="Vancouver Airbnb Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("listings.csv")
    # Select columns that exist in your data
    df = df[['id', 'name', 'neighbourhood', 'room_type', 'price', 'latitude', 
             'longitude', 'number_of_reviews', 'availability_365', 
             'last_review', 'reviews_per_month']]
    df = df.dropna()
    df['price'] = df['price'].replace({'\\$': '', ',': ''}, regex=True).astype(float)
    
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])
    
    return df

df = load_data()
  
# Streamlit Theme
st.markdown("""
    <style>
        .css-1d391kg {background-color: #f5f5f5;}
        .stApp {background-color: #f8f9fa;}
        .sidebar .sidebar-content {
            background-color: #ff7f50;
        }
        .stButton>button {
            background-color: #ff7f50;
            color: white;
        }
        h1, h2 {
            color: #2e3d49;
        }
        .st-bc {
            background-color: #ff7f50;
        }
        .sidebar .st-expander {
            border: none;
            box-shadow: none;
        }
        .sidebar .st-expander .st-expanderHeader {
            font-weight: bold;
            padding: 0.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar with Search and Navigation
st.sidebar.header("🏠 Dashboard Overview")
home_button = st.sidebar.button("Go to Home Page")

# Sidebar Search Filters with expandable sections
st.sidebar.header("🔍 Search & Filter")

# Neighborhood filter with expander
with st.sidebar.expander("📍 Choose a Neighborhood", expanded=False):
    neighborhoods = st.multiselect(
        "Select neighborhoods", 
        df['neighbourhood'].unique(), 
        default=df['neighbourhood'].unique(),
        label_visibility="collapsed"
    )

# Room type filter with expander
with st.sidebar.expander("🏠 Choose Room Type", expanded=False):
    room_types = st.multiselect(
        "Select room types", 
        df['room_type'].unique(), 
        default=df['room_type'].unique(),
        label_visibility="collapsed"
    )

# Price range filter with expander
with st.sidebar.expander("💰 Price Range", expanded=False):
    price_range = st.slider(
        "Select Price Range ($)", 
        int(df['price'].min()), 
        int(df['price'].max()), 
        (50, 300),
        label_visibility="collapsed"
    )

# Availability filter with expander
with st.sidebar.expander("📅 Availability", expanded=False):
    availability = st.slider(
        "Availability (days per year)", 
        int(df['availability_365'].min()), 
        int(df['availability_365'].max()), 
        (0, 365),
        label_visibility="collapsed"
    )

# Reviews per month filter with expander
with st.sidebar.expander("⭐ Reviews Activity", expanded=False):
    reviews_per_month_range = st.slider(
        "Reviews per Month", 
        float(df['reviews_per_month'].min()), 
        float(df['reviews_per_month'].max()), 
        (0.0, float(df['reviews_per_month'].max())),
        label_visibility="collapsed"
    )

# Apply filters
df_filtered = df[
    (df['neighbourhood'].isin(neighborhoods)) & 
    (df['price'].between(price_range[0], price_range[1])) & 
    (df['room_type'].isin(room_types)) & 
    (df['availability_365'].between(availability[0], availability[1])) & 
    (df['reviews_per_month'].between(reviews_per_month_range[0], reviews_per_month_range[1]))
]

# Main content layout
st.title("🏡 Vancouver Airbnb Data Dashboard")

st.markdown("""
    Welcome to the Vancouver Airbnb Data Dashboard! This interactive tool provides an in-depth analysis of Airbnb listings in Vancouver, helping users explore pricing trends, availability, and room types across different neighborhoods.

    With this dashboard, you can:
    - Filter listings based on **neighborhood, price range, room type, availability**, and **review activity**.
    - View **interactive charts and maps** to understand trends better.
    - Identify **the most affordable** or **most reviewed** listings easily.
    - Gain insights into **which neighborhoods have the most listings and their average prices**.
    - Make informed decisions whether you're a traveler, host, or researcher.

    Happy exploring! 🚀
    """)

# Map section at the top
st.subheader("🗺️ Airbnb Listings Map")
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)
for _, row in df_filtered.iterrows():
    folium.Marker(
        [row['latitude'], row['longitude']], 
        popup=f"{row['name']}\n${row['price']}/night\n{row['room_type']}",
        tooltip=row['name'],
        icon=folium.Icon(color='blue' if row['price'] < 100 else 'red')
    ).add_to(m)
folium_static(m, width=1200, height=500)

# Dashboard summary
st.markdown("""
### 📌 Dashboard Summary

This interactive dashboard provides insights into Vancouver's Airbnb market. Here's what you can explore:

- **🗺️ Map View**: Visualize all listings on an interactive map (shown above)
- **📊 Price Analysis**: See price distributions and averages by room type
- **📅 Review Activity**: Explore when listings were last reviewed and review frequency
- **🏘️ Neighborhood Insights**: Compare metrics across different neighborhoods
- **🔍 Filtered Data**: Use the sidebar filters to focus on specific listings

Navigate through the dashboard using the "Go to Home Page" button in the sidebar to see all visualizations.
""")

# Layout of Content when "Home" Button is Clicked
if home_button:
    # Price Distribution
    st.subheader("📊 Price Distribution")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_filtered['price'], bins=30, kde=True, color='royalblue', ax=ax)
    ax.set_xlabel("Price ($)")
    ax.set_ylabel("Count")
    ax.grid(True)
    st.pyplot(fig)

    # Average Price by Room Type
    st.subheader("🏠 Average Price by Room Type")
    fig, ax = plt.subplots(figsize=(5, 5))
    df_room_avg = df_filtered.groupby('room_type')['price'].mean().sort_values()
    df_room_avg.plot(kind='bar', color=['coral', 'lightblue', 'green'], ax=ax)
    ax.set_ylabel("Average Price ($)")
    ax.set_xlabel("Room Type")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)

    # Additional Stats
    st.subheader("📌 Additional Insights")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Price", f"${df_filtered['price'].mean():.2f}")
    col2.metric("Total Listings", len(df_filtered))
    col3.metric("Average Reviews per Month", f"{df_filtered['reviews_per_month'].mean():.1f}")

    # Top 10 Cheapest Listings
    st.subheader("🔻 Top 10 Cheapest Listings")
    st.dataframe(df_filtered.nsmallest(10, 'price')[['name', 'neighbourhood', 'room_type', 'price', 'number_of_reviews', 'availability_365']])

    # Reviews Activity Analysis
    st.subheader("📅 Last Review Date Analysis")
    df_filtered['last_review_year'] = df_filtered['last_review'].dt.year
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(data=df_filtered, x='last_review_year', color='teal', ax=ax)
    ax.set_xlabel("Year of Last Review")
    ax.set_ylabel("Number of Listings")
    ax.grid(True)
    st.pyplot(fig)

    # Reviews per Month Distribution
    st.subheader("📈 Reviews per Month Distribution")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_filtered['reviews_per_month'], bins=20, kde=True, color='purple', ax=ax)
    ax.set_xlabel("Reviews per Month")
    ax.set_ylabel("Count")
    ax.grid(True)
    st.pyplot(fig)

    # Price Heatmap
    st.subheader("🔥 Price Heatmap")
    m_heatmap = folium.Map(location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()], zoom_start=12)
    for _, row in df_filtered.iterrows():
        folium.CircleMarker(
            [row['latitude'], row['longitude']], 
            radius=5, 
            color='red' if row['price'] > 200 else 'green', 
            fill=True, 
            fill_color='red' if row['price'] > 200 else 'green', 
            fill_opacity=0.6
        ).add_to(m_heatmap)
    folium_static(m_heatmap, width=1200, height=500)

    # Neighborhood Insights
    st.subheader("🏘️ Neighborhood Insights")
    neighborhood_stats = df_filtered.groupby('neighbourhood').agg(
        average_price=('price', 'mean'),
        num_listings=('id', 'count'),
        avg_availability=('availability_365', 'mean'),
        avg_reviews_per_month=('reviews_per_month', 'mean')
    ).reset_index().sort_values('average_price', ascending=False)
    
    st.dataframe(neighborhood_stats)