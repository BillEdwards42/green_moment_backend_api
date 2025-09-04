from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import List

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.monthly_summary import MonthlySummary
from app.models.daily_carbon_progress import DailyCarbonProgress


def get_next_league(current_league: str) -> str:
    """Get the next league in progression"""
    league_hierarchy = ["bronze", "silver", "gold", "emerald", "diamond"]
    try:
        current_index = league_hierarchy.index(current_league)
        if current_index < len(league_hierarchy) - 1:
            return league_hierarchy[current_index + 1]
    except ValueError:
        pass
    return current_league

router = APIRouter()


@router.get("/summary")
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's progress summary including carbon (CO2e) saved and league info"""
    # Get last month's summary
    last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
    last_year = datetime.now().year if datetime.now().month > 1 else datetime.now().year - 1
    
    result = await db.execute(
        select(MonthlySummary).where(
            and_(
                MonthlySummary.user_id == current_user.id,
                MonthlySummary.month == last_month,
                MonthlySummary.year == last_year
            )
        )
    )
    last_month_summary = result.scalar_one_or_none()
    
    # Also check current month for recent promotions (for testing or early month promotions)
    current_month_result = await db.execute(
        select(MonthlySummary).where(
            and_(
                MonthlySummary.user_id == current_user.id,
                MonthlySummary.month == datetime.now().month,
                MonthlySummary.year == datetime.now().year
            )
        )
    )
    current_month_summary = current_month_result.scalar_one_or_none()
    
    return {
        "username": current_user.username,
        "current_league": current_user.current_league,
        "total_co2e_saved_g": current_user.total_carbon_saved,  # Now in grams
        "current_month_co2e_saved_g": current_user.current_month_carbon_saved,  # In grams
        "last_month_co2e_saved_g": last_month_summary.total_carbon_saved if last_month_summary else None,  # In grams
        "should_show_league_upgrade": (
            (current_month_summary.league_upgraded if current_month_summary else False) or
            (last_month_summary.league_upgraded if last_month_summary else False)
        )
    }


@router.get("/daily-carbon")
async def get_daily_carbon(
    date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get carbon saved for a specific date"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    result = await db.execute(
        select(DailyCarbonProgress).where(
            and_(
                DailyCarbonProgress.user_id == current_user.id,
                DailyCarbonProgress.date == target_date
            )
        )
    )
    daily_progress = result.scalar_one_or_none()
    
    if daily_progress:
        return {
            "date": target_date.isoformat(),
            "carbon_saved": daily_progress.daily_carbon_saved,
            "cumulative_carbon_saved": daily_progress.cumulative_carbon_saved
        }
    else:
        return {
            "date": target_date.isoformat(),
            "carbon_saved": 0.0,
            "cumulative_carbon_saved": 0.0
        }


@router.get("/league")
async def get_league_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's league information and standings"""
    # Get league standings - users in same league sorted by carbon saved
    result = await db.execute(
        select(User).where(
            and_(
                User.current_league == current_user.current_league,
                User.deleted_at.is_(None)
            )
        ).order_by(User.current_month_carbon_saved.desc())
    )
    league_users = result.scalars().all()
    
    standings = [
        {
            "username": user.username,
            "carbon_saved": user.current_month_carbon_saved,
            "league": user.current_league
        }
        for user in league_users
    ]
    
    # Find user's rank
    user_rank = next((i + 1 for i, u in enumerate(standings) if u["username"] == current_user.username), None)
    
    return {
        "current_league": current_user.current_league,
        "next_league": get_next_league(current_user.current_league),
        "user_rank": user_rank,
        "top_users": standings[:10]  # Top 10 users in the league
    }


@router.post("/mark-league-upgrade-shown")
async def mark_league_upgrade_shown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark that the league upgrade animation has been shown"""
    # Check both current and last month for the upgrade flag
    summaries_to_check = []
    
    # Current month
    current_result = await db.execute(
        select(MonthlySummary).where(
            and_(
                MonthlySummary.user_id == current_user.id,
                MonthlySummary.month == datetime.now().month,
                MonthlySummary.year == datetime.now().year,
                MonthlySummary.league_upgraded == True
            )
        )
    )
    current_summary = current_result.scalar_one_or_none()
    if current_summary:
        summaries_to_check.append(current_summary)
    
    # Last month
    last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
    last_year = datetime.now().year if datetime.now().month > 1 else datetime.now().year - 1
    
    last_result = await db.execute(
        select(MonthlySummary).where(
            and_(
                MonthlySummary.user_id == current_user.id,
                MonthlySummary.month == last_month,
                MonthlySummary.year == last_year,
                MonthlySummary.league_upgraded == True
            )
        )
    )
    last_summary = last_result.scalar_one_or_none()
    if last_summary:
        summaries_to_check.append(last_summary)
    
    # Mark all as shown
    for summary in summaries_to_check:
        summary.league_upgraded = False
    
    if summaries_to_check:
        await db.commit()
    
    return {"success": True}