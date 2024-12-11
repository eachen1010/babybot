from flask import Flask, request, jsonify
import pymongo

app = Flask(__name__)
DB_PASSWORD = '55jYmZd9jScKXhrU'

# Connect to MongoDB database
client = pymongo.MongoClient(f'mongodb+srv://eachen1010:{DB_PASSWORD}@babybotdb.ioh3s.mongodb.net/') # Replace with your connection string
db = client["baby_stats"]
collection = db["babybot_stats"]

@app.route('/data', methods=['GET', 'POST'])
def post_data():
    # Extract data from the request
    timestamp = request.form.get('time')
    temperature = request.form.get('temp')
    humidity = request.form.get('humidity')
    decibel = request.form.get('mic')
    state = request.form.get('state')


    # Insert the data into the MongoDB collection
    collection.insert_one({
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "decibel": decibel,
        "state": state
    })

    return jsonify({'message': 'Data received and inserted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)