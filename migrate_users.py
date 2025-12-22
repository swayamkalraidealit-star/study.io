"""
Simple migration to mark existing users as verified
Run this file directly: python3 migrate_users.py
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def migrate():
    """Mark all existing users as email verified"""
    print("🔄 Starting migration...")
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    try:
        # Count users without is_email_verified field
        count = await db["users"].count_documents({"is_email_verified": {"$exists": False}})
        print(f"📊 Found {count} users without verification status")
        
        # Update all users without is_email_verified field
        result = await db["users"].update_many(
            {"is_email_verified": {"$exists": False}},
            {"$set": {"is_email_verified": True}}
        )
        
        print(f"✅ Updated {result.modified_count} users to verified status")
        
        # Also check for users with False but no token
        result2 = await db["users"].update_many(
            {
                "is_email_verified": False,
                "verification_token": {"$exists": False}
            },
            {"$set": {"is_email_verified": True}}
        )
        
        if result2.modified_count > 0:
            print(f"✅ Updated {result2.modified_count} additional users")
        
        print("✨ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate())
