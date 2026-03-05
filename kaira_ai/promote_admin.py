import asyncio
from database import get_user_collection
import os

# Ensure we can import properly
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "kaira ai"))

# Mocking the database connection since we are running outside main app
# We need to make sure 'database.py' is importable.
# Moving this script to 'kaira ai' folder is better.

async def promote_to_admin(email):
    users_collection = get_user_collection()
    user = await users_collection.find_one({"email": email})
    
    if not user:
        print(f"Error: User with email {email} not found.")
        return

    result = await users_collection.update_one(
        {"email": email},
        {"$set": {"role": "admin"}}
    )
    
    if result.modified_count > 0:
        print(f"SUCCESS: User {email} is now an ADMIN.")
    else:
        print(f"User {email} was already an admin or update failed.")

if __name__ == "__main__":
    import argparse
    # Hardcoding for simplicity in this env
    target_email = "madhu@gmail.com" 
    
    print(f"Promoting {target_email} to Admin...")
    asyncio.run(promote_to_admin(target_email))
