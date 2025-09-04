#!/usr/bin/env python3
"""
Run notification scheduler every 10 minutes at X0 (00, 10, 20, 30, 40, 50)
Fixed version v2 - Prevents time drift by calculating exact run times
"""

import time
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path

# Change to backend API directory (parent of scripts)
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)

# Log file
log_file = Path("logs/notification_runner.log")
log_file.parent.mkdir(exist_ok=True)


def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    with open(log_file, "a") as f:
        f.write(log_entry + "\n")


def run_notification_scheduler():
    """Run the notification scheduler script"""
    try:
        log_message("Starting notification scheduler...")
        
        # Run the fixed scheduler from the backend directory
        result = subprocess.run(
            ["python3", "scripts/notification_scheduler_fixed.py"],
            capture_output=True,
            text=True,
            check=True,
            cwd=backend_dir  # Ensure we're in the right directory
        )
        
        if result.stdout:
            log_message(f"Scheduler output: {result.stdout}")
        
        if result.stderr:
            log_message(f"Scheduler errors: {result.stderr}")
            
        log_message("Notification scheduler completed successfully")
        
    except subprocess.CalledProcessError as e:
        log_message(f"ERROR: Notification scheduler failed with exit code {e.returncode}")
        log_message(f"STDOUT: {e.stdout}")
        log_message(f"STDERR: {e.stderr}")
        
    except Exception as e:
        log_message(f"ERROR: Unexpected error running notification scheduler: {e}")


def get_next_run_time():
    """Calculate the next X0 minute mark (00, 10, 20, 30, 40, 50)"""
    now = datetime.now()
    current_minute = now.minute
    
    # Calculate minutes until next X0
    next_minute = ((current_minute // 10) + 1) * 10
    if next_minute >= 60:
        next_minute = 0
    
    # Calculate the exact next run time
    next_run = now.replace(second=0, microsecond=0)
    
    if next_minute == 0:
        # Next hour
        next_run = next_run.replace(minute=0) + timedelta(hours=1)
    elif next_minute > current_minute:
        # Later this hour
        next_run = next_run.replace(minute=next_minute)
    else:
        # We're already at X0, so schedule for 10 minutes from now
        next_run = next_run.replace(minute=((current_minute // 10) * 10)) + timedelta(minutes=10)
        if next_run.minute >= 60:
            next_run = next_run.replace(minute=0) + timedelta(hours=1)
    
    return next_run


def main():
    """Main scheduler loop with drift prevention"""
    log_message("=" * 60)
    log_message("Notification Scheduler Runner Started (Fixed v2 - No Drift)")
    log_message(f"Working directory: {os.getcwd()}")
    log_message(f"Will run every 10 minutes at X0 (00, 10, 20, 30, 40, 50)")
    log_message("=" * 60)
    
    # Run once at startup if we're within 5 seconds of X0
    now = datetime.now()
    if now.minute % 10 == 0 and now.second < 5:
        log_message("Running immediately (at X0 minute mark)")
        run_notification_scheduler()
    
    while True:
        # Calculate exact time until next run
        next_run = get_next_run_time()
        now = datetime.now()
        sleep_seconds = (next_run - now).total_seconds()
        
        if sleep_seconds > 0:
            log_message(f"Next run scheduled for {next_run.strftime('%H:%M:%S')} (in {sleep_seconds:.0f} seconds)")
            
            # Sleep until just before the target time, then do precise timing
            if sleep_seconds > 1:
                time.sleep(sleep_seconds - 0.5)
            
            # Wait for exact time
            while datetime.now() < next_run:
                time.sleep(0.1)
        
        # Run the scheduler at the exact time
        run_notification_scheduler()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("\nNotification scheduler runner stopped by user")
    except Exception as e:
        log_message(f"\nFATAL ERROR: {e}")
        raise