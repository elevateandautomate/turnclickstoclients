#!/bin/bash

# Fix the CTA links in the quiz-applications directory
find quiz-applications -type f -name "*.html" -exec sed -i 's|file:///C:/Users/Eleva/Desktop/todo/contactlead/universal-application-form.html|../../universal-application-form.html|g' {} \;

echo "CTA links fixed in the quiz-applications directory."
