#!/bin/bash

# Fix the CTA links in the website/index.html file
sed -i 's|file:///C:/Users/Eleva/Desktop/todo/contactlead/quiz-start.html|quiz-start.html|g' website/index.html

echo "CTA links fixed in the website/index.html file."
