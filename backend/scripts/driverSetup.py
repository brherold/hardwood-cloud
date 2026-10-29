# driverSetup.py
'''
Keeps the current driverSetup (hardwood page)
#Should reset after every 30 mins due to Cloudflare reset 
'''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading
_driver = None  # global variable for singleton driver

def create_driver(manual=False):
    """Create a Selenium Chrome driver with anti-detection options."""
    chrome_options = Options()
    
    #chrome_options.add_argument("--headless=new") # Use new headless mode for better compatibility

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Hide webdriver property
    '''
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    '''
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
    """
    })
    return driver

def get_driver():
    """Return a single driver instance (create if it doesn't exist)."""
    global _driver
    if _driver is None:
        _driver = create_driver()
        beginnerURL = "https://onlinecollegebasketball.org"
        _driver.get(beginnerURL)
        print("Solve CAPTCHA in this browser window (waiting 10 seconds)")
        time.sleep(10)
    return _driver

def open_hardwood_home_auto():
    global _driver
    if _driver is None:
        return get_driver()
    beginnerURL = "https://onlinecollegebasketball.org"
    _driver.get(beginnerURL)
    print("Solve CAPTCHA in this browser window (waiting 10 seconds)")
    time.sleep(10)
    return _driver

def open_hardwood_home_manual():
    """Open Hardwood top prospects page and let user solve CAPTCHA."""
    driver = get_driver()
    beginnerURL = "https://onlinecollegebasketball.org"
    driver.get(beginnerURL)

    print("Solve CAPTCHA in the browser. Press Enter here when done.")

    stop_event = threading.Event()

    def ticker():
        while not stop_event.is_set():
            time.sleep(10)
            if not stop_event.is_set():
                print("⏳ Waiting for CAPTCHA solve... (10s)")

    t = threading.Thread(target=ticker, daemon=True)
    t.start()

    input()  # wait for user

    stop_event.set()
    return driver



def quit_driver():
    """Quit driver."""
    global _driver
    if _driver:
        _driver.quit()
        _driver = None
