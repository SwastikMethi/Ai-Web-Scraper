import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
# import undetected_chromedriver as uc
from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
# from playwright.async_api import sync_playwright
import asyncio
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def _common_headless_options(options: webdriver.ChromeOptions):
    # Modern headless flag; falls back to legacy if needed.
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")          # safe to include
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    return options

def scrape_website(url, headless: bool = True, wait_selector: str = "div.s-main-slot"):
    print("Launching chrome browser...")

    chrome_driver_path = os.path.join(BASE_DIR, "chromedriver.exe")

    options = webdriver.ChromeOptions()
    if headless:
        options = _common_headless_options(options)
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
    # service = Service(ChromeDriverManager().install())

    # driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"Scraping {url}")
        driver.get(url)
        html = driver.page_source
        return html
    except Exception as e:
        print(f"Error : {e}")
    finally:
        driver.quit()

def scrape_website_uc(url):
    print("Launching undetected Chrome...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options, use_subprocess=True, version_main=114)
    try:
        driver.get(url)
        html = driver.page_source
        return html
    finally:
        driver.quit()

# def scrape_website_playwright(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(url)
#         html = page.content()
#         browser.close()
#         return html


def extract_body_content(result):
    print("Extracting content...")
    soup = BeautifulSoup(result, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    print("Cleaning content...")
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script","style"]):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator = "\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
        )
    return cleaned_content

def split_cleaned_content(cleaned_content, size = 6000):
    return[
        cleaned_content[i:i+size] for i in range(0,len(cleaned_content),size)
    ]