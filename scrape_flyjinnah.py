import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_flyjinnah_prices(origin, destination, date):
    print(f"🔴 Starting Fly Jinnah (Silent): {origin} -> {destination}")
    
    # --- SILENT MODE SETUP ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") # <--- THIS MAKES IT INVISIBLE
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Critical User-Agent for Headless mode to work on Fly Jinnah
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Block images
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    flights = []

    try:
        driver.get("https://book.flyjinnah.com/en")
        wait = WebDriverWait(driver, 10)

        # 1. Popup
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#onetrust-accept-btn-handler"))).click()
        except: pass

        # 2. Origin
        try:
            org = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@type='text'])[1]")))
            org.click()
            org.send_keys(origin)
            time.sleep(0.5)
            org.send_keys(Keys.ENTER)
        except: pass

        # 3. Destination
        try:
            dest = driver.find_element(By.XPATH, "(//input[@type='text'])[2]")
            dest.click()
            dest.send_keys(destination)
            time.sleep(1)
            dest.send_keys(Keys.ENTER)
        except: pass

        # 4. Date
        try:
            y, m, d = date.split('-')
            formatted = f"{d}/{m}/{y}"
            date_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Date'], input.date-picker")
            driver.execute_script(f"arguments[0].value = '{formatted}';", date_input)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_input)
        except: pass

        # 5. Search
        try:
            btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            driver.execute_script("arguments[0].click();", btn)
        except: pass

        # 6. Wait & Scrape
        try:
            wait.until(lambda d: d.find_elements(By.CLASS_NAME, "currency-symbol") or d.find_elements(By.CLASS_NAME, "error-message"))
            
            if driver.find_elements(By.CLASS_NAME, "error-message"):
                return []

            rows = driver.find_elements(By.CSS_SELECTOR, ".flight-row, .journey-wrapper")
            for row in rows:
                try:
                    price_ele = row.find_element(By.CSS_SELECTOR, ".amount, .total-price")
                    clean_price = price_ele.text.strip().upper().replace("PKR", "").replace(",", "").strip()
                    if clean_price.isdigit():
                        flights.append({
                            "airline": "Fly Jinnah",
                            "flight_no": "9P-WEB",
                            "origin": origin,
                            "destination": destination,
                            "time": "See Site", 
                            "price": clean_price,
                            "currency": "PKR"
                        })
                except: continue
        except:
            return []

    except Exception as e:
        print(f"❌ Fly Jinnah Error: {e}")

    finally:
        driver.quit()
        return flights