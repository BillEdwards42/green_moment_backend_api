#!/usr/bin/env python3
"""
Verify that task tables and columns are removed
"""
import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal


async def verify_removal():
    """Verify that task tables and columns are removed"""
    print("🔍 Verifying task removal...")
    
    results = []
    
    async with AsyncSessionLocal() as db:
        # Check if tables exist
        try:
            await db.execute(text("SELECT 1 FROM tasks LIMIT 1"))
            results.append(("❌", "tasks table still exists!"))
        except:
            results.append(("✅", "tasks table removed"))
        
        try:
            await db.execute(text("SELECT 1 FROM user_tasks LIMIT 1"))
            results.append(("❌", "user_tasks table still exists!"))
        except:
            results.append(("✅", "user_tasks table removed"))
        
        # Check if columns exist
        try:
            await db.execute(text("SELECT current_month_tasks_completed FROM users LIMIT 1"))
            results.append(("❌", "current_month_tasks_completed column still exists!"))
        except:
            results.append(("✅", "current_month_tasks_completed column removed"))
        
        try:
            await db.execute(text("SELECT tasks_completed FROM monthly_summaries LIMIT 1"))
            results.append(("❌", "tasks_completed column still exists!"))
        except:
            results.append(("✅", "tasks_completed column removed"))
        
        try:
            await db.execute(text("SELECT total_points_earned FROM monthly_summaries LIMIT 1"))
            results.append(("❌", "total_points_earned column still exists!"))
        except:
            results.append(("✅", "total_points_earned column removed"))
    
    # Print results
    print("\nVerification Results:")
    print("=" * 50)
    all_good = True
    for status, message in results:
        print(f"{status} {message}")
        if status == "❌":
            all_good = False
    
    if all_good:
        print("\n✅ All task-related tables and columns successfully removed!")
    else:
        print("\n❌ Some items were not removed. Please check the migration.")
    
    return all_good


if __name__ == "__main__":
    success = asyncio.run(verify_removal())
    sys.exit(0 if success else 1)