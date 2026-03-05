import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

START_YEAR = 2010
END_YEAR = 2025

TARGETS = {
    "Canada": ("Canada", "CPI"),
    "France": ("France", "CPI"),
    "Germany": ("Germany", "CPI"),
    "Italy": ("Italy", "CPI"),
    "Japan": ("Japan", "CPI"),
    "United Kingdom": ("United Kingdom", "CPI"),
    "United States": ("United States", "CPI"),
    "Euro Area": ("Europe", "HICP"),
    "Australia": ("Australia", "CPI"),
}

def make_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,1000")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_percent(s: str):
    s = (s or "").strip().replace("%", "").replace(",", ".")
    try:
        return float(s)
    except:
        return None

def find_target_table(driver):
    tables = driver.find_elements(By.TAG_NAME, "table")
    for t in tables:
        tx = t.text.lower()
        if ("country" in tx) and ("type" in tx) and ("average" in tx):
            return t
    raise RuntimeError("Could not find the inflation table.")

def scrape_year(driver, year: int):
    url = f"https://www.global-rates.com/en/inflation/historical/{year}/"
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    table = find_target_table(driver)
    rows = table.find_elements(By.TAG_NAME, "tr")

    header_cells = rows[0].find_elements(By.TAG_NAME, "th")
    headers = [c.text.strip() for c in header_cells]

    def col_index(keywords):
        for i, h in enumerate(headers):
            hl = h.lower()
            if any(k in hl for k in keywords):
                return i
        return None

    idx_country = col_index(["country"])
    idx_type = col_index(["type"])
    idx_avg = col_index(["average"])

    out = []
    for r in rows[1:]:
        tds = r.find_elements(By.TAG_NAME, "td")
        if not tds:
            continue
        if len(tds) <= max(idx_country, idx_type, idx_avg):
            continue

        country_label = tds[idx_country].text.strip()
        infl_type = tds[idx_type].text.strip()
        avg = tds[idx_avg].text.strip()

        for out_country, (match_country, match_type) in TARGETS.items():
            if country_label == match_country and infl_type == match_type:
                out.append({
                    "year": year,
                    "country": out_country,
                    "inflation_type": infl_type,
                    "inflation_avg_percent": parse_percent(avg),
                    "source_url": url,
                })

    return out

def main():
    driver = make_driver(headless=True)
    all_rows = []
    try:
        for year in range(START_YEAR, END_YEAR + 1):
            print("Scraping year:", year)
            try:
                all_rows.extend(scrape_year(driver, year))
            except Exception as e:
                print("FAILED year", year, "->", e)
            time.sleep(0.4)
    finally:
        driver.quit()

    df = pd.DataFrame(all_rows)
    df.to_csv("inflation_annual_2010_2025.csv", index=False, encoding="utf-8")
    print("Saved inflation_annual_2010_2025.csv")

if __name__ == "__main__":
    main()