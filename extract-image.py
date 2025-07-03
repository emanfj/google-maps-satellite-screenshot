import time
import os
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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
        print("[WARN] Couldn't hover over map:", e)

    try:
        more_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[jsaction="layerswitcher.quick.more"]')
        ))
        more_button.click()
        time.sleep(1)
    except Exception as e:
        print("[ERROR] Couldn't click More button:", e)
        return

    #toggle off labels if currently checked
    try:
        labels_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//button[@jsaction="layerswitcher.intent.labels"]')
        ))
        if labels_button.get_attribute("aria-checked") == "true":
            print("[INFO] Labels are ON → turning OFF")
            labels_button.click()
            time.sleep(1)
        else:
            print("[INFO] Labels already OFF")
    except Exception as e:
        print("[ERROR] Couldn't access Labels button:", e)

    try:
        close_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[jsaction="layerswitcher.close"]')
        ))
        close_button.click()
        time.sleep(1)
    except Exception as e:
        print("[WARN] Couldn't close Layers menu:", e)

COORDINATES_LIST = [
    (33.6844, 73.0479),     #islamabad
    (40.7128, -74.0060)     #NYC
]
OUTPUT_DIR   = "output"
WAIT_SECONDS = 5
ZOOM_METERS  = 16  # 

#chrome setup
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
#chrome_options.add_argument("--headless=new")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.120 Safari/537.36"
)

chromedriver_path = r"C:\Users\Dell\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
service = Service(chromedriver_path)
driver  = webdriver.Chrome(service=service, options=chrome_options)

def capture_satellite_map(lat, lon, index):
    print(f"[INFO] Capturing satellite map for ({lat}, {lon})...")

    url = f"https://www.google.com/maps/@{lat},{lon},{ZOOM_METERS}m/data=!3m1!1e3"
    driver.get(url)
    time.sleep(5)

    disable_labels(driver)
    time.sleep(3)

    #zoom out twice to reach ~20m scale
    for _ in range(2):
        try:
            zoom_out = driver.find_element(By.ID, "widget-zoom-out")
            zoom_out.click()
            time.sleep(1)
        except Exception as e:
            print("[ERROR] zoom-out failed:", e)

    time.sleep(WAIT_SECONDS)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    screenshot_path = os.path.join(OUTPUT_DIR, f"full_{index}.png")
    driver.save_screenshot(screenshot_path)

    try:
        map_div = driver.find_element(By.ID, 'scene')
        loc = map_div.location
        sz  = map_div.size

        img   = Image.open(screenshot_path)
        left  = int(loc['x'])
        top   = int(loc['y'])
        right = left + int(sz['width'])
        bottom= top  + int(sz['height'])

        cropped_image = img.crop((left, top, right, bottom))
        final_path = os.path.join(OUTPUT_DIR, f"satellite_{index}_{lat}_{lon}.png")
        cropped_image.save(final_path)
        os.remove(screenshot_path)
        print(f"[✅] Saved: {final_path}")
    except Exception as e:
        print(f"[ERROR] Cropping failed: {e}")

for idx, (lat, lon) in enumerate(COORDINATES_LIST):
    capture_satellite_map(lat, lon, idx)

driver.quit()
print("[DONE] All maps captured.")
