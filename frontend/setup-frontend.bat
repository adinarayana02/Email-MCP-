@echo off
echo 🚀 Setting up AI Communication Assistant Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

REM Check Node.js version
for /f "tokens=1,2 delims=." %%a in ('node --version') do set NODE_VERSION=%%a
set NODE_VERSION=%NODE_VERSION:~1%
if %NODE_VERSION% lss 16 (
    echo ❌ Node.js version 16+ is required. Current version: 
    node --version
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo ✅ npm version: 
npm --version

REM Install dependencies
echo 📦 Installing dependencies...
npm install

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully!
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 🔧 Creating .env file...
    (
        echo REACT_APP_API_URL=http://localhost:8000
        echo REACT_APP_APP_NAME=AI Communication Assistant
        echo REACT_APP_VERSION=1.0.0
        echo REACT_APP_ENVIRONMENT=development
    ) > .env
    echo ✅ .env file created
)

echo.
echo 🎉 Frontend setup completed successfully!
echo.
echo To start the development server, run:
echo   npm start
echo.
echo The application will open at http://localhost:3000
echo.
echo Make sure your backend is running on http://localhost:8000
echo.
pause
