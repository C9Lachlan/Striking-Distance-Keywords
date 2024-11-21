import streamlit as st
import pandas as pd
from scipy.stats import zscore

# Streamlit interface
st.title('Striking Distance Keywords')

st.markdown("#### Inputs")
# Search Console Queries Section
file1 = st.file_uploader("Search Console Queries", type="csv", key="file1")
st.write("Find the file at Search Console > Search Results > Export > Queries (then File > Download > .csv)")
st.markdown("<br>", unsafe_allow_html=True)

# Ahrefs Volume Data Section
file2 = st.file_uploader("Ahrefs Volume Data", type="csv", key="file2")
st.write("Find the file at Ahrefs > Keyword Explorer > paste in the keywords from Search Console > Export ")
st.markdown("<br>", unsafe_allow_html=True)

# Looker Studio Cannibalisation Export Section
file3 = st.file_uploader("Looker Studio Cannibalisation Export", type="csv", key="file3")
st.write("https://lookerstudio.google.com/reporting/f3b15314-d09d-4f40-bf3e-4bf37813dfd1")
st.write("Find the file at Looker Studio on the Webmaster Account > Keyword Cannibalisation Export Tool > Select site from dropdown > More (in corner of the table) > Export")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")  # Horizontal bar

# Initialize position range with default values
min_position_default, max_position_default = 6, 30

st.markdown("#### Settings")
# Position Slider
min_position, max_position = st.slider(
    "Select the range for Average Position:",
    min_value=1, 
    max_value=50, 
    value=(min_position_default, max_position_default)
)

# Exclude Brand Keywords Input
exclusion_input = st.text_input(
    "Enter brand keywords to exclude (separated by commas):",
    placeholder="e.g., free, discount, sale"
)

# Combine matching keywords checkbox
combine_keywords = st.checkbox("Combine matching keywords")

# Process the exclusion keywords
if exclusion_input:
    exclusion_keywords = [keyword.strip().lower() for keyword in exclusion_input.split(',') if keyword.strip()]
    st.write(f"Excluding keywords containing: {', '.join(exclusion_keywords)}")
else:
    exclusion_keywords = []

if file1 and file2 and file3:
    # Read CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df3 = pd.read_csv(file3)

    # Ensure the necessary columns exist
    required_columns_df1 = {'Top queries', 'Position'}
    required_columns_df2 = {'Keyword', 'Volume', 'Difficulty', 'Intents'}
    required_columns_df3 = {'Query', 'Landing Page' ,'Impressions'}

    if required_columns_df1.issubset(df1.columns) and \
        required_columns_df2.issubset(df2.columns) and \
        required_columns_df3.issubset(df3.columns):
        
        # If the checkbox is checked, process df3 to keep rows with the highest impressions
        if combine_keywords:
            df3 = df3.loc[df3.groupby('Query')['Impressions'].idxmax()]

        # Merge the dataframes on Query and Keyword/Top queries column
        merged_df = pd.merge(df1, df2, left_on='Top queries', right_on='Keyword', how='inner')
        merged_df = pd.merge(merged_df, df3, left_on='Top queries', right_on='Query', how='inner')
        
        if not merged_df.empty:
            # Filter based on user-selected position range
            filtered_df = merged_df[(merged_df['Position'] >= min_position) & (merged_df['Position'] <= max_position)]

            # **Apply Exclusion Keywords Filter**
            if exclusion_keywords:
                # Use case-insensitive matching
                pattern = '(?i)(' + '|'.join(exclusion_keywords) + ')'
                filtered_df = filtered_df[~filtered_df['Keyword'].str.contains(pattern, regex=True, na=False)]
                st.write(f"After exclusion, {filtered_df.shape[0]} keywords remain.")

            # Handle missing values by replacing them with 0 or 1 as appropriate
            filtered_df['Volume'] = filtered_df['Volume'].fillna(1)
            filtered_df['Difficulty'] = filtered_df['Difficulty'].fillna(0)
            
            # Calculate Opportunity Score
            filtered_df['Opportunity Score'] = (100 - filtered_df['Difficulty']) * filtered_df['Volume']
            
            # Calculate the z-score for Opportunity Score
            filtered_df['Opportunity Z-Score'] = zscore(filtered_df['Opportunity Score'])
            
            # Round the Opportunity Score Z-Score to two decimal places
            filtered_df['Opportunity Z-Score'] = filtered_df['Opportunity Z-Score'].round(2)
            
            # Rename Position column to Average Position
            filtered_df = filtered_df.rename(columns={'Position': 'Average Position'})
            
            # Select the relevant columns and order by Opportunity Score Z-Score
            output_df = filtered_df[['Keyword', 'Landing Page', 'Average Position', 'Volume', 'Difficulty', 'Opportunity Z-Score', 'Intents']].sort_values(by='Opportunity Z-Score', ascending=False)
            
            # Reset the index to remove row numbers
            output_df_reset_index = output_df.reset_index(drop=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")  # Horizontal bar

            # Display the output
            st.write('### Striking Distance Keywords:')
            st.dataframe(output_df_reset_index)

            # Option to download the resulting DataFrame
            csv = output_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Output as CSV",
                data=csv,
                file_name='output.csv',
                mime='text/csv',
            )
        else:
            st.warning("The merged DataFrame is empty. Please check your CSV files for matching data.")
    else:
        st.error("One or more CSV files are missing the required columns.")
else:
    st.info("Please upload all three CSV files.")