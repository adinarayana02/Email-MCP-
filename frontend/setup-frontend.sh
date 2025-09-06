#!/bin/bash

echo "🚀 Setting up AI Communication Assistant Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=AI Communication Assistant
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
EOF
    echo "✅ .env file created"
fi

echo ""
echo "🎉 Frontend setup completed successfully!"
echo ""
echo "To start the development server, run:"
echo "  npm start"
echo ""
echo "The application will open at http://localhost:3000"
echo ""
echo "Make sure your backend is running on http://localhost:8000"
echo ""
