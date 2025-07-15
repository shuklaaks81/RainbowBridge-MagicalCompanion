#!/bin/bash
# GitHub Issue Creation Script for Rainbow Bridge Routine MCP Integration

echo "🌈 Creating GitHub Issue for Rainbow Bridge Routine MCP Integration..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "📝 Please create the issue manually using the browser method."
    echo "🔗 Go to: https://github.com/shuklaaks81/RainbowBridge-MagicalCompanion/issues/new"
    exit 1
fi

# Create the issue using GitHub CLI
gh issue create \
    --title "[COMPLETED] Implement Routine Management with MCP Server Integration" \
    --body-file GITHUB_ISSUE_TEMPLATE.md \
    --label "enhancement,completed,mcp-integration,routine-management" \
    --repo shuklaaks81/RainbowBridge-MagicalCompanion

if [ $? -eq 0 ]; then
    echo "✅ GitHub issue created successfully!"
    echo "🎉 Issue includes comprehensive documentation of the MCP routine integration work."
else
    echo "❌ Failed to create issue via GitHub CLI."
    echo "📝 Please create manually using the browser method."
fi
