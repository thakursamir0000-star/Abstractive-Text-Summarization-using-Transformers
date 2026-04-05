#!/usr/bin/env bash
# Quick setup script for development

set -e  # Exit on error

echo "🚀 Setting up Text Summarization Project..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
echo "📚 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "   💡 Remember to customize .env if needed"
fi

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v --tb=short || echo "⚠️  Some tests may have failed - check output above"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Activate environment: source venv/bin/activate (or venv\\Scripts\\activate on Windows)"
echo "   2. Run app: streamlit run app.py"
echo "   3. Open browser: http://localhost:8501"
echo ""
echo "🔗 Useful commands:"
echo "   - pytest              : Run tests"
echo "   - black src/ tests/    : Format code"
echo "   - flake8 src/ tests/   : Lint code"
echo "   - mypy src/            : Type check"
echo ""
