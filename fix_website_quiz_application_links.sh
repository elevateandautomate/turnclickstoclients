#!/bin/bash

# Fix the CTA links in the website/quiz-applications directory
find website/quiz-applications -type f -name "*.html" -exec sed -i 's|file:///C:/Users/Eleva/Desktop/todo/contactlead/universal-application-form.html|../../../universal-application-form.html|g' {} \;

echo "CTA links fixed in the website/quiz-applications directory."
