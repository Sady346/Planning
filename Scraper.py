from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

SEARCH_TERMS = ["London Dock", "Wood Wharf", "South Quay Plaza"]
BASE_SEARCH_URL = "https://development.towerhamlets.gov.uk/online-applications/search.do?action=simple"
OUTPUT_FILE = "application_ids.txt"

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

found_ids = set()

for term in SEARCH_TERMS:
    print(f"\nSearching for: {term}")
    driver.get(BASE_SEARCH_URL)

    search_box = wait.until(EC.presence_of_element_located((By.ID, "simpleSearchString")))
    search_box.clear()
    search_box.send_keys(term)

    search_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Search']"))
    )
    search_button.click()

    time.sleep(2)

    try:
        results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='applicationDetails.do?keyVal=']"))
        )
        for link in results:
            href = link.get_attribute("href")
            if "keyVal=" in href:
                keyval = href.split("keyVal=")[1].split("&")[0]
                found_ids.add(keyval)
    except:
        print("  No results or timeout.")

driver.quit()

with open(OUTPUT_FILE, "w") as f:
    for keyval in sorted(found_ids):
        f.write(f"{keyval}\n")

print(f"\n✅ Collected {len(found_ids)} application IDs into {OUTPUT_FILE}")
