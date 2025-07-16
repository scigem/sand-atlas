#!/bin/bash

# Sand Atlas Link Checker Helper Script
# Builds the site and runs link checking

set -e  # Exit on any error

echo "🏗️  Building Jekyll site..."
bundle exec jekyll build

echo ""
echo "🔗 Running link check..."

# Check if Python script exists
if [ ! -f "scripts/check_links.py" ]; then
    echo "❌ Error: scripts/check_links.py not found!"
    echo "   Make sure you're running this from the repository root."
    exit 1
fi

# Install Python dependencies if needed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    python3 -m pip install requests
fi

# Run the link checker with default options
python3 scripts/check_links.py "$@"

echo ""
echo "📄 Check the generated reports:"
echo "   - link_check_report.md (human-readable)"
echo "   - link_check_results.json (machine-readable)"
