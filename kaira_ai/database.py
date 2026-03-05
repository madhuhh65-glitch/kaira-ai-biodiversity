import os
from motor.motor_asyncio import AsyncIOMotorClient

# Default to localhost if not specified in env
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_DETAILS)

database = client.biodiversity_ai

def get_user_collection():
    return database.get_collection("users")
