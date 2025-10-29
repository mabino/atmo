#!/bin/bash

# Atmo Documentation Site Setup Script

echo "🚀 Setting up Atmo documentation site..."

# Check if we're in the docs directory
if [ ! -f "_config.yml" ]; then
    echo "❌ Please run this script from the docs/ directory"
    exit 1
fi

# Check if Ruby is installed
if ! command -v ruby &> /dev/null; then
    echo "❌ Ruby is not installed. Please install Ruby first."
    echo "   On macOS: brew install ruby"
    exit 1
fi

# Check if Bundler is installed
if ! command -v bundle &> /dev/null; then
    echo "📦 Installing Bundler..."
    gem install bundler
fi

# Install dependencies
echo "📦 Installing Jekyll dependencies..."
bundle install

# Copy screenshots
echo "📸 Copying screenshots..."
mkdir -p assets/images
cp -r ../../screenshots/* assets/images/ 2>/dev/null || echo "⚠️  No screenshots found in root screenshots/ directory"

# Start development server
echo "🌐 Starting Jekyll development server..."
echo "   Site will be available at: http://localhost:4000/atmo/"
bundle exec jekyll serve --baseurl "/atmo"