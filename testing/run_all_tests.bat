@echo off
echo Running all pre-launch tests...
echo.

echo 1. Testing tracking functionality...
python test_tracking.py
echo.

echo 2. Testing split test variations...
python test_split_variations.py
echo.

echo 3. Testing Supabase tracking integration...
python test_supabase_tracking.py
echo.

echo 4. Opening browser-based tests...
start "" "split_test_distribution.html"
start "" "dashboard_integration_test.html"
echo.

echo All tests started!
echo Please review the results and check against the pre-launch checklist.
pause
