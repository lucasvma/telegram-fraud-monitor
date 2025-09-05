#!/bin/bash
set -euo pipefail

echo "🛡️ Starting secure deployment of Fraud Monitor Bot..."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_status "Creating .env from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual credentials before continuing!"
    exit 1
fi

print_status "Validating environment variables..."

source .env

required_vars=("TELEGRAM_BOT_TOKEN" "DB_PASS" "DB_USER" "DB_NAME")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        print_error "Required environment variable $var is not set!"
        exit 1
    fi
done

if [ ${#DB_PASS} -lt 16 ]; then
    print_error "Database password must be at least 16 characters long!"
    exit 1
fi

if [ ${#TELEGRAM_BOT_TOKEN} -lt 40 ]; then
    print_error "Invalid Telegram bot token format!"
    exit 1
fi

print_status "Environment validation passed"

print_status "Creating logs directory..."
mkdir -p logs
chmod 755 logs

print_status "Checking for potential secrets in git..."
if git check-ignore .env >/dev/null 2>&1; then
    print_status ".env file is properly ignored by git"
else
    print_warning ".env file might not be ignored by git!"
fi

print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

print_status "Waiting for services to be healthy..."
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose ps | grep -q "healthy"; then
        print_status "Services are healthy"
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    print_error "Services failed to become healthy within $timeout seconds"
    docker-compose logs
    exit 1
fi

print_status "Deployment completed successfully!"
print_status "Checking service status..."
docker-compose ps

print_status "Recent logs:"
docker-compose logs --tail=20

print_warning "Security Reminders:"
echo "  • Never commit .env file to version control"
echo "  • Regularly rotate your database password"
echo "  • Monitor logs for suspicious activity"
echo "  • Keep Docker images updated"
echo "  • Review access logs regularly"

print_status "Bot is now running securely!"