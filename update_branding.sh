#!/bin/bash

# Update the copyright notice
sed -i 's|&copy; 2024 The Connector Group. All rights reserved.|&copy; 2024 TurnClicksToClients.com. All rights reserved.|g' apps/onboarding/index.html

# Update the portal title
sed -i 's|<h1 id="portal-title" class="text-2xl font-bold text-gray-800">The Connector Group Onboarding Portal</h1>|<h1 id="portal-title" class="text-2xl font-bold text-gray-800">TurnClicksToClients.com Onboarding Portal</h1>|g' apps/onboarding/index.html

# Update the welcome message
sed -i 's|Complete the steps below to set up your account with The Connector Group. We recommend following these steps in order.|Complete the steps below to set up your account with TurnClicksToClients.com. We recommend following these steps in order.|g' apps/onboarding/index.html

# Update the guide title
sed -i 's|<h3 class="text-xl font-bold text-gray-800" id="guide-title">The Connector Group Welcome Guide</h3>|<h3 class="text-xl font-bold text-gray-800" id="guide-title">TurnClicksToClients.com Welcome Guide</h3>|g' apps/onboarding/index.html

# Update the guide heading
sed -i 's|<h4 class="text-2xl font-bold text-gray-800 mb-4">The Connector Group Getting Started Guide</h4>|<h4 class="text-2xl font-bold text-gray-800 mb-4">TurnClicksToClients.com Getting Started Guide</h4>|g' apps/onboarding/index.html

# Update the guide description
sed -i 's|<p class="text-gray-500 mt-1">Learn how The Connector Group will help elevate your business</p>|<p class="text-gray-500 mt-1">Learn how TurnClicksToClients.com will help elevate your business</p>|g' apps/onboarding/index.html

# Update the guide box title
sed -i 's|<h3 class="text-lg font-semibold text-gray-800">The Connector Group Guide</h3>|<h3 class="text-lg font-semibold text-gray-800">TurnClicksToClients.com Guide</h3>|g' apps/onboarding/index.html

# Update the service agreement title
sed -i 's|<h4 class="text-lg font-semibold text-gray-800 mb-3 text-center">THE CONNECTOR GROUP SERVICE AGREEMENT</h4>|<h4 class="text-lg font-semibold text-gray-800 mb-3 text-center">TURNCLICKSTOCLIENTS.COM SERVICE AGREEMENT</h4>|g' apps/onboarding/index.html

# Update the service agreement text
sed -i 's|This Service Agreement (the "Agreement") is entered into by and between The Connector Group ("The Connector Group" or "We") and the undersigned customer ("Customer" or "You") as of the date of signing this Agreement.|This Service Agreement (the "Agreement") is entered into by and between TurnClicksToClients.com ("TurnClicksToClients.com" or "We") and the undersigned customer ("Customer" or "You") as of the date of signing this Agreement.|g' apps/onboarding/index.html

# Update the non-refundable payments text
sed -i 's|<p><strong>1.2 Non-Refundable Payments:</strong> All payments made to The Connector Group are non-refundable under any circumstances.</p>|<p><strong>1.2 Non-Refundable Payments:</strong> All payments made to TurnClicksToClients.com are non-refundable under any circumstances.</p>|g' apps/onboarding/index.html

# Update the core services text
sed -i 's|<p><strong>2.1 Core Services:</strong> The Connector Group will provide business messaging and communication services as outlined in your selected service package.</p>|<p><strong>2.1 Core Services:</strong> TurnClicksToClients.com will provide business messaging and communication services as outlined in your selected service package.</p>|g' apps/onboarding/index.html

# Update the intellectual property text
sed -i 's|<p><strong>5.1 Ownership:</strong> All intellectual property related to our services remains the property of The Connector Group.</p>|<p><strong>5.1 Ownership:</strong> All intellectual property related to our services remains the property of TurnClicksToClients.com.</p>|g' apps/onboarding/index.html

# Update the social media text
sed -i 's|Connecting your social media accounts with The Connector Group enables seamless campaign management and optimization:|Connecting your social media accounts with TurnClicksToClients.com enables seamless campaign management and optimization:|g' apps/onboarding/index.html

# Update the quiz questions
sed -i 's|1. What is the primary focus of The Connector Group'\''s service?|1. What is the primary focus of TurnClicksToClients.com'\''s service?|g' apps/onboarding/index.html
sed -i 's|2. Which tasks does The Connector Group handle for your business?|2. Which tasks does TurnClicksToClients.com handle for your business?|g' apps/onboarding/index.html
sed -i 's|3. What makes The Connector Group'\''s system particularly effective?|3. What makes TurnClicksToClients.com'\''s system particularly effective?|g' apps/onboarding/index.html
sed -i 's|4. The Connector Group'\''s system is designed to work for:|4. TurnClicksToClients.com'\''s system is designed to work for:|g' apps/onboarding/index.html
sed -i 's|5. What type of freedom does The Connector Group'\''s system aim to provide?|5. What type of freedom does TurnClicksToClients.com'\''s system aim to provide?|g' apps/onboarding/index.html

# Update the authorization form
sed -i 's|As part of our commitment to providing a seamless and secure billing experience, The Connector Group requires a active card on file to facilitate your subscription payments.|As part of our commitment to providing a seamless and secure billing experience, TurnClicksToClients.com requires a active card on file to facilitate your subscription payments.|g' apps/onboarding/index.html
sed -i 's|Authorize The Connector Group to securely process subscription payments according to your chosen plan.|Authorize TurnClicksToClients.com to securely process subscription payments according to your chosen plan.|g' apps/onboarding/index.html
sed -i 's|<h4 class="text-lg font-semibold text-gray-800 mb-3">The Connector Group LLC Credit Card Authorization Form Authorization Details:</h4>|<h4 class="text-lg font-semibold text-gray-800 mb-3">TurnClicksToClients.com Credit Card Authorization Form Authorization Details:</h4>|g' apps/onboarding/index.html
sed -i 's|By completing and submitting this form, you authorize The Connector Group LLC, Elevate and Automate LLC, or EOR Consulting LLC to charge your credit card|By completing and submitting this form, you authorize TurnClicksToClients.com, Elevate and Automate LLC, or EOR Consulting LLC to charge your credit card|g' apps/onboarding/index.html
sed -i 's|You agree to notify The Connector Group LLC, Elevate and Automate LLC, or EOR Consulting LLC of any changes to your credit card information|You agree to notify TurnClicksToClients.com, Elevate and Automate LLC, or EOR Consulting LLC of any changes to your credit card information|g' apps/onboarding/index.html

echo "All branding updated from 'The Connector Group' to 'TurnClicksToClients.com' in the onboarding portal."
