@echo off
setlocal
cd /d "%~dp0"
echo ======================================================== >> scraper.log
echo [Daily Games Scrape Started: %date% %time%] >> scraper.log
python run_scraper.py --action games >> scraper.log 2>&1
echo [Daily Games Scrape Finished: %date% %time%] >> scraper.log
endlocal
