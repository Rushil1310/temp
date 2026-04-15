import csv
import requests # type: ignore
import sqlite3
import pymongo # type: ignore
import os
import sys
from dotenv import load_dotenv # type: ignore

load_dotenv()

# --- Configurations ---
CSV_FILE = os.getenv('CSV_FILE', 'batch_data.csv')
SQLITE_DB = os.getenv('SQLITE_DB', 'database.db')
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = "user_assets"
MONGO_COLLECTION = "profiles"

def setup_databases():
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    # VARCHAR and INT types as specified in requirements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid VARCHAR PRIMARY KEY,
            name VARCHAR,
            elo_rating INT DEFAULT 1200,
            is_online BOOLEAN DEFAULT FALSE
        )
    ''') 
    conn.commit()
    return conn, cursor

def process_sync():
    mode = input("Select Sync Mode: [1] Full (SQL + Mongo) [2] Relational Only (SQL): ").strip()
    sync_mongo = (mode == '1')

    stats = {"sql_success": 0, "mongo_success": 0, "failure": 0}
    sqlite_conn, sqlite_cur = setup_databases()
    
    mongo_collection = None
    if sync_mongo:
        if not MONGO_URI:
            print("Error: MONGO_URI not found in .env")
            return
        mongo_client = pymongo.MongoClient(MONGO_URI)
        mongo_collection = mongo_client[MONGO_DB][MONGO_COLLECTION]

    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                uid, name = row['uid'], row['name']
                base_url = f"https://{row['website_url'].rstrip('/')}"
                target_url = f"{base_url}/images/pfp.jpg"

                # --- 1. SQLITE POPULATION (Always runs) ---
                try:
                    sqlite_cur.execute('''
                        INSERT INTO users (uid, name, elo_rating, is_online)
                        VALUES (?, ?, 1200, FALSE)
                        ON CONFLICT(uid) DO UPDATE SET name=excluded.name
                    ''', (uid, name))
                    stats["sql_success"] += 1
                except Exception as sql_e:
                    print(f"[SQL ERROR] Could not record {uid}: {sql_e}")
                    # We don't 'continue' here because we might still want to try Mongo

                # --- 2. MONGO ASSET HARVESTING (Conditional) ---
                if sync_mongo:
                    try:
                        # Fault Tolerance: handle HTTP 404, timeouts, etc.
                        response = requests.get(target_url, timeout=5)
                        response.raise_for_status() 
                        
                        mongo_collection.update_one(
                            {'uid': uid},
                            {'$set': {
                                'uid': uid,
                                'image_data': response.content
                            }},
                            upsert=True # 
                        )
                        stats["mongo_success"] += 1
                        print(f"[SUCCESS] SQL + Mongo: {uid}")
                    
                    except Exception as mongo_e:
                        stats["failure"] += 1
                        print(f"[MONGO/IMG FAILURE] {uid}: {mongo_e}")
                else:
                    print(f"[SUCCESS] SQL Only: {uid}")

            sqlite_conn.commit()

    finally:
        sqlite_conn.close()
        if sync_mongo: mongo_client.close()

    print(f"\n{'='*30}")
    print("SYNC COMPLETED")
    print(f"SQL Records Processed: {stats['sql_success']}")
    print(f"Mongo Assets Scraped:  {stats['mongo_success']}")
    print(f"Image Fetch Failures:  {stats['failure']}")
    print(f"{'='*30}")

if __name__ == "__main__":
    process_sync()