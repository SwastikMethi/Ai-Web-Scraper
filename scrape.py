import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse
import time
import config
import asyncio
import os
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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

# def scrape_website_playwright(url: str) -> str:
    with sync_playwright() as p:
        # Launch Chromium (bundled with Playwright)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)  # wait up to 60s
        page.wait_for_load_state("networkidle")  # wait until network is idle
        html = page.content()
        browser.close()
        return html


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

def split_cleaned_content(cleaned_content, size = config.chunk_size):
    return[
        cleaned_content[i:i+size] for i in range(0,len(cleaned_content),size)
    ]

def crawl_website(base_url, headless=True, max_pages=20, delay=1.5):
    visited = set()
    to_visit = [base_url]
    all_content = []
    domain = urlparse(base_url).netloc

    print(f"Starting crawl for {base_url} (max {max_pages} pages)...")

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        print(f"[{len(visited)+1}/{max_pages}] Scraping: {url}")
        try:
            html = scrape_website(url, headless=config.headless)
            visited.add(url)

            # Extract and clean content
            body = extract_body_content(html)
            cleaned = clean_body_content(body)
            all_content.append(f"--- PAGE: {url} ---\n{cleaned}\n\n")

            yield len(visited), url, cleaned

            # Find all internal links
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                full_link = urljoin(base_url, a["href"])
                parsed = urlparse(full_link)
                if parsed.netloc == domain and full_link not in visited and full_link not in to_visit:
                    to_visit.append(full_link)

            time.sleep(delay)  # Avoid hammering the site
        except Exception as e:
            print(f"⚠️ Error scraping {url}: {e}")
            continue

    yield "done", f"Crawled {len(visited)} pages successfully.", "\n".join(all_content)