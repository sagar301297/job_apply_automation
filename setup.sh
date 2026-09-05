#!/bin/bash
# Autonomous Job Applier - Setup Script

echo "🚀 Starting Setup for Autonomous Job Applier..."

# 1. Check Python version (requires 3.11+)
PYTHON_CMD="python3"
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
fi
echo "🐍 Using Python binary: $PYTHON_CMD"

# 2. Setup Virtual Environment
if [ ! -d "ai_job_env" ]; then
    echo "📦 Creating virtual environment 'ai_job_env'..."
    $PYTHON_CMD -m venv ai_job_env
else
    echo "📦 Virtual environment 'ai_job_env' already exists."
fi

# 3. Activate and install requirements
echo "⬇️ Installing dependencies..."
source ai_job_env/bin/activate
pip install -r requirements.txt
playwright install chromium

# 4. Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file template..."
    echo "GEMINI_API_KEY=your_api_key_here" > .env
    echo "⚠️ Please remember to add your API key to the .env file!"
fi

# 5. Create user_profile.py if it doesn't exist
if [ ! -f "user_profile.py" ]; then
    if [ -f "user_profile.example.py" ]; then
        echo "👤 Creating user_profile.py from template..."
        cp user_profile.example.py user_profile.py
        echo "⚠️ Please remember to edit user_profile.py with your real personal details and resume path!"
    fi
fi

# 6. Ensure chrome_profile folder exists for persistent sessions
mkdir -p chrome_profile

echo ""
echo "✅ Setup Complete!"
echo "To run the agent, make sure to configure your files, then run:"
echo "source ai_job_env/bin/activate"
echo "python multi_apply_agent.py"
