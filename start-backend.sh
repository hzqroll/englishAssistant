#!/bin/bash
set -e

echo "🚀 Starting English Transfer Assistant..."

# 1. Start PostgreSQL
echo "📦 Starting PostgreSQL..."
cd /Users/roll/code/english/englishAssistant
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for database to start..."
sleep 5

# Check if database is ready
until docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
  echo "⏳ Waiting for PostgreSQL..."
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# 2. Apply database configuration
echo "🔧 Applying database configuration..."
cd backend
if [ -f .env.backup ]; then
    echo "⚠️  .env.backup exists, skipping backup"
else
    mv .env .env.backup
fi
cp .env.local .env
echo "✅ Database configuration applied"

# 3. Run database migrations
echo "📊 Running database migrations..."
poetry run alembic upgrade head
echo "✅ Migrations completed"

# 4. Restart backend
echo "🔄 Restarting backend..."
pkill -f "uvicorn main:app" || true
sleep 2

echo "✅ Starting backend server..."
echo "📍 Backend will run on http://localhost:8000"
echo "📍 API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

poetry run uvicorn main:app --reload --port 8000
