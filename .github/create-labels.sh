#!/bin/bash
# Space Framework - Create All GitHub Labels
# Repository: https://github.com/nsin08/ai_agents
# Run this script to create all Rule 12 labels

REPO="nsin08/ai_agents"

echo "Creating state labels..."
gh label create "state:idea" --description "Initial business idea" --color "FFA500" --repo $REPO
gh label create "state:approved" --description "Idea approved by stakeholder" --color "0075CA" --repo $REPO
gh label create "state:ready" --description "Story ready for implementation (DoR met)" --color "7057FF" --repo $REPO
gh label create "state:in-progress" --description "Currently being worked on" --color "FBCA04" --repo $REPO
gh label create "state:in-review" --description "In code review (PR open)" --color "E99695" --repo $REPO
gh label create "state:done" --description "Complete and merged (DoD met)" --color "28A745" --repo $REPO
gh label create "state:released" --description "Deployed to production" --color "004B87" --repo $REPO

echo "Creating type labels..."
gh label create "type:idea" --description "Business idea or feature concept" --color "1D76DB" --repo $REPO
gh label create "type:epic" --description "Large feature breakdown" --color "0052CC" --repo $REPO
gh label create "type:story" --description "User story or feature" --color "D4C5F9" --repo $REPO
gh label create "type:task" --description "Chore, refactor, or technical work" --color "BFD4F2" --repo $REPO
gh label create "type:bug" --description "Bug report" --color "D73A49" --repo $REPO
gh label create "type:feature-request" --description "Feature request from user" --color "A2EEEF" --repo $REPO

echo "Creating priority labels..."
gh label create "priority:critical" --description "Blocking, urgent" --color "FF0000" --repo $REPO
gh label create "priority:high" --description "Important, needed soon" --color "FF6B6B" --repo $REPO
gh label create "priority:medium" --description "Normal priority" --color "FFA500" --repo $REPO
gh label create "priority:low" --description "Nice to have, future" --color "90EE90" --repo $REPO

echo "Creating role labels..."
gh label create "role:implementer" --description "Implementation task" --color "CCCCCC" --repo $REPO
gh label create "role:reviewer" --description "Requires review" --color "999999" --repo $REPO
gh label create "role:codeowner" --description "Requires CODEOWNER action" --color "333333" --repo $REPO

echo "✅ All 23 labels created!"
echo "Verify at: https://github.com/nsin08/ai_agents/labels"
