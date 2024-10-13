import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page configuration
st.set_page_config(page_title="Territory-wise Data Analytics")

# Function to load datasets
@st.cache_data
def load_data():
    arrivals = pd.read_csv('admin/cleaned_arrivals_data.csv')
    departures = pd.read_csv('admin/cleaned_departures_data.csv')
    return arrivals, departures

# Function to compute net migration
def compute_net_migration(arrivals, departures):
    # Ensure both datasets have the same structure
    net_migration = arrivals.copy()
    years_columns = [col for col in arrivals.columns if col not in ['SACC code', 'Country of birth', 'Territory']]
    net_migration[years_columns] = arrivals[years_columns].values - departures[years_columns].values
    return net_migration

# Function to display analytics
def show_analytics():
    arrivals_df, departures_df = load_data()
    net_migration_df = compute_net_migration(arrivals_df, departures_df)

    # Define years columns
    years_columns = [col for col in arrivals_df.columns if col not in ['SACC code', 'Country of birth', 'Territory']]

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Arrivals", "Departures", "Net Migration"])

    # Dictionary to map tabs to datasets
    data_dict = {
        "Arrivals": arrivals_df,
        "Departures": departures_df,
        "Net Migration": net_migration_df
    }

    for tab_name, tab in zip(data_dict.keys(), [tab1, tab2, tab3]):
        with tab:
            df = data_dict[tab_name]
            st.title(f"{tab_name} Data Analytics")
            st.write(f"""
            Explore insights across different Australian territories for {tab_name.lower()}. Use the visualizations below to understand trends, 
            distributions, and comparisons over time.
            """)

            # 1. Territory-wise Yearly Trends (Line Plot)
            st.subheader("Yearly Trends by Territory")
            territory = st.selectbox("Select Territory", df['Territory'].unique(), key=f"territory_{tab_name}")
            selected_territory_data = df[df['Territory'] == territory]

            # Sum counts for each year across all countries of birth in the selected territory
            territory_yearly_totals = selected_territory_data[years_columns].sum()

            fig, ax = plt.subplots(figsize=(10, 5))
            territory_yearly_totals.plot(ax=ax)
            ax.set_title(f"Yearly Trends for {territory} ({tab_name})")
            ax.set_xlabel("Year")
            ax.set_ylabel("Total Count")
            st.pyplot(fig)
            st.write(f"This plot shows the yearly trend of total counts in {territory} for {tab_name.lower()}.")

            # 2. Total Counts by Territory (Bar Plot)
            st.subheader("Total Counts by Territory")
            territory_totals = df.groupby('Territory')[years_columns].sum().sum(axis=1).sort_values(ascending=False)

            fig, ax = plt.subplots(figsize=(12, 6))
            territory_totals.plot(kind='bar', ax=ax)
            ax.set_title(f"Total Counts by Territory ({tab_name})")
            ax.set_xlabel("Territory")
            ax.set_ylabel("Total Count")
            st.pyplot(fig)
            st.write(f"This bar chart shows the total counts across all years for each territory ({tab_name.lower()}).")

            # 3. Distribution of Birth Origins by Territory (Pie Chart)
            st.subheader("Distribution of Birth Origins within a Territory")
            selected_territory = st.selectbox("Select Territory for Distribution", df['Territory'].unique(), key=f"distribution_territory_{tab_name}")
            selected_territory_data = df[df['Territory'] == selected_territory].copy()  # Ensure deep copy
            selected_territory_data.loc[:, 'Total'] = selected_territory_data[years_columns].sum(axis=1)  # Correct assignment
            birth_distribution = selected_territory_data.groupby('Country of birth')['Total'].sum()

            # Optionally, get top N countries
            top_N = st.slider("Select number of top countries to display", min_value=1, max_value=20, value=10, key=f"top_N_{tab_name}")
            birth_distribution = birth_distribution.sort_values(ascending=False).head(top_N)

            fig, ax = plt.subplots(figsize=(8, 8))
            birth_distribution.plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=90)
            ax.set_ylabel("")  # Hide y-label for a cleaner display
            ax.set_title(f"Top {top_N} Birth Origins in {selected_territory} ({tab_name})")
            st.pyplot(fig)
            st.write(f"This pie chart shows the distribution of the top {top_N} countries of birth in {selected_territory} ({tab_name.lower()}).")

            # 4. Heatmap of Counts Across Territories and Years
            st.subheader("Heatmap of Counts Across Territories and Years")
            heatmap_data = df.groupby('Territory')[years_columns].sum()
            heatmap_data = heatmap_data.fillna(0)

            fig, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, fmt='.0f', ax=ax)
            ax.set_title(f"Counts Across Territories and Years ({tab_name})")
            ax.set_xlabel("Year")
            ax.set_ylabel("Territory")
            st.pyplot(fig)
            st.write(f"This heatmap visualizes the counts across territories and years for {tab_name.lower()}, highlighting trends and patterns.")

            # 5. Comparison Between Two Territories (Line Plot)
            st.subheader("Comparison Between Two Territories")
            available_territories = df['Territory'].dropna().unique()
            territories = st.multiselect(
                "Select Two Territories to Compare",
                available_territories,
                default=list(available_territories)[:2],
                key=f"compare_territories_{tab_name}"
            )

            if len(territories) == 2:
                comparison_data = df[df['Territory'].isin(territories)]
                if comparison_data.empty:
                    st.warning("No data available for the selected territories.")
                else:
                    comparison_data = comparison_data.groupby('Territory')[years_columns].sum().T

                    fig, ax = plt.subplots(figsize=(10, 5))
                    comparison_data.plot(ax=ax)
                    ax.set_title(f"Comparison of {territories[0]} and {territories[1]} ({tab_name})")
                    ax.set_xlabel("Year")
                    ax.set_ylabel("Total Count")
                    st.pyplot(fig)
                    st.write(f"This plot compares the total counts over the years between **{territories[0]}** and **{territories[1]}** for {tab_name.lower()}.")
            else:
                st.warning("Please select exactly two territories to compare.")

            # 6. Stacked Area Chart of Positive and Negative Net Migration
            st.subheader("Stacked Area Chart of Net Migration (Positive and Negative)")

            # Split net migration data into positive and negative parts
            net_migration_data = net_migration_df.groupby('Territory')[years_columns].sum().T

            # Create two DataFrames: one with only positive values and one with only negative values
            positive_net_migration = net_migration_data.clip(lower=0)  # Clip negative values to 0
            negative_net_migration = net_migration_data.clip(upper=0).abs()  # Clip positive values to 0 and take absolute value

            # Plot positive net migration
            fig, ax = plt.subplots(figsize=(12, 6))
            positive_net_migration.plot(kind='area', stacked=True, ax=ax)
            ax.set_title("Positive Net Migration Over the Years")
            ax.set_xlabel("Year")
            ax.set_ylabel("Total Positive Net Migration")
            st.pyplot(fig)
            st.write("This stacked area chart shows the positive net migration over the years, highlighting where arrivals exceeded departures.")

            # Plot negative net migration
            fig, ax = plt.subplots(figsize=(12, 6))
            negative_net_migration.plot(kind='area', stacked=True, ax=ax)
            ax.set_title("Negative Net Migration Over the Years")
            ax.set_xlabel("Year")
            ax.set_ylabel("Total Negative Net Migration")
            st.pyplot(fig)
            st.write("This stacked area chart shows the negative net migration over the years, indicating where departures exceeded arrivals.")

            # 7. Box Plot of Counts Distribution Across Territories
            st.subheader("Box Plot of Counts Distribution Across Territories")
            melted_df = df.melt(id_vars=['Territory'], value_vars=years_columns, var_name='Year', value_name='Count')
            melted_df['Count'] = pd.to_numeric(melted_df['Count'], errors='coerce')
            melted_df = melted_df.dropna(subset=['Count'])
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.boxplot(x='Territory', y='Count', data=melted_df, ax=ax)
            ax.set_title(f"Distribution of Counts Across Territories ({tab_name})")
            ax.set_xlabel("Territory")
            ax.set_ylabel("Count")
            plt.xticks(rotation=45)
            st.pyplot(fig)
            st.write(f"This box plot displays the distribution of counts for each territory in {tab_name.lower()}, providing insights into the spread and central tendency of the data.")

            # 8. Clustered Bar Chart of Average Counts by Territory
            st.subheader("Clustered Bar Chart of Average Counts by Territory")
            average_counts = df.groupby('Territory')[years_columns].mean()

            fig, ax = plt.subplots(figsize=(12, 6))
            average_counts.plot(kind='bar', ax=ax)
            ax.set_title(f"Average Counts by Territory Over the Years ({tab_name})")
            ax.set_xlabel("Territory")
            ax.set_ylabel("Average Count")
            plt.xticks(rotation=45)
            st.pyplot(fig)
            st.write(f"This clustered bar chart shows the average counts for each territory across all years in {tab_name.lower()}, allowing for easy comparison between territories.")

