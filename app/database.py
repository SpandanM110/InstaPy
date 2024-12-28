# app/database.py

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "instagram")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

logger = logging.getLogger("app.database")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


async def init_db():
    # Create indexes
    await db.users.create_index([("username", ASCENDING)], unique=True)
    await db.users.create_index([("email", ASCENDING)], unique=True)
    await db.posts.create_index([("hashtags", ASCENDING)])
    await db.posts.create_index([("category", ASCENDING)])
    await db.posts.create_index([("created_at", DESCENDING)])
    await db.posts.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await db.likes.create_index([("post_id", ASCENDING)])
    await db.likes.create_index([("user_id", ASCENDING)])
    await db.comments.create_index([("post_id", ASCENDING)])
    await db.comments.create_index([("user_id", ASCENDING)])
    logger.info("All indexes created successfully.")


def get_database():
    return db
