#!/bin/bash
# Setup script for FloatChat React Frontend

echo "🌊 Setting up FloatChat React Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first:"
    echo "   https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are available"

# Install dependencies
echo "📦 Installing React dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🚀 Setup complete! To run the application:"
echo ""
echo "1. Start the Python API server:"
echo "   python api_server.py"
echo ""
echo "2. In a new terminal, start the React app:"
echo "   npm start"
echo ""
echo "3. Open your browser to: http://localhost:3000"
echo ""
echo "The React app will automatically connect to the Python API server."
