#!/bin/bash
# 📡 OmniDrive GitHub Mirror Publisher
# Syncs local changes to Mac Mini and pushes to GitHub via SSH.

MINI_IP="100.64.196.24"
MINI_USER="jaegwan.kim"
MINI_PATH="~/omnidrive"
GITHUB_REPO="git@github.com:encredible/omnidrive.git"

echo "📂 Staging local changes..."
git add .
git commit -m "Ecosystem Update: Dockerized Web Dashboard & packaging" 2>/dev/null || true

echo "📡 Syncing workspace to Mac Mini ($MINI_IP)..."
rsync -avz --exclude '.git' --exclude 'omnidrive.egg-info' \
    /Users/jack/.gemini/antigravity/scratch/omnidrive/ \
    ${MINI_USER}@${MINI_IP}:${MINI_PATH}/

if [ $? -ne 0 ]; then
    echo "❌ Sync failed. Please check connection to Mac Mini over Tailscale."
    exit 1
fi

echo "🚀 Executing Git push from Mac Mini to GitHub..."
ssh ${MINI_USER}@${MINI_IP} << EOF
    cd ${MINI_PATH}
    git init
    # Configure Gitea/GitHub Identity
    git config user.name "j1010red"
    git config user.email "j1010red@j1010red.com"
    
    git add .
    git commit -m "Ecosystem Update: Dockerized Web Dashboard & CLI Package v0.1.0" --allow-empty
    
    git remote remove origin 2>/dev/null
    git remote add origin ${GITHUB_REPO}
    git branch -M main
    
    echo "Pushing main branch to git@github.com:encredible/omnidrive.git..."
    git push -u origin main --force
EOF

if [ $? -eq 0 ]; then
    echo "🎉 Repository successfully published to GitHub: https://github.com/encredible/omnidrive"
else
    echo "❌ Push to GitHub failed."
fi
