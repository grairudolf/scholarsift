#!/bin/bash
# ScholarSift Quick Start Script
echo "🚀 ScholarSift Quick Start"
echo "=========================="

cd "$(dirname "$0")"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the ScholarSift directory"
    exit 1
fi

echo "📦 Installing essential packages..."
pip3 install --break-system-packages flask beautifulsoup4 requests sqlalchemy pandas lxml flask-cors python-dotenv fake-useragent

echo "✅ Testing core functionality..."
python3 test_core.py

echo ""
echo "🎯 Ready to run ScholarSift!"
echo ""
echo "Choose an option:"
echo "1) Run web dashboard only (recommended for testing)"
echo "2) Run scraper to get real scholarship data"
echo "3) Run both (scraper + dashboard)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🌐 Starting web dashboard..."
        echo "Visit: http://localhost:5000"
        echo "Press Ctrl+C to stop"
        cd dashboard && python3 app.py
        ;;
    2)
        echo "🔍 Running scholarship scraper..."
        python3 main.py --scrape
        ;;
    3)
        echo "🚀 Starting both scraper and dashboard..."
        echo "1. Scraper will run first to get data"
        echo "2. Dashboard will start automatically"
        echo ""
        echo "Scraping scholarships..."
        python3 main.py --scrape

        echo ""
        echo "🌐 Starting dashboard..."
        echo "Visit: http://localhost:5000"
        echo "Press Ctrl+C to stop"
        cd dashboard && python3 app.py
        ;;
    *)
        echo "❌ Invalid choice. Please run again and select 1-3"
        exit 1
        ;;
esac
