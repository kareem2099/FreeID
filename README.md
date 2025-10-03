# FreeID Telegram Bot

A simple Telegram bot that helps users easily get their username and user ID, along with other user information. Includes analytics to track usage and user engagement.

## Features

- Get comprehensive user information with `/start` or `/help`
- Get User ID only with `/myid`
- Get Username only with `/username`
- Public statistics with `/publicstats` (visible to all users)
- Detailed analytics with `/stats` (owner only)
- MongoDB-based analytics for tracking users and interactions
- Fetches all available user data from Telegram API

## Setup

1. Create a new bot with [BotFather](https://t.me/botfather) on Telegram
2. Get the bot token
3. Set up MongoDB database (or use provided URI)
4. Create `.env` file with the following variables:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   MONGODB_URI=your_mongodb_uri
   MONGODB_BOT_DB_NAME=FreeIDanalytics
   ADMIN_USER_ID=your_telegram_user_id
   ```
5. Install dependencies: `pip install -r requirements.txt`
6. Run the bot: `python3 bot.py`

## Usage

- Start the bot and send `/start` to get your info and interactive buttons
- Interactive buttons available in /start message for quick access
- Use `/myid` for user ID only
- Use `/username` for username only
- Use `/publicstats` to view public statistics
- Use `/stats` to view detailed analytics (admin only)

## Analytics

The bot automatically tracks:
- Total unique users
- Daily active users
- Weekly active users
- User interaction counts
- Last interaction timestamps

Data is stored in MongoDB for persistent storage and analysis.

## Data Fetched

- First Name
- Last Name
- Username
- User ID
- Language Code
- Bot Status
- Permissions (join groups, read messages, inline queries)
- Premium Status

## License

MIT
