import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables from .env if needed
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:28017/"))
db = client["regulatory_ai"]  # Replace with your DB name
collection = db["regulatory_updates"]

# Fetch all documents
documents = list(collection.find())

# Convert ObjectId and array fields
for doc in documents:
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    doc["categories"] = ", ".join(doc.get("categories", []))
    doc["impact_areas"] = ", ".join(doc.get("impact_areas", []))

# Define column order (optional)
columns = [
    "_id",
    "title",
    "link",
    "date",
    "source",
    "regulatory_body",
    "release_no",
    "content",
    "full_content",
    "categories",
    "impact_areas",
    "geographic_scope",
    "summary",
    "processed",
    "last_updated"
]

# Convert to DataFrame
df = pd.DataFrame(documents)

# Reorder columns if needed
df = df[columns]

# Save to CSV
df.to_csv("regulations_data.csv", index=False)
print("✅ Data exported to regulations_data.csv")
