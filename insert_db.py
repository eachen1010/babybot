import pymongo
import datetime
import random

# Connect to your MongoDB database

DB_PASSWORD = '55jYmZd9jScKXhrU'

# Replace with your MongoDB connection string
client = pymongo.MongoClient(f'mongodb+srv://eachen1010:{DB_PASSWORD}@babybotdb.ioh3s.mongodb.net/') # Replace with your connection string
db = client["baby_stats"]
collection = db["babybot_stats"]

# Function to generate random data
def generate_random_data():
    humidity = round(random.uniform(30, 80), 2)
    temperature = round(random.uniform(20, 30), 2)
    decibel = round(random.uniform(40, 80), 2)
    timestamp = datetime.datetime.utcnow()
    return {"humidity": humidity, "temperature": temperature, "decibel": decibel, "timestamp": timestamp}

# Insert multiple documents
for _ in range(10):  # Adjust the number of documents as needed
    data = generate_random_data()
    result = collection.insert_one(data)
    print(f"Inserted document with ID: {result.inserted_id}")