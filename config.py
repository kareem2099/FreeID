import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    telegram_bot_token: str
    mongodb_uri: str
    mongodb_bot_db_name: str
    admin_user_id: int

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.telegram_bot_token or self.telegram_bot_token == 'YOUR_BOT_TOKEN':
            raise ValueError("TELEGRAM_BOT_TOKEN must be set in environment variables")
        if not self.mongodb_uri:
            raise ValueError("MONGODB_URI must be set in environment variables")
        if not self.mongodb_bot_db_name:
            self.mongodb_bot_db_name = 'FreeID'
        if self.admin_user_id == 0:
            raise ValueError("ADMIN_USER_ID must be set in environment variables")


def load_config() -> Config:
    return Config(
        telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
        mongodb_uri=os.getenv('MONGODB_URI', ''),
        mongodb_bot_db_name=os.getenv('MONGODB_BOT_DB_NAME', 'FreeID'),
        admin_user_id=int(os.getenv('ADMIN_USER_ID', '0'))
    )
