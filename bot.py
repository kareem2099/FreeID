import logging
import sys
import time
import telebot
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException

from config import load_config
from database import DatabaseManager
from handlers import setup_handlers

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        # Uncomment to also log to file
        # logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

# Load configuration and validate
try:
    config = load_config()
    logger.info("Configuration loaded successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)

# Initialize database
try:
    db_manager = DatabaseManager(config.mongodb_uri, config.mongodb_bot_db_name)
    logger.info("Database connection established")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    sys.exit(1)

# Initialize bot
bot = telebot.TeleBot(config.telegram_bot_token)

# Set up handlers
setup_handlers(bot, db_manager, config)

if __name__ == '__main__':
    try:
        logger.info("Bot is starting...")
        while True:
            try:
                bot.polling(timeout=30, interval=2)
                break  # Polling exited normally (rare)
            except ApiTelegramException as e:
                if e.error_code == 429:
                    retry_after = e.result.get('parameters', {}).get('retry_after', 5)
                    logger.warning(f"Rate limited by Telegram API. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                else:
                    logger.error(f"Telegram API error (code {e.error_code}): {e.description}")
                    time.sleep(10)  # Retry after a short delay for other API errors
            except KeyboardInterrupt:
                logger.info("Received interrupt, stopping bot gracefully.")
                break
            except Exception as e:
                logger.error(f"Unexpected polling error: {e}")
                time.sleep(10)  # Wait before retrying on unknown errors
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        db_manager.close()
        logger.info("Database connection closed")
