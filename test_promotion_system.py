#!/usr/bin/env python3
"""
Test promotion system for league advancement
"""

import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from scripts.carbon_league_promotion import CarbonLeaguePromotion
from app.models.user import User
from app.models.monthly_summary import MonthlySummary

async def test_promotion_system():
    """Test the carbon-based promotion system"""
    
    async with AsyncSessionLocal() as db:
        # Get test user
        result = await db.execute(
            select(User).where(User.username == "edwards_test1")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User edwards_test1 not found")
            return
            
        print(f"✅ Found user: {user.username}")
        print(f"📊 Current status:")
        print(f"  League: {user.current_league}")
        print(f"  Total carbon saved: {user.total_carbon_saved:.2f}g")
        print(f"  Current month carbon: {user.current_month_carbon_saved:.2f}g")
        
        # Check promotion thresholds
        thresholds = {
            'bronze': 100,
            'silver': 500,
            'gold': 700,
            'emerald': 1000,
            'diamond': float('inf')
        }
        
        current_threshold = thresholds.get(user.current_league, 0)
        print(f"\n🎯 Promotion threshold from {user.current_league}: {current_threshold}g CO2e")
        
        if user.current_month_carbon_saved >= current_threshold:
            print(f"✅ User qualifies for promotion! ({user.current_month_carbon_saved:.2f}g >= {current_threshold}g)")
        else:
            print(f"❌ User needs {current_threshold - user.current_month_carbon_saved:.2f}g more for promotion")
        
        # Check last month's summary if exists
        last_month = datetime.now().replace(day=1) - timedelta(days=1)
        result = await db.execute(
            select(MonthlySummary).where(
                MonthlySummary.user_id == user.id,
                MonthlySummary.year == last_month.year,
                MonthlySummary.month == last_month.month
            )
        )
        last_summary = result.scalar_one_or_none()
        
        if last_summary:
            print(f"\n📅 Last month summary ({last_summary.month}/{last_summary.year}):")
            print(f"  Carbon saved: {last_summary.carbon_saved:.2f}g")
            print(f"  League: {last_summary.league}")
            print(f"  Promoted: {last_summary.promoted}")
        
        # Test promotion logic
        print("\n🔄 Testing promotion logic...")
        promotion_service = CarbonLeaguePromotion()
        
        # Simulate checking for promotion
        if user.current_month_carbon_saved >= current_threshold and user.current_league != 'diamond':
            league_order = ['bronze', 'silver', 'gold', 'emerald', 'diamond']
            current_index = league_order.index(user.current_league)
            new_league = league_order[current_index + 1]
            print(f"  → Would promote from {user.current_league} to {new_league}")
        else:
            print(f"  → No promotion (stays in {user.current_league})")

if __name__ == "__main__":
    asyncio.run(test_promotion_system())