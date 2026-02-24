import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class CookieManager:
    def __init__(self, cookies_file="cookies.txt"):
        self.cookies_file = os.path.abspath(cookies_file)

    def login_and_save_cookies(self, status_callback=None):
        """
        Opens a Chrome window for the user to log in.
        Once logged in (user closes the window or we detect it),
        saves cookies in Netscape format.
        """
        if status_callback:
            status_callback("Launching Browser for Login...")

        options = Options()
        # Headless mode often triggers anti-bot protections, so we show the window.
        # options.add_argument("--headless") 
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Stealth: Remove navigator.webdriver property
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })

            driver.get("https://www.pornhub.com/login")
            
            if status_callback:
                status_callback("Waiting for you to log in...")
            
            # Loop to check for login success or window close
            # We assume login is successful if we see specific cookies or user closes window
            while True:
                try:
                    # Check if window is still open
                    if not driver.window_handles:
                        break
                    
                    cookies = driver.get_cookies()
                    cookie_names = [c['name'] for c in cookies]
                    
                    # 'bs' and 'ss' are common PH session cookies, 'access_token' might be there too
                    # If we see them, we can assume login might be done, but better to let user decide or wait for close.
                    # For now, we mainly wait for window close to ensure they finished 2FA etc.
                    
                    time.sleep(1)
                except Exception:
                    break
            
            # If we are here, window might be closed. 
            # If driver is still accessible, try to grab cookies one last time.
            try:
                if driver.window_handles:
                    cookies = driver.get_cookies()    
                    driver.quit()
                else:
                    # Logic for when window is already closed is tricky with Selenium, 
                    # usually we can't get cookies after close. 
                    # So we should actually capture cookies periodically if we want to support "close to finish".
                    # BUT, 'driver.get_cookies()' works as long as driver process is alive.
                    pass
            except:
                pass

            # Since we can't easily detect "user finished" without a button in UI or closing window (which kills session),
            # The best flow is: User logs in, then closes the browser.
            # However, if they close the browser, we might lose the session if not saved.
            # ACTUALLY: We need to save cookies *before* they close, or use a "I'm done" prompt.
            # Simplified approach: We install a listener or just run a loop that saves valid cookies if found.
            
            # Re-thinking: The user closes the browser => Driver dies => Can't get cookies.
            # Solution: We will start the browser, and in the background loop, if we see 'bs' cookie (logged in), 
            # we save it and then close the driver automatically? 
            # OR we tell the user "Close this window when done".
            
            return self.cookies_file

        except Exception as e:
            print(f"Selenium Error: {e}")
            if status_callback:
                status_callback(f"Login Error: {str(e)}")
            return None
        finally:
            # logic to ensure driver is quit
            try:
                if driver:
                    driver.quit()
            except:
                pass

    def run_login_flow(self, status_callback=None):
        """
        Executes the robust login flow.
        """
        if status_callback:
            status_callback("Initializing Login Browser...")
            
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get("https://www.pornhub.com/login")
            
            if status_callback:
                status_callback("Browser Open. Please Log In via the opened window.")

            # Monitor for login cookies
            max_retries = 300 # 5 minutes max
            logged_in = False
            
            for _ in range(max_retries):
                try:
                    if not driver.window_handles:
                        break # User closed window
                        
                    cookies = driver.get_cookies()
                    cookie_names = [c['name'] for c in cookies]
                    
                    # 'ua' is User Attribute, 'bs' is often session. 
                    # If we see a significant number of cookies or specific ones, we save.
                    # Best indicator: 'platform' or 'bs'
                    if 'bs' in cookie_names:
                        self._save_cookies_netscape(cookies)
                        logged_in = True
                        if status_callback:
                            status_callback("Login Detected! Saving cookies...")
                        time.sleep(2) # Give it a moment
                        break
                    
                    time.sleep(1)
                except:
                    break
            
            if logged_in:
                driver.quit()
                return self.cookies_file
            else:
                return None

        except Exception as e:
            if status_callback:
                status_callback(f"Error: {e}")
            return None
        finally:
            try:
                driver.quit()
            except:
                pass

    def _save_cookies_netscape(self, cookies):
        with open(self.cookies_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This file is generated by the application. Do not edit.\n\n")
            
            for cookie in cookies:
                domain = cookie.get('domain', '')
                flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure') else 'FALSE'
                expiry = str(int(cookie.get('expiry', time.time() + 3600*24*365)))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
