@echo off
echo Updating quiz result pages with trust mechanism elements...
python trust_mechanism_update.py %1 %2 %3
echo Done!
pause
