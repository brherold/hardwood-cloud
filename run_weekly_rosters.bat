@echo off
setlocal
cd /d "%~dp0"
echo ======================================================== >> scraper.log
echo [Weekly Rosters Scrape Started: %date% %time%] >> scraper.log
python run_scraper.py --action rosters >> scraper.log 2>&1
echo [Weekly Rosters Scrape Finished: %date% %time%] >> scraper.log
endlocal
