import pandas as pd

# Load both CSV files
newsapi_df = pd.read_csv('newsapi_regulations.csv')
regulations_df = pd.read_csv('regulations_data.csv')

# Combine them
combined_df = pd.concat([regulations_df, newsapi_df], ignore_index=True)

# Optional: Remove duplicates if needed based on 'link' or 'title'
combined_df.drop_duplicates(subset='link', inplace=True)

# Save to new file
combined_df.to_csv('merged_regulations.csv', index=False)

print(f"✅ Combined {len(regulations_df)} + {len(newsapi_df)} rows into merged_regulations.csv")
