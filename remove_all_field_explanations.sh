#!/bin/bash

# Remove all field explanations from all quiz pages
find . -name "*-quiz.html" -exec sed -i '/<p class="field-explanation">We'\''re asking/d' {} \;

echo "All field explanations removed from all quiz pages."
