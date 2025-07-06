#!/bin/bash
# Push Stock Market Analyzer to GitHub

echo "🚀 Pushing Stock Market Analyzer to GitHub"
echo "==========================================="

# Check if Git is configured
if ! git config user.name &> /dev/null; then
    echo "⚠️ Git not configured. Please run:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

echo "✅ Git configured for user: $(git config user.name)"
echo ""

# Instructions for creating GitHub repository
echo "📋 Steps to push to GitHub:"
echo ""
echo "1. 🌐 Go to: https://github.com/new"
echo "2. 📝 Repository name: stockit-analyzer (or your preferred name)"
echo "3. 📄 Description: Indian Stock Market Analyzer with AI recommendations and alerts"
echo "4. 🔓 Choose: Public (for free Streamlit Cloud deployment)"
echo "5. ❌ Don't initialize with README (we already have one)"
echo "6. 🚀 Click 'Create repository'"
echo ""

read -p "Have you created the GitHub repository? (y/n): " repo_created

if [ "$repo_created" = "y" ] || [ "$repo_created" = "Y" ]; then
    echo ""
    read -p "📝 Enter your GitHub username: " github_username
    read -p "📝 Enter your repository name (e.g., stockit-analyzer): " repo_name
    
    # Add remote origin
    REPO_URL="https://github.com/${github_username}/${repo_name}.git"
    echo "🔗 Adding remote origin: $REPO_URL"
    git remote add origin $REPO_URL
    
    # Set main branch
    echo "🌿 Setting main branch..."
    git branch -M main
    
    # Push to GitHub
    echo "📤 Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Successfully pushed to GitHub!"
        echo "================================="
        echo ""
        echo "🌐 Your repository: https://github.com/${github_username}/${repo_name}"
        echo ""
        echo "🚀 Ready for FREE deployment:"
        echo ""
        echo "✅ Streamlit Cloud:"
        echo "   1. Go to: https://share.streamlit.io/"
        echo "   2. Sign in with GitHub"
        echo "   3. Click 'New app'"
        echo "   4. Select: ${github_username}/${repo_name}"
        echo "   5. Branch: main"
        echo "   6. Main file: app.py"
        echo "   7. Click 'Deploy!'"
        echo ""
        echo "✅ Railway:"
        echo "   1. Go to: https://railway.app/"
        echo "   2. Sign in with GitHub"
        echo "   3. 'New Project' → 'Deploy from GitHub repo'"
        echo "   4. Select: ${github_username}/${repo_name}"
        echo ""
        echo "✅ Render:"
        echo "   1. Go to: https://render.com/"
        echo "   2. Sign in with GitHub"
        echo "   3. 'New Web Service'"
        echo "   4. Connect: ${github_username}/${repo_name}"
        echo ""
        echo "🔐 Don't forget to add environment variables:"
        echo "   TWILIO_ACCOUNT_SID"
        echo "   TWILIO_AUTH_TOKEN"
        echo "   TWILIO_PHONE_NUMBER"
        echo "   TARGET_PHONE_NUMBER"
        echo "   TARGET_WHATSAPP_NUMBER"
        echo ""
        echo "📱 Your Stock Analyzer will be live in 2-5 minutes!"
    else
        echo "❌ Failed to push to GitHub. Please check:"
        echo "   • Repository URL is correct"
        echo "   • You have push permissions"
        echo "   • GitHub credentials are set up"
        echo ""
        echo "💡 Try these commands manually:"
        echo "   git remote -v"
        echo "   git push -u origin main"
    fi
else
    echo ""
    echo "📋 Please create GitHub repository first:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: stockit-analyzer"
    echo "3. Description: Indian Stock Market Analyzer"
    echo "4. Public repository"
    echo "5. Don't initialize with README"
    echo "6. Create repository"
    echo "7. Run this script again"
fi
