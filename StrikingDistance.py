import streamlit as st
import pandas as pd
from scipy.stats import zscore

# Streamlit interface
st.title('Striking Distance Keywords')

# Upload CSV files
file1 = st.file_uploader("Search Console Queries", type="csv")
file2 = st.file_uploader("Ahrefs Volume Data", type="csv")
file3 = st.file_uploader("Looker Studio Cannibalisation Export", type="csv")

if file1 and file2 and file3:
    # Read CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df3 = pd.read_csv(file3)

    # Ensure the necessary columns exist
    if 'Top queries' in df1.columns and 'Position' in df1.columns \
       and 'Keyword' in df2.columns and 'Volume' in df2.columns \
       and 'Difficulty' in df2.columns and 'Intents' in df2.columns \
       and 'Query' in df3.columns and 'Landing Page' in df3.columns:
        
        # Merge the dataframes on Query and Keyword/Top queries column
        merged_df = pd.merge(df1, df2, left_on='Top queries', right_on='Keyword', how='inner')
        merged_df = pd.merge(merged_df, df3, left_on='Top queries', right_on='Query', how='inner')

        # Filter based on Position between 6 and 30
        filtered_df = merged_df[(merged_df['Position'] >= 6) & (merged_df['Position'] <= 30)]

        # Handle missing values by replacing them with 1
        filtered_df['Volume'] = filtered_df['Volume'].fillna(0)
        filtered_df['Difficulty'] = filtered_df['Difficulty'].fillna(1)
        
        # Calculate Opportunity Score
        filtered_df['Opportunity Score'] = (100 - filtered_df['Difficulty']) * filtered_df['Volume']

        # Calculate the z-score for Opportunity Score
        filtered_df['Opportunity Z-Score'] = zscore(filtered_df['Opportunity Score'])

        # Round the Opportunity Score Z-Score to two decimal places
        filtered_df['Opportunity Z-Score'] = filtered_df['Opportunity Z-Score'].round(2)

        # Rename Position column to Average Position
        filtered_df = filtered_df.rename(columns={'Position': 'Average Position'})

        # Select the relevant columns and order by Opportunity Score Z-Score
        output_df = filtered_df[[ 'Keyword', 'Landing Page', 'Average Position' ,  'Volume',  'Difficulty', 'Opportunity Z-Score', 'Intents']].sort_values(by='Opportunity Z-Score', ascending=False)

        # Reset the index to remove row numbers
        output_df_reset_index = output_df.reset_index(drop=True)
        
        # Display the output
        st.write('Striking Distance Keywords:')
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
        st.error("One or more CSV files are missing the required columns.")
else:
    st.info("Please upload all three CSV files.")