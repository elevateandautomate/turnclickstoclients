#!/bin/bash

# Update the button text from "3 Mins" to "30 seconds" in the home page
sed -i 's|in 3 Mins|in 30 seconds|g' index.html
sed -i 's|in 3 Mins|in 30 seconds|g' website/index.html

echo "Button text updated from '3 Mins' to '30 seconds' in the home page."
