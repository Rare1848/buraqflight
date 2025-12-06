import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_airblue_flights(origin, destination, date):
    print(f"🔵 Starting Airblue (Silent): {origin} -> {destination}")
    
    # --- SILENT MODE SETUP ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") # <--- THIS MAKES IT INVISIBLE
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    
    # Block images for speed
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    flights = []

    try:
        driver.get("https://www.airblue.com/")
        wait = WebDriverWait(driver, 5)

        # 1. ORIGIN
        try:
            org = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[contains(@id,'Origin') or contains(@name,'org')])[1]")))
            org.click()
            org.clear()
            org.send_keys(origin)
            time.sleep(0.5)
            org.send_keys(Keys.TAB)
        except: pass

        # 2. DESTINATION
        try:
            dest = driver.find_element(By.XPATH, "(//input[contains(@id,'Dest') or contains(@name,'dest')])[1]")
            dest.click()
            dest.clear()
            dest.send_keys(destination)
            time.sleep(0.5)
            dest.send_keys(Keys.TAB)
        except: pass

        # 3. DATE
        try:
            y, m, d = date.split('-')
            formatted_date = f"{d}/{m}/{y}"
            date_input = driver.find_element(By.XPATH, "//input[contains(@id,'Date') or contains(@name,'date')]")
            driver.execute_script(f"arguments[0].value = '{formatted_date}';", date_input)
        except: pass

        # 4. SEARCH
        try:
            search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            search_btn.click()
        except: pass

        # 5. WAIT & SCRAPE
        try:
            # Check if we are still on homepage (Invalid route)
            if "view-flight" not in driver.current_url and "sched" not in driver.current_url:
                return [] 

            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "price-display")))
            
            rows = driver.find_elements(By.CLASS_NAME, "flight-row")
            for row in rows:
                try:
                    time_val = row.find_element(By.CLASS_NAME, "time").text
                    price_val = row.find_element(By.CLASS_NAME, "price").text
                    clean_price = price_val.upper().replace("PKR", "").replace(",", "").replace("RS", "").strip()
                    
                    flights.append({
                        "airline": "Airblue",
                        "flight_no": "PA-WEB",
                        "origin": origin,
                        "destination": destination,
                        "time": time_val,
                        "price": clean_price,
                        "currency": "PKR"
                    })
                except: continue
        except:
            return []

    except Exception as e:
        print(f"❌ Airblue Error: {e}")

    finally:
        driver.quit()
        return flights