#!/bin/bash

# Fix the centering of the TurnClicksToClients.com logo in the onboarding login form
sed -i 's|<div class="w-40 mx-auto mb-4 text-center text-blue-600 font-bold text-2xl">TurnClicksToClients.com</div>|<div class="mx-auto mb-4 text-center text-blue-600 font-bold text-2xl">TurnClicksToClients.com</div>|g' apps/onboarding/index.html

# Fix the extra whitespace in the div
sed -i 's|                                        </div>|        </div>|g' apps/onboarding/index.html

echo "Logo centering fixed in the onboarding login form."
