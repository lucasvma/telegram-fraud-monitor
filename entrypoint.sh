#!/bin/bash
set -e

echo "Starting Fraud Monitor Bot..."

echo "Waiting for database to be ready..."
python -c "
import sys
import os
sys.path.append('/app/src')
from database import wait_for_db
try:
    wait_for_db(max_retries=60, initial_delay=1)
    print('Database is ready!')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"

echo "Starting Telegram Bot..."
exec python src/telegram_bot.py