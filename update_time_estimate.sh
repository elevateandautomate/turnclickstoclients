#!/bin/bash

# Update the "3 min" text to "30 seconds" in the onboarding portal
sed -i 's|Estimated time: 3 min|Estimated time: 30 seconds|g' apps/onboarding/index.html

echo "Time estimates updated from '3 min' to '30 seconds' in the onboarding portal."
