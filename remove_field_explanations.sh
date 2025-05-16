#!/bin/bash

# Remove the field explanations from all quiz pages
find . -name "*-quiz.html" -exec sed -i '/<p class="field-explanation">We'\''re asking so we can personalize your growth plan and recommendations.<\/p>/d' {} \;
find . -name "*-quiz.html" -exec sed -i '/<p class="field-explanation">We'\''re asking to create your complete profile in our system.<\/p>/d' {} \;
find . -name "*-quiz.html" -exec sed -i '/<p class="field-explanation">We'\''re asking so we can tailor our recommendations to your specific practice.<\/p>/d' {} \;
find . -name "*-quiz.html" -exec sed -i '/<p class="field-explanation">We'\''re asking so we can send you your personalized growth plan and follow-up resources.<\/p>/d' {} \;
find . -name "*-quiz.html" -exec sed -i '/<p class="field-explanation">We'\''re asking so our team can reach out with specific insights about your practice growth opportunities.<\/p>/d' {} \;

echo "Field explanations removed from all quiz pages."
