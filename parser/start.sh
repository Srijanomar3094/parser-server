#!/bin/bash

echo "🚀 Starting Contract Intelligence Parser Backend"
echo "================================================"

# Check if MongoDB is running
echo "🔍 Checking MongoDB connection..."
if ! python test_mongodb.py; then
    echo "❌ MongoDB connection failed. Starting MongoDB with Docker..."
    
    # Start MongoDB if not running
    if ! docker ps | grep -q "parser_mongodb"; then
        echo "🐳 Starting MongoDB container..."
        docker-compose up -d db
        
        # Wait for MongoDB to be ready
        echo "⏳ Waiting for MongoDB to be ready..."
        sleep 10
    fi
fi

# Install dependencies if needed
if [ ! -d "penv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv penv
fi

echo "🔧 Activating virtual environment..."
source penv/bin/activate

echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "👤 Creating superuser if needed..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

echo "🌐 Starting Django development server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "🔑 Admin interface: http://localhost:8000/admin"
echo "📚 API endpoints: http://localhost:8000/contracts"

python manage.py runserver 0.0.0.0:8000

