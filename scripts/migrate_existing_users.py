"""
Migration script to mark all existing users as email verified
Run this ONCE to ensure existing users can still log in
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def migrate_existing_users():
    """Mark all existing users as email verified"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    try:
        # Update all users without is_email_verified field
        result = await db["users"].update_many(
            {"is_email_verified": {"$exists": False}},
            {"$set": {"is_email_verified": True}}
        )
        
        print(f"✓ Updated {result.modified_count} existing users to verified status")
        
        # Also set to True for any users that have it set to False but no verification token
        # (in case of partial migration)
        result2 = await db["users"].update_many(
            {
                "is_email_verified": False,
                "verification_token": {"$exists": False}
            },
            {"$set": {"is_email_verified": True}}
        )
        
        print(f"✓ Updated {result2.modified_count} additional users to verified status")
        print("Migration complete!")
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate_existing_users())
