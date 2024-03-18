from pymongo import MongoClient
import sys
from dotenv import load_dotenv
import os

# Function to ask for input and validate it
def ask_for_input(prompt, input_type):
    while True:
        user_input = input(prompt)
        if input_type == 'int':
            try:
                return int(user_input)
            except ValueError:
                print("Please enter a valid integer.")
        elif input_type == 'str':
            if user_input:
                return user_input
            else:
                print("Input cannot be empty.")
        else:
            break

# Connect to the MongoDB database
load_dotenv()
MONGO_DB_URL = os.getenv('MONGO_DB_URL')

client = MongoClient(MONGO_DB_URL)
db = client['reminder_database']  # Use your database name
collection = db['reminders']  # Use your collection name

# Ask user for input
username = ask_for_input("Enter username: ", 'str')
reminder_time = ask_for_input("Enter reminder time (e.g., 9pm, 10:15am): ", 'str')
frequency = ask_for_input("Enter frequency (e.g., daily, weekly): ", 'str')
progress = ask_for_input("Enter progress (e.g., s, None): ", 'str')
project = ask_for_input("Enter project ID (integer): ", 'int')

# Create the document to be inserted
reminder_document = {
    "username": username,
    "reminder_time": reminder_time,
    "frequency": frequency,
    "progress": progress,
    "project": project
}

# Insert the document into the collection
try:
    result = collection.insert_one(reminder_document)
    print(f"Reminder added successfully with ID: {result.inserted_id}")
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
