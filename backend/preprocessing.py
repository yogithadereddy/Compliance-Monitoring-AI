import pandas as pd
from datetime import datetime

# Load CSV file
df = pd.read_csv('merged_regulations.csv')

# Convert to datetime (handling errors)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')

# Strip whitespace in text columns
text_fields = ['title', 'source', 'regulatory_body', 'geographic_scope', 'content', 'full_content']
for col in text_fields:
    df[col] = df[col].astype(str).str.strip()

# Handle missing summaries
df['summary'] = df['summary'].fillna('')

# Ensure processed column is boolean
df['processed'] = df['processed'].fillna(False).astype(bool)

# Convert comma-separated string columns to lists
def split_to_list(val):
    if pd.isna(val) or not isinstance(val, str):
        return []
    return [item.strip() for item in val.split(',') if item.strip()]

df['categories'] = df['categories'].apply(split_to_list)
df['impact_areas'] = df['impact_areas'].apply(split_to_list)

# Drop rows with missing essential data
df.dropna(subset=['title', 'content'], inplace=True)

# Save cleaned version
df.to_csv('preprocessed_regulations_pandas.csv', index=False)

print(f"✅ Preprocessed {len(df)} rows with Pandas. Saved to preprocessed_regulations_pandas.csv")
