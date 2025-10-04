import logging
from datetime import datetime, timezone
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telebot import TeleBot
    from database import DatabaseManager
    from config import Config

logger = logging.getLogger(__name__)


def setup_handlers(bot: 'TeleBot', db: 'DatabaseManager', config: 'Config'):
    """Set up all bot message and callback handlers."""

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        user = message.from_user
        try:
            db.update_user_analytics(user.id, user.username, user.first_name)
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
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("Get My ID", callback_data="myid"),
                InlineKeyboardButton("Get Username", callback_data="username")
            )
            markup.row(
                InlineKeyboardButton("Public Stats", callback_data="publicstats")
            )
            bot.reply_to(message, user_info, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            logger.error(f"Error in send_welcome for user {user.id}: {e}")
            bot.reply_to(message, "Sorry, an error occurred while processing your request.")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        user = call.from_user
        try:
            db.update_user_analytics(user.id, user.username, user.first_name)
            if call.data == "myid":
                bot.answer_callback_query(call.id, f"Your User ID: {user.id}", show_alert=True)
            elif call.data == "username":
                username = f"@{user.username}" if user.username else "No username set"
                bot.answer_callback_query(call.id, f"Your Username: {username}", show_alert=True)
            elif call.data == "publicstats":
                stats = db.get_bot_stats()
                stats_msg = (
                    f"👥 Total Users: {stats['total_users']}\n"
                    f"📅 Today Active: {stats['today_active']}\n"
                    f"📈 Weekly Active: {stats['week_active']}\n"
                    f"💬 Total Interactions: {stats['total_interactions']}"
                )
                bot.answer_callback_query(call.id, stats_msg, show_alert=True)
        except Exception as e:
            logger.error(f"Error in handle_callback for user {user.id}: {e}")
            bot.answer_callback_query(call.id, "An error occurred while processing your request.")

    @bot.message_handler(commands=['myid'])
    def send_my_id(message):
        user = message.from_user
        try:
            db.update_user_analytics(user.id, user.username, user.first_name)
            bot.reply_to(message, f"Your User ID: `{user.id}`", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in send_my_id for user {user.id}: {e}")
            bot.reply_to(message, "Sorry, an error occurred.")

    @bot.message_handler(commands=['username'])
    def send_username(message):
        user = message.from_user
        try:
            db.update_user_analytics(user.id, user.username, user.first_name)
            username = f"@{user.username}" if user.username else "No username set"
            bot.reply_to(message, f"Your Username: {username}")
        except Exception as e:
            logger.error(f"Error in send_username for user {user.id}: {e}")
            bot.reply_to(message, "Sorry, an error occurred.")

    @bot.message_handler(commands=['publicstats'])
    def get_public_stats(message):
        user = message.from_user
        try:
            db.update_user_analytics(user.id, user.username, user.first_name)
            stats = db.get_bot_stats()
            public_stats_msg = f"""
📊 *Bot Statistics* 📊

👥 *Total Users:* {stats['total_users']}
📅 *Today Active Users:* {stats['today_active']}
📈 *Weekly Active Users:* {stats['week_active']}
💬 *Total Interactions:* {stats['total_interactions']}

_Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_
"""
            bot.reply_to(message, public_stats_msg, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in get_public_stats for user {user.id}: {e}")
            bot.reply_to(message, "Sorry, an error occurred while fetching statistics.")

    @bot.message_handler(commands=['stats'])
    def get_stats(message):
        user = message.from_user
        try:
            if user.id != config.admin_user_id:
                bot.reply_to(message, "This is admin-only. Use /publicstats for public statistics.")
                return

            db.update_user_analytics(user.id, user.username, user.first_name)
            stats = db.get_bot_stats()
            top_users = db.get_top_users()

            stats_msg = f"""
📊 *Bot Analytics* 📊

👥 *Total Users:* {stats['total_users']}
📅 *Today Active Users:* {stats['today_active']}
📈 *Weekly Active Users:* {stats['week_active']}
💬 *Total Interactions:* {stats['total_interactions']}
📊 *Avg Interactions/User:* {stats['avg_interactions']}

🔝 *Top 5 Active Users:*
"""
            for i, t_user in enumerate(top_users, 1):
                name = t_user.get('first_name', 'Unknown')
                username = t_user.get('username', 'No username')
                count = t_user.get('interaction_count', 0)
                stats_msg += f"\n{i}. {name} (@{username}) - {count} interactions"

            stats_msg += f"\n\n_Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_"

            bot.reply_to(message, stats_msg, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in get_stats for user {user.id}: {e}")
            bot.reply_to(message, "Sorry, an error occurred while fetching admin statistics.")

    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        user = message.from_user
        try:
            db.update_user_analytics(user.id, user.username, user.first_name)
            bot.reply_to(message, "Use /start to get your info or /myid for ID only, /username for username only.")
        except Exception as e:
            logger.error(f"Error in echo_all for user {user.id}: {e}")
