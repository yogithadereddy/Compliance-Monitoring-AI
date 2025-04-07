from pymongo import MongoClient
import os

# Load MongoDB credentials from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:28017/")
DB_NAME = "regulatory_ai"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Define collections
regulations_collection = db["regulatory_updates"]
