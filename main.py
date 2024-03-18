from datetime import datetime, timedelta
import os
import pytz
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from discord import Embed
import logging
import requests  # For making HTTP requests
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Discord bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

nepal_timezone = pytz.timezone('Asia/Kathmandu')

# API Endpoints
BASE_URL = os.getenv('BASE_URL')
USERS_API = BASE_URL + "/api/users/"
PROJECTS_API = BASE_URL + "/api/projects/"
UPDATE_REMINDER_API = BASE_URL + "/api/users/{}/{}/"

def parse_reminder_time(reminder_time_str, now):
    try:
        if 'am' in reminder_time_str or 'pm' in reminder_time_str:
            if ':' not in reminder_time_str:
                reminder_time_str = reminder_time_str.replace('am', ':00am').replace('pm', ':00pm')
        else:
            if reminder_time_str.count(':') == 0:
                reminder_time_str += ":00"

        reminder_time = datetime.strptime(reminder_time_str, "%I:%M%p").time()
    except ValueError:
        reminder_time = datetime.strptime(reminder_time_str, "%H:%M").time()

    reminder_time = datetime.combine(now.date(), reminder_time).replace(tzinfo=now.tzinfo)
    return reminder_time

def create_project_embed(project):
    embed = Embed(title="Scheduled Reminder", description="It's time to do some tasks!", color=0x00ff00)
    tasks = project.get('tasks', '').replace('\\n', '\n')

    fields = [
        ("Project Name", project.get('project_name', 'N/A'), False),
        ("Tier", project.get('tier'), True),
        ("Cost to Farm", project.get('cost_to_farm'), True),
        ("Airdrop Status", project.get('airdrop_status'), True),
        ("Priority", project.get('priority'), True),
        ("Funding", project.get('funding'), True),
        ("Stage", project.get('stage'), True),
        ("Type", project.get('type'), True),
        ("Chain", project.get('chain'), True),
        ("Twitter Guide", project.get('twitter_guide'), False),
        ("Discord Link", project.get('discord_link'), True),
        ("Twitter Link", project.get('twitter_link'), True),
        ("Tasks", tasks or 'N/A', False)
    ]

    for name, value, inline in fields:
        if value:
            embed.add_field(name=name, value=value, inline=inline)

    if thumbnail_url := project.get('image_link'):
        embed.set_thumbnail(url=thumbnail_url.strip())

    return embed

def should_send_reminder(reminder, now):
    reminder_datetime = parse_reminder_time(reminder["reminder_time"], now)
    last_reminded = reminder.get("last_reminded")

    if isinstance(last_reminded, str) and last_reminded:
        last_reminded = nepal_timezone.localize(datetime.strptime(last_reminded, "%Y-%m-%d %H:%M:%S"))
    elif not isinstance(last_reminded, datetime) and not last_reminded:
        last_reminded = now - timedelta(days=1)
    else:
        last_reminded = last_reminded.replace(tzinfo=pytz.utc).astimezone(nepal_timezone)

    print(f"Reminder time: {reminder_datetime} - Last reminded: {last_reminded} - Now: {now}")

    frequency = reminder["frequency"]
    if now < reminder_datetime or \
       (frequency == "daily" and now.date() == last_reminded.date()) or \
       (frequency == "weekly" and (now - last_reminded).days < 7):
        return False
    return True

@tasks.loop(seconds=60)
async def check_reminders():
    now = datetime.now(nepal_timezone)
    logging.info(f"Current Nepal time: {now}")

    reminders_response = requests.get(USERS_API)
    print(reminders_response)
    if reminders_response.status_code == 200:
        reminders = reminders_response.json()

        for reminder in reminders:
            print(f"Reminder id: {reminder['id']} - {reminder['reminder_time']}")
            if should_send_reminder(reminder, now):
                try:
                    user_id = reminder["username"]
                    reminder_id = reminder["id"]
                    user = discord.utils.get(bot.get_all_members(), name=f"{reminder['username']}", discriminator="0")
                    project_response = requests.get(f"{PROJECTS_API}{reminder['project']}")
                    if project_response.status_code == 200:
                        project = project_response.json()
                        if user and project:
                            logging.info(f"Sending reminder to {user.name} for project {project['project_name']}")
                            embed = create_project_embed(project)
                            await user.send(embed=embed)
                            reminder["last_reminded"] = now.strftime("%Y-%m-%d %H:%M:%S")
                            url = UPDATE_REMINDER_API.format(user_id, reminder_id)
                            print(url)
                            response = requests.put(url, json=reminder).json()
                            print(response)
                except Exception as e:
                    logging.error(f"Error during reminder check: {e}")
                    traceback.print_exc()
    else:
        logging.error("Failed to fetch reminders")

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} has connected to Discord!')
    check_reminders.start()

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
