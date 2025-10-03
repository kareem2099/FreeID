import telebot
import os
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_BOT_DB_NAME = os.getenv('MONGODB_BOT_DB_NAME', 'FreeID')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))  # Set your Telegram user ID

bot = telebot.TeleBot(BOT_TOKEN)

# MongoDB connection
client = MongoClient(MONGODB_URI)
db = client[MONGODB_BOT_DB_NAME]
users_collection = db['users']
analytics_collection = db['analytics']

# Helper function to update user analytics
def update_user_analytics(user_id, username, first_name):
    user_data = {
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'last_interaction': datetime.now(timezone.utc)
    }

    # Insert or update user
    users_collection.update_one(
        {'user_id': user_id},
        {
            '$set': user_data,
            '$inc': {'interaction_count': 1}
        },
        upsert=True
    )

    # Daily active users analytics
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    analytics_collection.update_one(
        {'date': today, 'type': 'daily_active_users'},
        {'$addToSet': {'user_ids': user_id}},
        upsert=True
    )

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user
    update_user_analytics(user.id, user.username, user.first_name)
    user_info = f"""
🔍 <b>User Information</b> 🔍

👤 <b>First Name:</b> {user.first_name or 'N/A'}
👥 <b>Last Name:</b> {user.last_name or 'N/A'}
🎭 <b>Username:</b> {f"@{user.username}" if user.username else "Not set"}
🆔 <b>User ID:</b> <code>{user.id}</code>

🌍 <b>Language:</b> {user.language_code or 'N/A'}

📍 <b>Is Bot:</b> {'Yes' if user.is_bot else 'No'}
📈 <b>Can Join Groups:</b> {'Yes' if user.can_join_groups else 'No'}
💬 <b>Can Read All Group Messages:</b> {'Yes' if user.can_read_all_group_messages else 'No'}
⭐ <b>Supports Inline Queries:</b> {'Yes' if user.supports_inline_queries else 'No'}
🤖 <b>Is Premium:</b> {'Yes' if user.is_premium else 'No'}

For more information about the bot, visit: https://github.com/kareem2099/FreeID
"""

    # Create inline keyboard
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Get My ID", callback_data="myid"),
        InlineKeyboardButton("Get Username", callback_data="username")
    )
    markup.row(
        InlineKeyboardButton("Public Stats", callback_data="publicstats")
    )

    bot.reply_to(message, user_info, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "myid":
        user = call.from_user
        update_user_analytics(user.id, user.username, user.first_name)
        bot.answer_callback_query(call.id, f"Your User ID: {user.id}", show_alert=True)
    elif call.data == "username":
        user = call.from_user
        update_user_analytics(user.id, user.username, user.first_name)
        username = f"@{user.username}" if user.username else "No username set"
        bot.answer_callback_query(call.id, f"Your Username: {username}", show_alert=True)
    elif call.data == "publicstats":
        user = call.from_user
        total_users = users_collection.count_documents({})
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_active = analytics_collection.find_one({'date': today, 'type': 'daily_active_users'})
        today_count = len(today_active['user_ids']) if today_active else 0

        # Recent active users (last 7 days)
        week_ago = today - timedelta(days=7)
        week_active = users_collection.count_documents({'last_interaction': {'$gte': week_ago}})

        # Total interactions
        pipeline = [
            {"$group": {"_id": None, "total_interactions": {"$sum": "$interaction_count"}}}
        ]
        total_interactions_result = list(users_collection.aggregate(pipeline))
        total_interactions = total_interactions_result[0]['total_interactions'] if total_interactions_result else 0

        stats_msg = f"""👥 Total Users: {total_users}
📅 Today Active: {today_count}
📈 Weekly Active: {week_active}
💬 Total Interactions: {total_interactions}"""
        bot.answer_callback_query(call.id, stats_msg, show_alert=True)

@bot.message_handler(commands=['myid'])
def send_my_id(message):
    user = message.from_user
    update_user_analytics(user.id, user.username, user.first_name)
    bot.reply_to(message, f"Your User ID: `{user.id}`", parse_mode='Markdown')

@bot.message_handler(commands=['username'])
def send_username(message):
    user = message.from_user
    update_user_analytics(user.id, user.username, user.first_name)
    username = f"@{user.username}" if user.username else "No username set"
    bot.reply_to(message, f"Your Username: {username}")

@bot.message_handler(commands=['publicstats'])
def get_public_stats(message):
    total_users = users_collection.count_documents({})
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_active = analytics_collection.find_one({'date': today, 'type': 'daily_active_users'})
    today_count = len(today_active['user_ids']) if today_active else 0

    # Recent active users (last 7 days)
    week_ago = today - timedelta(days=7)
    week_active = users_collection.count_documents({'last_interaction': {'$gte': week_ago}})

    # Total interactions
    pipeline = [
        {"$group": {"_id": None, "total_interactions": {"$sum": "$interaction_count"}}}
    ]
    total_interactions_result = list(users_collection.aggregate(pipeline))
    total_interactions = total_interactions_result[0]['total_interactions'] if total_interactions_result else 0

    public_stats_msg = f"""
📊 *Bot Statistics* 📊

👥 *Total Users:* {total_users}
📅 *Today Active Users:* {today_count}
📈 *Weekly Active Users:* {week_active}
💬 *Total Interactions:* {total_interactions}

_Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_
"""
    bot.reply_to(message, public_stats_msg, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def get_stats(message):
    user = message.from_user
    if user.id == ADMIN_USER_ID:
        total_users = users_collection.count_documents({})
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_active = analytics_collection.find_one({'date': today, 'type': 'daily_active_users'})
        today_count = len(today_active['user_ids']) if today_active else 0

        # Recent active users (last 7 days)
        week_ago = today - timedelta(days=7)
        week_active = users_collection.count_documents({'last_interaction': {'$gte': week_ago}})

        # Total interactions
        pipeline = [
            {"$group": {"_id": None, "total_interactions": {"$sum": "$interaction_count"}}}
        ]
        total_interactions_result = list(users_collection.aggregate(pipeline))
        total_interactions = total_interactions_result[0]['total_interactions'] if total_interactions_result else 0

        # Average interactions per user
        avg_interactions = round(total_interactions / total_users, 1) if total_users > 0 else 0

        # Top 5 most active users (by interaction count)
        top_users = list(users_collection.find({}, {'user_id': 1, 'username': 1, 'first_name': 1, 'interaction_count': 1}).sort('interaction_count', -1).limit(5))

        stats_msg = f"""
📊 *Bot Analytics* 📊

👥 *Total Users:* {total_users}
📅 *Today Active Users:* {today_count}
📈 *Weekly Active Users:* {week_active}
💬 *Total Interactions:* {total_interactions}
📊 *Avg Interactions/User:* {avg_interactions}

🔝 *Top 5 Active Users:*
"""

        for i, t_user in enumerate(top_users, 1):
            name = t_user.get('first_name', 'Unknown')
            username = t_user.get('username', 'No username')
            count = t_user.get('interaction_count', 0)
            stats_msg += f"\n{i}. {name} (@{username}) - {count} interactions"

        stats_msg += f"\n\n_Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_"

        # Due to message length limit, if too long, send in parts or truncate
        if len(stats_msg) > 4096:
            stats_parts = []
            current_part = ""
            for line in stats_msg.split('\n'):
                if len(current_part + line + '\n') > 4000:
                    stats_parts.append(current_part)
                    current_part = line
                else:
                    current_part += line + '\n'
            if current_part:
                stats_parts.append(current_part)
            
            for part in stats_parts:
                bot.reply_to(message, part, parse_mode='Markdown')
        else:
            bot.reply_to(message, stats_msg, parse_mode='Markdown')
    else:
        bot.reply_to(message, "This is admin-only. Use /publicstats for public statistics.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user = message.from_user
    update_user_analytics(user.id, user.username, user.first_name)
    bot.reply_to(message, "Use /start to get your info or /myid for ID only, /username for username only.")

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()
