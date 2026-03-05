import asyncio
from database import get_user_collection
from auth import get_password_hash
from models import UserRole
import os
import sys

# Ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), "kaira ai"))

async def create_admin():
    users_collection = get_user_collection()
    
    email = "admin@kaira.ai"
    password = "admin123"
    hashed_password = get_password_hash(password)
    
    user_data = {
        "name": "Kaira Administrator",
        "email": email,
        "password": hashed_password,
        "role": UserRole.ADMIN,
        "profile_image": None
    }
    
    # Check if exists
    existing_user = await users_collection.find_one({"email": email})
    if existing_user:
        print(f"User {email} already exists. Updating role and password...")
        await users_collection.update_one(
            {"email": email},
            {"$set": {"role": UserRole.ADMIN, "password": hashed_password}}
        )
    else:
        print(f"Creating new Admin user: {email}")
        await users_collection.insert_one(user_data)
        
    print("\n✅ Admin Account Ready!")
    print(f"Email: {email}")
    print(f"Password: {password}")

if __name__ == "__main__":
    asyncio.run(create_admin())
