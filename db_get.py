import pymongo
import datetime

class BabyStats:
    def __init__(self, DB_PASSWORD):
        # Connect to MongoDB database
        self.client = pymongo.MongoClient(f'mongodb+srv://eachen1010:{DB_PASSWORD}@babybotdb.ioh3s.mongodb.net/')
        self.db = self.client["baby_stats"]
        self.collection = self.db["babybot_stats"]

    def update_arrays(self):
        # Find all documents, sorted by timestamp
        cursor = self.collection.find().sort("timestamp", pymongo.ASCENDING)

        # Create empty lists to store data
        timestamps = []
        temperatures = []
        humidities = []
        decibels = []
        states = []

        # Iterate through the cursor and append data to lists
        for document in cursor:
            timestamps.append(float(document["timestamp"]))
            temperatures.append(float(document["temperature"]))
            humidities.append(float(document["humidity"]))
            decibels.append(float(document["decibel"]))
            states.append(document["state"])

        # Print the sorted lists
        print("Timestamps:", timestamps)
        print("Temperatures:", temperatures)
        print("Humidities:", humidities)
        print("Decibels:", decibels)

        return temperatures, humidities, decibels, states