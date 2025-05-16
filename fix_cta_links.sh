#!/bin/bash

# Fix the CTA links in the home page
sed -i 's|file:///C:/Users/Eleva/Desktop/todo/contactlead/quiz-start.html|quiz-start.html|g' index.html

echo "CTA links fixed in the home page."
