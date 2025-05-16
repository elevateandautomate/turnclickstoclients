#!/bin/bash

# Fix the copyright text in the onboarding login form
sed -i 's|&copy; 2024 The Connector Group. All rights reserved.copy; 2024 TurnClicksToClients.com. All rights reserved.|&copy; 2024 TurnClicksToClients.com. All rights reserved.|g' apps/onboarding/index.html

echo "Copyright text fixed in the onboarding login form."
