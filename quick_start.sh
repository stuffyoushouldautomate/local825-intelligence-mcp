#!/bin/bash

# DataPilotPlus Scraper Quick Start Script
# This script will set up and launch the comprehensive scraper

echo "🚀 DataPilotPlus Intelligence Scraper - Quick Start"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your credentials."
    echo "   See README.md for configuration details."
    exit 1
fi

# Check if MySQL credentials are configured
if ! grep -q "MYSQL_USERNAME" .env || ! grep -q "MYSQL_PASSWORD" .env; then
    echo "⚠️  MySQL credentials not configured in .env file."
    echo "   Please add your MySQL username and password."
    exit 1
fi

# Setup database
echo "🗄️  Setting up database..."
python setup_database.py

if [ $? -ne 0 ]; then
    echo "❌ Database setup failed. Please check your MySQL credentials."
    exit 1
fi

echo "✅ Database setup completed!"

# Ask user what they want to run
echo ""
echo "What would you like to run?"
echo "1. Full Application (Scraper + MCP Server)"
echo "2. MCP Server Only"
echo "3. Scraper Only"
echo "4. Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting full DataPilotPlus application..."
        echo "   - Main scraper will run in background"
        echo "   - MCP server will start on port 8000"
        echo "   - Check logs for progress"
        echo ""
        echo "Press Ctrl+C to stop"
        
        # Start both services
        nohup python src/main.py > scraper.log 2>&1 &
        SCRAPER_PID=$!
        
        nohup python mcp_server.py > mcp.log 2>&1 &
        MCP_PID=$!
        
        echo "✅ Services started!"
        echo "   Scraper PID: $SCRAPER_PID"
        echo "   MCP Server PID: $MCP_PID"
        echo ""
        echo "📊 Check status: curl http://localhost:8000/health"
        echo "📊 View stats: curl http://localhost:8000/stats"
        echo ""
        echo "Logs:"
        echo "   Scraper: tail -f scraper.log"
        echo "   MCP Server: tail -f mcp.log"
        ;;
        
    2)
        echo "🌐 Starting MCP Server only..."
        echo "   Server will run on port 8000"
        echo "   Check mcp.log for details"
        echo ""
        echo "Press Ctrl+C to stop"
        python mcp_server.py
        ;;
        
    3)
        echo "📊 Starting scraper only..."
        echo "   Scraper will run in background"
        echo "   Check scraper.log for progress"
        echo ""
        echo "Press Ctrl+C to stop"
        python src/main.py
        ;;
        
    4)
        echo "👋 Exiting..."
        exit 0
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete! Check the logs for any errors."
echo ""
echo "📚 For more information, see README.md"
echo "🆘 For support: jeremy@augments.art"
