import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

SEARCH_TERMS = [
    "London Dock",
    "1 Virginia Street",
    "News International",
    "Wood Wharf",
    "Canary Wharf Group",
    "South Quay Plaza"
]

BASE_SEARCH_URL = "https://development.towerhamlets.gov.uk/online-applications/search.do?action=simple"
OUTPUT_FILE = "application_ids.txt"

options = uc.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--no-sandbox")

driver = uc.Chrome(options=options, headless=True)
wait = WebDriverWait(driver, 15)

found_ids = set()

for term in SEARCH_TERMS:
    print(f"\nSearching for: {term}")
    driver.get(BASE_SEARCH_URL)

    try:
        search_box = wait.until(EC.presence_of_element_located((By.ID, "simpleSearchString")))
        search_box.clear()
        search_box.send_keys(term)

        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Search']"))
        )
        search_button.click()

        print("  Submitting search, waiting for response...")
        time.sleep(2)

        print("  Page title after submit:", driver.title)

        # Save the full page HTML for inspection
        html_file = f"debug_{term.replace(' ', '_')}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"  Saved page to: {html_file}")

        # Try to extract application links
        results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='applicationDetails.do?keyVal=']"))
        )
        for link in results:
            href = link.get_attribute("href")
            if "keyVal=" in href:
                keyval = href.split("keyVal=")[1].split("&")[0]
                found_ids.add(keyval)

    except Exception as e:
        print(f"  No results or error: {e}")

driver.quit()

with open(OUTPUT_FILE, "w") as f:
    for keyval in sorted(found_ids):
        f.write(f"{keyval}\n")

print(f"\n Collected {len(found_ids)} application IDs into {OUTPUT_FILE}")
