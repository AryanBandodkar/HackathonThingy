@echo off
echo 🌊 Setting up FloatChat React Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first:
    echo    https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo ✅ Node.js and npm are available

REM Install dependencies
echo 📦 Installing React dependencies...
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.
echo 🚀 Setup complete! To run the application:
echo.
echo 1. Start the Python API server:
echo    python api_server.py
echo.
echo 2. In a new terminal, start the React app:
echo    npm start
echo.
echo 3. Open your browser to: http://localhost:3000
echo.
echo The React app will automatically connect to the Python API server.
pause
