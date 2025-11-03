#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@gobarberly.com').exists():
    User.objects.create_superuser(
        email='admin@gobarberly.com',
        password='admin123',
        name='Admin User',
        is_super_admin=True
    )
    print('✅ Superuser created successfully')
else:
    print('ℹ️  Superuser already exists')
"

# Create sample data (only if SAMPLE_DATA environment variable is set)
if [ "$LOAD_SAMPLE_DATA" = "true" ]; then
    echo "🌱 Loading sample data..."
    python create_sample_data.py
else
    echo "⏭️  Skipping sample data (set LOAD_SAMPLE_DATA=true to load)"
fi

echo "✅ Build completed successfully!"