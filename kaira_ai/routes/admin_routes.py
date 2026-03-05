from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import UserResponse, UserRole
from database import get_user_collection
from auth import get_current_admin_user
from bson import ObjectId

router = APIRouter()

# --- ADMIN ENDPOINTS ---

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_admin_user)):
    """
    Get all registered users. Admin access only.
    """
    users_collection = get_user_collection()
    users_cursor = users_collection.find({})
    users = await users_cursor.to_list(length=1000)
    return users

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_admin_user)):
    """
    Delete a user by ID. Admin access only.
    """
    users_collection = get_user_collection()
    try:
        oid = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
        
    result = await users_collection.delete_one({"_id": oid})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": "User deleted successfully"}

@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(get_current_admin_user)):
    """
    Get system statistics. Admin access only.
    """
    users_collection = get_user_collection()
    user_count = await users_collection.count_documents({})
    
    # Count species from dataset.csv
    import os
    import csv
    
    species_count = 0
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "dataset.csv")
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                species_count = sum(1 for row in reader if row and row[0] != "Unknown") # Count Valid Species
    except Exception as e:
        print(f"Error reading dataset.csv: {e}")

    return {
        "total_users": user_count,
        "species_logs": species_count, 
        "active_models": 1, 
        "server_status": "Operational",
        "system_load": "Low"
    }
