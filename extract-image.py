import time
import os
import csv
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def disable_labels(driver):
    wait = WebDriverWait(driver, 10)
    try:
        map_div = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.yHc72[aria-label="Interactive map"]')
        ))
        webdriver.ActionChains(driver).move_to_element(map_div).perform()
        time.sleep(1)
    except Exception as e:
        print("[WARN] hover failed:", e)
    try:
        more = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[jsaction="layerswitcher.quick.more"]')
        ))
        more.click()
        time.sleep(1)
    except Exception as e:
        print("[WARN] open layers failed:", e)
        return
    try:
        labels = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//button[@jsaction="layerswitcher.intent.labels"]')
        ))
        if labels.get_attribute("aria-checked") == "true":
            labels.click()
            time.sleep(1)
    except Exception:
        pass
    try:
        close_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[jsaction="layerswitcher.close"]')
        ))
        close_btn.click()
        time.sleep(1)
    except Exception:
        pass

INPUT_CSV    = "input.csv"
OUTPUT_DIR   = "output"
WAIT_SECONDS = 5
ZOOM_METERS  = 16

os.makedirs(OUTPUT_DIR, exist_ok=True)

#chrome setup
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.120 Safari/537.36"
)

# manually point to chrome driver (ver138)
chromedriver_path = r"C:\Users\Dell\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
service = Service(chromedriver_path)
driver  = webdriver.Chrome(service=service, options=chrome_options)

def capture_satellite_map(row_num, lat, lon):
    print(f"[INFO] row {row_num}: capturing map at ({lat}, {lon})")
    url = f"https://www.google.com/maps/@{lat},{lon},{ZOOM_METERS}m/data=!3m1!1e3"
    driver.get(url)
    time.sleep(5)
    disable_labels(driver)
    time.sleep(2)
    for _ in range(2):
        try:
            driver.find_element(By.ID, "widget-zoom-out").click()
            time.sleep(1)
        except Exception:
            break
    time.sleep(WAIT_SECONDS)
    temp_path = os.path.join(OUTPUT_DIR, f"full_row{row_num}.png")
    driver.save_screenshot(temp_path)
    try:
        scene = driver.find_element(By.ID, 'scene')
        loc, sz = scene.location, scene.size
        img = Image.open(temp_path)
        left, top = int(loc['x']), int(loc['y'])
        right = left + int(sz['width'])
        bottom= top  + int(sz['height'])
        cropped = img.crop((left, top, right, bottom))
        out_name = f"sat_row{row_num}_{lat:.6f}_{lon:.6f}.png"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        cropped.save(out_path)
        os.remove(temp_path)
        print(f"[✅] saved {out_name}")
    except Exception as e:
        print(f"[ERROR] cropping failed for row {row_num}:", e)

with open(INPUT_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row_num, row in enumerate(reader, start=1):
        latlon = row.get("Lat, Long", "").strip()
        if not latlon or ',' not in latlon:
            print(f"[WARNING] skipping row {row_num}: invalid 'Lat, Long' format → '{latlon}'")
            continue
        try:
            lat_str, lon_str = latlon.split(",", 1)
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
        except Exception:
            print(f"[WARNING] skipping row {row_num}: unable to parse lat/lon → '{latlon}'")
            continue
        capture_satellite_map(row_num, lat, lon)

driver.quit()
print("DONE.")
