from fastapi import APIRouter, Body, Request
from pymongo import MongoClient
import sqlite3
import base64
import os
from dotenv import load_dotenv

from utils.facial_recognition_module import find_closest_match

load_dotenv()

router = APIRouter()
    
# --- Config ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
SQLITE_DB = os.getenv("SQLITE_DB", "database.db")

# --- MongoDB connection (create ONCE) ---
mongo_client = MongoClient(MONGO_URI)
collection = mongo_client["user_assets"]["profiles"]


@router.post("/login-face")
async def login_face(request: Request, data: dict = Body(...)):
    try:
        # --- 1. Decode incoming image ---
        image_base64 = data["image"]
        image_base64 = image_base64.split(",")[1]
        image_bytes = base64.b64decode(image_base64)

        # --- 2. Load images from MongoDB (LIMIT for speed) ---
        db_images = {}
        for doc in collection.find().limit(2):
            if "uid" in doc and "image_data" in doc:
                db_images[doc["uid"]] = doc["image_data"]

        print("Total images in DB (used):", len(db_images))

        # --- 3. Face matching ---
        matched_uid = find_closest_match(image_bytes, db_images)

        if not matched_uid:
            return {"success": False, "reason": "Face not recognised"}

        # --- 4. Verify user in SQLite ---
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()

        cursor.execute("SELECT uid FROM users WHERE uid = ?", (matched_uid,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {"success": False, "reason": "User not found"}

        # --- 5. Update online status ---
        cursor.execute(
            "UPDATE users SET is_online = 1 WHERE uid = ?",
            (matched_uid,)
        )
        conn.commit()
        conn.close()

        request.session["uid"] = matched_uid

        # --- 6. Success ---
        return {"success": True, "uid": matched_uid}

    except Exception as e:
        print("Error in login_face:", e)
        return {"success": False, "reason": "Internal server error"}