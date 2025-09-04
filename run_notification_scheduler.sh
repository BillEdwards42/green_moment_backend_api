#!/bin/bash
# Notification scheduler runner - runs every 10 minutes

echo "Starting notification scheduler (runs every 10 minutes)..."
echo "Press Ctrl+C to stop"

while true; do
    echo ""
    echo "=========================================="
    echo "Running notification check at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    
    python scripts/notification_scheduler_fixed.py
    
    echo "Waiting 10 minutes until next check..."
    sleep 600
done