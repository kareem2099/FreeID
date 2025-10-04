from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, mongo_uri: str, db_name: str):
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.users_collection: Collection = self.db['users']
            self.analytics_collection: Collection = self.db['analytics']
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def update_user_analytics(self, user_id: int, username: Optional[str], first_name: Optional[str]):
        """Update user analytics on interaction."""
        try:
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_interaction': datetime.now(timezone.utc)
            }

            # Insert or update user
            self.users_collection.update_one(
                {'user_id': user_id},
                {
                    '$set': user_data,
                    '$inc': {'interaction_count': 1}
                },
                upsert=True
            )

            # Daily active users analytics
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            self.analytics_collection.update_one(
                {'date': today, 'type': 'daily_active_users'},
                {'$addToSet': {'user_ids': user_id}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating user analytics for user {user_id}: {e}")

    def get_bot_stats(self) -> Dict[str, int]:
        """Get comprehensive bot statistics."""
        try:
            total_users = self.users_collection.count_documents({})

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_active_doc = self.analytics_collection.find_one({'date': today, 'type': 'daily_active_users'})
            today_count = len(today_active_doc.get('user_ids', [])) if today_active_doc else 0

            # Recent active users (last 7 days)
            week_ago = today - timedelta(days=7)
            week_active = self.users_collection.count_documents({'last_interaction': {'$gte': week_ago}})

            # Total interactions
            pipeline = [
                {"$group": {"_id": None, "total_interactions": {"$sum": "$interaction_count"}}}
            ]
            total_interactions_result = list(self.users_collection.aggregate(pipeline))
            total_interactions = total_interactions_result[0]['total_interactions'] if total_interactions_result else 0

            return {
                'total_users': total_users,
                'today_active': today_count,
                'week_active': week_active,
                'total_interactions': total_interactions,
                'avg_interactions': round(total_interactions / total_users, 1) if total_users > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {
                'total_users': 0,
                'today_active': 0,
                'week_active': 0,
                'total_interactions': 0,
                'avg_interactions': 0
            }

    def get_top_users(self, limit: int = 5) -> List[Dict]:
        """Get top users by interaction count."""
        try:
            top_users = list(self.users_collection.find(
                {},
                {'user_id': 1, 'username': 1, 'first_name': 1, 'interaction_count': 1}
            ).sort('interaction_count', -1).limit(limit))
            return top_users
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []

    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
