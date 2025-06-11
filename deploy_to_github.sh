#!/bin/bash

# 🚀 Magical Fanfiction Generator - GitHub Deployment Script
# This script helps you quickly deploy your project to GitHub

echo "⚡ Magical Fanfiction Generator - GitHub Deployment ⚡"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please run this script from the project directory."
    exit 1
fi

# Get GitHub username
echo ""
read -p "🧙‍♂️ Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required!"
    exit 1
fi

# Repository name
REPO_NAME="magical-fanfiction-generator"

echo ""
echo "📋 Repository Details:"
echo "   Username: $GITHUB_USERNAME"
echo "   Repository: $REPO_NAME"
echo "   URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

echo ""
echo "🔧 Setting up remote repository..."

# Remove existing origin if it exists
git remote remove origin 2>/dev/null || true

# Add new origin
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "✅ Remote repository configured!"

echo ""
echo "📤 Ready to push to GitHub!"
echo ""
echo "Next steps:"
echo "1. Create the repository on GitHub.com:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: ⚡ Create enchanting Harry Potter fanfiction using AI"
echo "   - Make it Public"
echo "   - DO NOT initialize with README, .gitignore, or license"
echo ""
echo "2. After creating the repository, run:"
echo "   git push -u origin main"
echo ""
echo "🎉 Your magical project will be live on GitHub!"

# Optional: Try to push if user confirms
echo ""
read -p "🚀 Have you created the repository? Push now? (y/N): " PUSH_NOW

if [[ $PUSH_NOW =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Pushing to GitHub..."
    
    if git push -u origin main; then
        echo ""
        echo "🎉 SUCCESS! Your project is now live on GitHub!"
        echo "🔗 View it at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
        echo ""
        echo "✨ Share your magical fanfiction generator with the world! ✨"
    else
        echo ""
        echo "❌ Push failed. Please make sure:"
        echo "   1. The repository exists on GitHub"
        echo "   2. You have push permissions"
        echo "   3. Your GitHub credentials are set up"
        echo ""
        echo "💡 You can try pushing manually with:"
        echo "   git push -u origin main"
    fi
else
    echo ""
    echo "📝 When you're ready, run: git push -u origin main"
    echo "🔗 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
fi

echo ""
echo "⚡ Thank you for using the Magical Fanfiction Generator! ⚡"