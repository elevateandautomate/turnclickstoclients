@echo off
echo Updating quiz result pages with towards language...
python towards_language_update.py %1 %2 %3
echo Done!
pause
