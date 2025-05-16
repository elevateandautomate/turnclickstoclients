#!/bin/bash

# Update the logo in the onboarding index.html file
sed -i 's|<img src="https://storage.googleapis.com/msgsndr/C4EL78WQvWpqMgSsv2kE/media/680f685733fee4f1f74411df.png" alt="The Connector Group Logo" class="w-40 mx-auto mb-4 shadow" style="height:auto; border-radius:12px;" />|<div class="w-40 mx-auto mb-4 text-center text-blue-600 font-bold text-2xl">TurnClicksToClients.com</div>|g' apps/onboarding/index.html

# Also update the title
sed -i 's|<title>The Connector Group - Onboarding</title>|<title>TurnClicksToClients.com - Onboarding</title>|g' apps/onboarding/index.html

echo "Logo and title updated in the onboarding portal."
