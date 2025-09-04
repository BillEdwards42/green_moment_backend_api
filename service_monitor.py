#!/usr/bin/env python3
"""
Service Monitoring Dashboard for Green Moment Backend
Shows status of all backend services and recent activity
"""

import asyncio
import json
import psycopg2
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from tabulate import tabulate

# Configuration
API_URL = "http://localhost:8000"
DB_CONFIG = "postgresql://postgres:password@localhost:5432/green_moment"
CARBON_DATA_PATH = Path("data/carbon_intensity.json")
LOGS_DIR = Path("logs")

def check_api_server():
    """Check if FastAPI server is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        if response.status_code == 200:
            return "✅ Running", response.json().get("version", "Unknown")
        return "⚠️ Responding but error", f"Status: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ Not running", "Connection refused"
    except Exception as e:
        return "❌ Error", str(e)

def check_database():
    """Check database connection and stats"""
    try:
        conn = psycopg2.connect(DB_CONFIG)
        cur = conn.cursor()
        
        # Get database stats
        cur.execute("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM chores")
        chore_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return "✅ Connected", f"Users: {user_count}, Chores: {chore_count}"
    except Exception as e:
        return "❌ Error", str(e)

def check_carbon_intensity_data():
    """Check carbon intensity data freshness"""
    try:
        with open(CARBON_DATA_PATH, 'r') as f:
            data = json.load(f)
        
        last_updated = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
        if last_updated.tzinfo is None:
            # If no timezone, assume UTC
            last_updated = pytz.UTC.localize(last_updated)
        
        now = datetime.now(pytz.UTC)
        age_minutes = (now - last_updated).total_seconds() / 60
        
        if age_minutes < 15:
            status = "✅ Fresh"
        elif age_minutes < 30:
            status = "⚠️ Slightly stale"
        else:
            status = "❌ Stale"
            
        current_intensity = data.get('current_intensity', {}).get('gCO2e_kWh', 'Unknown')
        
        return status, f"Age: {age_minutes:.1f} min, Current: {current_intensity}g/kWh"
    except FileNotFoundError:
        return "❌ File not found", "No carbon data"
    except Exception as e:
        return "❌ Error", str(e)

def check_log_files():
    """Check recent log activity"""
    log_status = []
    
    log_files = [
        ("notification_scheduler.log", "Notifications"),
        ("carbon_scheduler.log", "Carbon Daily"),
        ("generator.log", "Carbon Generator")
    ]
    
    for log_file, name in log_files:
        log_path = LOGS_DIR / log_file
        if log_path.exists():
            # Get last modified time
            mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
            age_hours = (datetime.now() - mtime).total_seconds() / 3600
            
            # Get last line
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    last_line = lines[-1].strip() if lines else "Empty"
                    # Truncate if too long
                    if len(last_line) > 50:
                        last_line = last_line[:47] + "..."
            except:
                last_line = "Cannot read"
            
            if age_hours < 1:
                status = "✅"
            elif age_hours < 24:
                status = "⚠️"
            else:
                status = "❌"
                
            log_status.append([name, status, f"{age_hours:.1f}h ago", last_line])
        else:
            log_status.append([name, "❌", "Not found", "-"])
    
    return log_status

def check_notification_timing():
    """Check notification scheduling for edwards_test1"""
    try:
        conn = psycopg2.connect(DB_CONFIG)
        cur = conn.cursor()
        
        # Get notification settings
        cur.execute("""
            SELECT ns.scheduled_time, ns.enabled
            FROM notification_settings ns
            JOIN users u ON ns.user_id = u.id
            WHERE u.username = 'edwards_test1'
        """)
        
        result = cur.fetchone()
        if result:
            scheduled_time, enabled = result
            status = "✅ Enabled" if enabled else "❌ Disabled"
            
            # Check recent notifications
            cur.execute("""
                SELECT COUNT(*), MAX(sent_at)
                FROM notification_logs nl
                JOIN users u ON nl.user_id = u.id
                WHERE u.username = 'edwards_test1'
                AND sent_at > NOW() - INTERVAL '24 hours'
            """)
            
            count, last_sent = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if last_sent:
                taipei_tz = pytz.timezone('Asia/Taipei')
                if last_sent.tzinfo is None:
                    last_sent = pytz.UTC.localize(last_sent)
                last_sent_taipei = last_sent.astimezone(taipei_tz)
                details = f"Scheduled: {scheduled_time}, Last 24h: {count}, Last: {last_sent_taipei.strftime('%H:%M')}"
            else:
                details = f"Scheduled: {scheduled_time}, No recent notifications"
                
            return status, details
        else:
            return "❌ No settings", "User not found"
            
    except Exception as e:
        return "❌ Error", str(e)

def main():
    """Display monitoring dashboard"""
    print("\n" + "="*80)
    print(" GREEN MOMENT BACKEND MONITORING DASHBOARD ".center(80))
    print("="*80)
    print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Service Status Table
    print("\n🔧 SERVICE STATUS")
    print("-" * 40)
    
    services = []
    
    # Check each service
    api_status, api_details = check_api_server()
    services.append(["FastAPI Server", api_status, api_details])
    
    db_status, db_details = check_database()
    services.append(["PostgreSQL", db_status, db_details])
    
    carbon_status, carbon_details = check_carbon_intensity_data()
    services.append(["Carbon Data", carbon_status, carbon_details])
    
    print(tabulate(services, headers=["Service", "Status", "Details"], tablefmt="simple"))
    
    # Notification Status
    print("\n📬 NOTIFICATION SYSTEM (edwards_test1)")
    print("-" * 40)
    notif_status, notif_details = check_notification_timing()
    print(f"Status: {notif_status}")
    print(f"Details: {notif_details}")
    
    # Log Files
    print("\n📝 LOG FILES")
    print("-" * 40)
    log_status = check_log_files()
    print(tabulate(log_status, headers=["Log", "Status", "Last Modified", "Last Entry"], tablefmt="simple"))
    
    # Scheduler Information
    print("\n⏰ SCHEDULER INFORMATION")
    print("-" * 40)
    
    taipei_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(taipei_tz)
    
    schedules = [
        ["Carbon Generator", "Every X9 minute", f"Next: :{(now.minute // 10 + 1) * 10 - 1:02d}"],
        ["Notifications", "Every 10 minutes", f"Next: :{(now.minute // 10 + 1) * 10:02d}"],
        ["Daily Carbon", "Daily at 00:00", "Next: Tomorrow 00:00"],
        ["Monthly Promotion", "1st of month 00:00", "Next: Next month 1st"],
    ]
    
    print(tabulate(schedules, headers=["Scheduler", "Schedule", "Next Run"], tablefmt="simple"))
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    if "❌" in api_status:
        recommendations.append("• Start API server: uvicorn app.main:app --reload")
    
    if "❌" in carbon_status or "⚠️" in carbon_status:
        recommendations.append("• Update carbon data: python scripts/carbon_intensity_generator.py --once")
    
    if "❌" in notif_status:
        recommendations.append("• Check notification settings and device tokens")
    
    if not recommendations:
        recommendations.append("✅ All systems operational!")
    
    for rec in recommendations:
        print(rec)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()