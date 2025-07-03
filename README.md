# Satellite View Screenshot Tool with Selenium

Python script that opens Google Maps in satellite view for a given list of coordinates, disables labels, zooms out, captures a clean screenshot, and saves an image of just the map. 


## What It Does

- Opens Google Maps at specified coordinates (in satellite mode)
- Disables map labels for clean imagery
- Zooms out slightly for better framing
- Saves the satellite image to `output/`

## Requirements

- Python 3.7 or higher
- Google Chrome installed
- ChromeDriver (matching your Chrome version)

Note: the script points to the locally installed ChromeDriver version 137. For more info: [Download ChromeDriver](https://developer.chrome.com/docs/chromedriver/downloads)

### Python packages:

```
pip install selenium pillow webdriver-manager
```

## How To Use:

1. Clone or download this repo.
2. Update your chromedriver_path in the script to point to where your ChromeDriver is located:
```
chromedriver_path = r"C:\Path\To\chromedriver.exe"
```

3. Run the script:

```
python extract-image.py
```

Your screenshots will be saved inside the output/ directory.

**NOTE:** This tool is intended for educational and research purposes ONLY. Please respect Google Maps Terms of Service.
