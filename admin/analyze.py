import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page configuration
st.set_page_config(page_title="Territory-wise Data Analytics", layout="wide")

# Function to load the cleaned combined data
@st.cache_data
def load_data():
    return pd.read_csv('admin/cleaned_combined_data.csv')

# Function to display the analytics with enhanced visualizations
def show_analytics():
    df = load_data()

    # Title and description for the analytics page
    st.title("Territory-wise Data Analytics")
    st.write("""
    Explore insights across different Australian territories. Use the visualizations below to understand trends, 
    distributions, and comparisons over time.
    """)

    # Define years columns
    years_columns = [col for col in df.columns if col not in ['SACC code', 'Country of birth', 'Territory']]

    # Existing plots (unchanged)...

    # 1. Territory-wise Yearly Trends (Line Plot)
    st.subheader("Yearly Trends by Territory")
    territory = st.selectbox("Select Territory", df['Territory'].unique())
    selected_territory_data = df[df['Territory'] == territory]

    # Sum counts for each year across all countries of birth in the selected territory
    territory_yearly_totals = selected_territory_data[years_columns].sum()

    fig, ax = plt.subplots(figsize=(10, 5))
    territory_yearly_totals.plot(ax=ax)
    ax.set_title(f"Yearly Trends for {territory}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Count")
    st.pyplot(fig)
    st.write("This plot shows the yearly trend of total counts in the selected territory.")

    # 2. Total Counts by Territory (Bar Plot)
    st.subheader("Total Counts by Territory")
    territory_totals = df.groupby('Territory')[years_columns].sum().sum(axis=1).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    territory_totals.plot(kind='bar', ax=ax)
    ax.set_title("Total Counts by Territory")
    ax.set_xlabel("Territory")
    ax.set_ylabel("Total Count")
    st.pyplot(fig)
    st.write("This bar chart shows the total counts across all years for each territory.")

    # 3. Distribution of Birth Origins by Territory (Pie Chart)
    st.subheader("Distribution of Birth Origins within a Territory")
    selected_territory = st.selectbox("Select Territory for Distribution", df['Territory'].unique(), key='distribution_territory')
    selected_territory_data = df[df['Territory'] == selected_territory]
    selected_territory_data['Total'] = selected_territory_data[years_columns].sum(axis=1)
    birth_distribution = selected_territory_data.groupby('Country of birth')['Total'].sum()

    # Optionally, get top N countries
    top_N = st.slider("Select number of top countries to display", min_value=1, max_value=20, value=10)
    birth_distribution = birth_distribution.sort_values(ascending=False).head(top_N)

    fig, ax = plt.subplots(figsize=(8, 8))
    birth_distribution.plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=90)
    ax.set_ylabel("")  # Hide y-label for a cleaner display
    ax.set_title(f"Top {top_N} Birth Origins in {selected_territory}")
    st.pyplot(fig)
    st.write(f"This pie chart shows the distribution of the top {top_N} countries of birth in {selected_territory}.")

    # 4. Heatmap of Counts Across Territories and Years
    st.subheader("Heatmap of Counts Across Territories and Years")
    heatmap_data = df.groupby('Territory')[years_columns].sum()

    # Replace NaN values with zeros for the heatmap
    heatmap_data = heatmap_data.fillna(0)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt='g', ax=ax)
    ax.set_title("Counts Across Territories and Years")
    ax.set_xlabel("Year")
    ax.set_ylabel("Territory")
    st.pyplot(fig)
    st.write("This heatmap visualizes the counts across territories and years, highlighting trends and patterns.")

    # 5. Comparison Between Two Territories (Line Plot)
    st.subheader("Comparison Between Two Territories")
    available_territories = df['Territory'].dropna().unique()
    territories = st.multiselect(
        "Select Two Territories to Compare",
        available_territories,
        default=list(available_territories)[:2]
    )

    if len(territories) == 2:
        comparison_data = df[df['Territory'].isin(territories)]
        if comparison_data.empty:
            st.warning("No data available for the selected territories.")
        else:
            comparison_data = comparison_data.groupby('Territory')[years_columns].sum().T

            fig, ax = plt.subplots(figsize=(10, 5))
            comparison_data.plot(ax=ax)
            ax.set_title(f"Comparison of {territories[0]} and {territories[1]}")
            ax.set_xlabel("Year")
            ax.set_ylabel("Total Count")
            st.pyplot(fig)
            st.write(f"This plot compares the total counts over the years between **{territories[0]}** and **{territories[1]}**.")
    else:
        st.warning("Please select exactly two territories to compare.")

    # Additional Comprehensive Plots

    # 6. Stacked Area Chart of Counts Over Years for All Territories
    st.subheader("Stacked Area Chart of Counts Over Years for All Territories")
    territory_yearly_data = df.groupby('Territory')[years_columns].sum()

    # Prepare data for stacked area chart
    territory_yearly_data = territory_yearly_data.T

    fig, ax = plt.subplots(figsize=(12, 6))
    territory_yearly_data.plot(kind='area', stacked=True, ax=ax)
    ax.set_title("Stacked Area Chart of Counts Over Years")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Count")
    st.pyplot(fig)
    st.write("This stacked area chart shows how the counts for each territory have changed over the years, and how they contribute to the overall total.")

    # 7. Box Plot of Counts Distribution Across Territories
    st.subheader("Box Plot of Counts Distribution Across Territories")
    # Melt the data to have years and counts in rows
    melted_df = df.melt(id_vars=['Territory'], value_vars=years_columns, var_name='Year', value_name='Count')
    melted_df['Count'] = pd.to_numeric(melted_df['Count'], errors='coerce')
    melted_df = melted_df.dropna(subset=['Count'])
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='Territory', y='Count', data=melted_df, ax=ax)
    ax.set_title("Distribution of Counts Across Territories")
    ax.set_xlabel("Territory")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    st.write("This box plot displays the distribution of counts for each territory, providing insights into the spread and central tendency of the data.")

    # 8. Clustered Bar Chart of Average Counts by Territory
    st.subheader("Clustered Bar Chart of Average Counts by Territory")
    average_counts = df.groupby('Territory')[years_columns].mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    average_counts.plot(kind='bar', ax=ax)
    ax.set_title("Average Counts by Territory Over the Years")
    ax.set_xlabel("Territory")
    ax.set_ylabel("Average Count")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    st.write("This clustered bar chart shows the average counts for each territory across all years, allowing for easy comparison between territories.")

