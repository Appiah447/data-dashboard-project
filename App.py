import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static

# Set Streamlit Page Config (Must be the first Streamlit command)
st.set_page_config(page_title="Vancouver Airbnb Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("listings.csv")
    df = df[['id', 'name', 'neighbourhood', 'room_type', 'price', 'latitude', 'longitude', 'number_of_reviews', 'availability_365']]
    df = df.dropna()
    df['price'] = df['price'].replace({'\\$': '', ',': ''}, regex=True).astype(float)
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
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🏡 Vancouver Airbnb Data Dashboard")
st.markdown("Analyze Airbnb listings in Vancouver using interactive charts, filters, and maps.")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
neighborhoods = st.sidebar.multiselect("Select Neighborhoods", df['neighbourhood'].unique(), default=df['neighbourhood'].unique())
price_range = st.sidebar.slider("Select Price Range ($)", int(df['price'].min()), int(df['price'].max()), (50, 300))
room_types = st.sidebar.multiselect("Select Room Type", df['room_type'].unique(), default=df['room_type'].unique())
availability = st.sidebar.slider("Availability (days per year)", int(df['availability_365'].min()), int(df['availability_365'].max()), (0, 365))

df_filtered = df[(df['neighbourhood'].isin(neighborhoods)) &
                 (df['price'].between(price_range[0], price_range[1])) &
                 (df['room_type'].isin(room_types)) &
                 (df['availability_365'].between(availability[0], availability[1]))]

# Layout: Column Division
col1, col2 = st.columns([2, 1])

# Price Distribution
with col1:
    st.subheader("📊 Price Distribution")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_filtered['price'], bins=30, kde=True, color='royalblue', ax=ax)
    ax.set_xlabel("Price ($)")
    ax.set_ylabel("Count")
    ax.grid(True)
    st.pyplot(fig)

# Average Price by Room Type
with col2:
    st.subheader("🏠 Average Price by Room Type")
    fig, ax = plt.subplots(figsize=(5, 5))
    df_room_avg = df_filtered.groupby('room_type')['price'].mean().sort_values()
    df_room_avg.plot(kind='bar', color=['coral', 'lightblue', 'green'], ax=ax)
    ax.set_ylabel("Average Price ($)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)

# Map of Listings
st.subheader("🗺️ Airbnb Listings Map")
m = folium.Map(location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()], zoom_start=12)
for _, row in df_filtered.iterrows():
    folium.Marker([row['latitude'], row['longitude']], 
                  popup=f"{row['name']} - ${row['price']}\nReviews: {row['number_of_reviews']}", 
                  tooltip=row['name'],
                  icon=folium.Icon(color='blue' if row['price'] < 100 else 'red')).add_to(m)
folium_static(m)

# Additional Stats
st.subheader("📌 Additional Insights")
st.metric("Average Price", f"${df_filtered['price'].mean():.2f}")
st.metric("Total Listings", len(df_filtered))
st.metric("Average Reviews", f"{df_filtered['number_of_reviews'].mean():.1f}")

# Top 10 Cheapest Listings
st.subheader("🔻 Top 10 Cheapest Listings")
st.dataframe(df_filtered.nsmallest(10, 'price')[['name', 'neighbourhood', 'room_type', 'price', 'number_of_reviews', 'availability_365']])
