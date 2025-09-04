#!/usr/bin/env python3
"""
Test notification timing for edwards_test1 user
Checks if notifications are being delayed
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytz

sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import User, NotificationSettings, NotificationLog

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check_notification_timing():
    """Check edwards_test1 notification schedule and recent logs"""
    
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            select(User).where(User.username == "edwards_test1")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User edwards_test1 not found")
            return
            
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Get notification settings
        result = await db.execute(
            select(NotificationSettings).where(NotificationSettings.user_id == user.id)
        )
        settings = result.scalar_one_or_none()
        
        if settings:
            print(f"\n📅 Notification Settings:")
            print(f"  Enabled: {settings.enabled}")
            print(f"  Scheduled Time: {settings.scheduled_time}")
            print(f"  Daily Recommendation: {settings.daily_recommendation}")
        else:
            print("❌ No notification settings found")
            
        # Get recent notification logs
        result = await db.execute(
            select(NotificationLog)
            .where(NotificationLog.user_id == user.id)
            .order_by(NotificationLog.sent_at.desc())
            .limit(10)
        )
        logs = result.scalars().all()
        
        taipei_tz = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(taipei_tz)
        
        print(f"\n🕐 Current Time (Taipei): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if logs:
            print(f"\n📬 Recent Notification Logs (Last 10):")
            for log in logs:
                # Convert to Taipei time if needed
                sent_time = log.sent_at
                if sent_time.tzinfo is None:
                    sent_time = pytz.UTC.localize(sent_time)
                sent_time_taipei = sent_time.astimezone(taipei_tz)
                
                # Calculate delay if scheduled time exists
                if settings and settings.scheduled_time:
                    scheduled_hour, scheduled_min = map(int, settings.scheduled_time.split(':'))
                    scheduled_dt = sent_time_taipei.replace(hour=scheduled_hour, minute=scheduled_min, second=0, microsecond=0)
                    
                    # If notification was sent before scheduled time, it might be from previous day
                    if sent_time_taipei.time() < scheduled_dt.time():
                        scheduled_dt -= timedelta(days=1)
                    
                    delay = sent_time_taipei - scheduled_dt
                    delay_minutes = int(delay.total_seconds() / 60)
                    
                    print(f"  {sent_time_taipei.strftime('%Y-%m-%d %H:%M:%S')} - Status: {log.status}")
                    print(f"    Expected: {scheduled_dt.strftime('%H:%M')}, Actual: {sent_time_taipei.strftime('%H:%M')}")
                    print(f"    Delay: {delay_minutes} minutes")
                    if log.error_message:
                        print(f"    Error: {log.error_message}")
                else:
                    print(f"  {sent_time_taipei.strftime('%Y-%m-%d %H:%M:%S')} - Status: {log.status}")
        else:
            print("\n❌ No notification logs found")
            
        # Check if notification should have been sent today
        if settings and settings.enabled and settings.scheduled_time:
            scheduled_hour, scheduled_min = map(int, settings.scheduled_time.split(':'))
            today_scheduled = current_time.replace(hour=scheduled_hour, minute=scheduled_min, second=0, microsecond=0)
            
            if current_time > today_scheduled:
                # Check if notification was sent today
                today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                result = await db.execute(
                    select(NotificationLog)
                    .where(
                        NotificationLog.user_id == user.id,
                        NotificationLog.sent_at >= today_start
                    )
                )
                today_logs = result.scalars().all()
                
                if not today_logs:
                    time_since = current_time - today_scheduled
                    print(f"\n⚠️  WARNING: Notification was scheduled for {settings.scheduled_time} today")
                    print(f"   but hasn't been sent yet ({int(time_since.total_seconds()/60)} minutes overdue)")
                    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_notification_timing())