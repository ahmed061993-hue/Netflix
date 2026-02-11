import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Netflix Analytics Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('netflix_titles.csv')
    # Clean up date_added and extract year
    df['date_added'] = pd.to_datetime(df['date_added'].str.strip(), errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    return df

df = load_data()

# Sidebar - Title and Filters
st.sidebar.title("Netflix Dashboard Filters")
content_type = st.sidebar.multiselect("Select Content Type", 
                                      options=df['type'].unique(), 
                                      default=df['type'].unique())

year_range = st.sidebar.slider("Select Release Year Range", 
                               int(df['release_year'].min()), 
                               int(df['release_year'].max()), 
                               (2010, 2021))

# Filter Data
filtered_df = df[(df['type'].isin(content_type)) & 
                 (df['release_year'].between(year_range[0], year_range[1]))]

# Main Page - Title and Metrics
st.title("🎬 Netflix Content Analysis")
st.markdown("Exploring the distribution and trends of Netflix movies and TV shows.")

col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", len(filtered_df))
col2.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
col3.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))

st.divider()

# Row 1: Distribution Charts
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Content Type Distribution")
    type_counts = filtered_df['type'].value_counts().reset_index()
    fig_pie = px.pie(type_counts, values='count', names='type', 
                     color_discrete_sequence=px.colors.sequential.RdBu, hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with row1_col2:
    st.subheader("Top 10 Genres")
    genres = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(10).reset_index()
    fig_genres = px.bar(genres, x='count', y='listed_in', orientation='h',
                        labels={'listed_in': 'Genre', 'count': 'Count'},
                        color='count', color_continuous_scale='Reds')
    fig_genres.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_genres, use_container_width=True)

# Row 2: Trends and Geography
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Top 10 Countries Producing Content")
    countries = filtered_df['country'].str.split(', ').explode().value_counts().head(10).reset_index()
    fig_country = px.bar(countries, x='country', y='count', 
                         color='count', color_continuous_scale='Viridis')
    st.plotly_chart(fig_country, use_container_width=True)

with row2_col2:
    st.subheader("Content Added Over Time")
    growth = filtered_df.groupby('year_added').size().reset_index(name='count')
    fig_growth = px.area(growth, x='year_added', y='count', 
                         line_shape='spline', color_discrete_sequence=['#E50914'])
    st.plotly_chart(fig_growth, use_container_width=True)

# Data Table
st.divider()
st.subheader("Explore the Raw Data")
search_term = st.text_input("Search for a title or director")
if search_term:
    search_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False) | 
                            filtered_df['director'].str.contains(search_term, case=False, na=False)]
    st.dataframe(search_df, use_container_width=True)
else:
    st.dataframe(filtered_df.head(100), use_container_width=True)
