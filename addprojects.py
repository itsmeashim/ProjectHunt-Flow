from pymongo import MongoClient
import sys
from dotenv import load_dotenv
import os

# Establish connection to MongoDB
load_dotenv()
MONGO_DB_URL = os.getenv('MONGO_DB_URL')

# Connect to MongoDB
client = MongoClient(MONGO_DB_URL)
db = client["reminder_database"]
projects_collection = db["projects"]

def input_with_prompt(prompt, required=False, input_type=str):
    """Helper function to get user input with validation."""
    while True:
        user_input = input(prompt)
        if not user_input and required:
            print("This field is required. Please enter a value.")
            continue
        try:
            return input_type(user_input) if user_input else None
        except ValueError:
            print(f"Invalid input type. Please enter a {input_type.__name__} value.")
            continue

def add_project_interactively():
    """
    Ask the user for project details interactively and add the project to the database.
    """
    print("Enter project details (leave optional fields blank if not applicable):")

    id = input_with_prompt("ID (required): ", required=True, input_type=int)
    project_name = input_with_prompt("Project Name (required): ", required=True)
    tier = input_with_prompt("Tier (required): ", required=True)
    cost_to_farm = input_with_prompt("Cost to Farm (default 0.0): ", input_type=float) or 0.0
    airdrop_status = input_with_prompt("Airdrop Status (required): ", required=True)
    priority = input_with_prompt("Priority: ")
    funding = input_with_prompt("Funding (default 0.0): ", input_type=float) or 0.0
    stage = input_with_prompt("Stage: ")
    type = input_with_prompt("Type (required): ", required=True)
    chain = input_with_prompt("Chain: ")
    tasks = input_with_prompt("Tasks: ")
    twitter_guide = input_with_prompt("Twitter Guide URL: ")
    discord_link = input_with_prompt("Discord Link: ")
    twitter_link = input_with_prompt("Twitter Link: ")
    frequency = input_with_prompt("Frequency (default daily): ") or "daily"
    image_link = input_with_prompt("Image Link: ")

    project_data = {
        "id": id,
        "project_name": project_name,
        "tier": tier,
        "cost_to_farm": cost_to_farm,
        "airdrop_status": airdrop_status,
        "priority": priority,
        "funding": funding,
        "stage": stage,
        "type": type,
        "chain": chain,
        "tasks": tasks,
        "twitter_guide": twitter_guide,
        "discord_link": discord_link,
        "twitter_link": twitter_link,
        "frequency": frequency,
        "image_link": image_link
    }

    # Insert the project into the database
    try:
        projects_collection.insert_one(project_data)
        print(f"Project {project_name} added successfully.")
    except Exception as e:
        print(f"Error adding project: {e}")

if __name__ == "__main__":
    try:
        add_project_interactively()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
        sys.exit(1)
