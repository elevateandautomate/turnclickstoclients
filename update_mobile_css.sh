#!/bin/bash

# Replace the existing mobile optimization CSS with the enhanced version
cp enhanced_mobile_optimization.css mobile_optimization.css
cp enhanced_mobile_optimization.css website/mobile_optimization.css
cp enhanced_mobile_optimization.css apps/mobile_optimization.css
cp enhanced_mobile_optimization.css coldoutbound/mobile_optimization.css

echo "Mobile optimization CSS updated with enhanced spacing rules."
