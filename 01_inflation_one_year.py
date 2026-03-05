import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


TARGETS = {
    "Canada": ("Canada", "CPI"),
    "France": ("France", "CPI"),
    "Germany": ("Germany", "CPI"),
    "Italy": ("Italy", "CPI"),
    "Japan": ("Japan", "CPI"),
    "United Kingdom": ("United Kingdom", "CPI"),
    "United States": ("United States", "CPI"),
    "Euro Area": ("Europe", "HICP"),   # Global-Rates uses "Europe" for Euro-area line
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
    # Find the table whose header contains: Country/Region, Type, Average
    tables = driver.find_elements(By.TAG_NAME, "table")
    for t in tables:
        header_text = t.text.lower()
        if ("country" in header_text) and ("type" in header_text) and ("average" in header_text):
            return t
    raise RuntimeError("Could not find the inflation table.")

def main():
    YEAR = 2020
    url = f"https://www.global-rates.com/en/inflation/historical/{YEAR}/"

    driver = make_driver(headless=True)
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        table = find_target_table(driver)
        rows = table.find_elements(By.TAG_NAME, "tr")

        # Identify columns by header row (first tr with th)
        header_cells = rows[0].find_elements(By.TAG_NAME, "th")
        headers = [c.text.strip() for c in header_cells]

        # Build a mapping: column name -> index
        def col_index(keywords):
            for i, h in enumerate(headers):
                hl = h.lower()
                if any(k in hl for k in keywords):
                    return i
            return None

        idx_country = col_index(["country"])
        idx_type = col_index(["type"])
        idx_avg = col_index(["average"])

        if idx_country is None or idx_type is None or idx_avg is None:
            raise RuntimeError(f"Header columns not found. Headers: {headers}")

        data = []
        # start from row 1 because row 0 is header
        for r in rows[1:]:
            tds = r.find_elements(By.TAG_NAME, "td")
            if len(tds) < max(idx_country, idx_type, idx_avg) + 1:
                continue

            country_label = tds[idx_country].text.strip()
            infl_type = tds[idx_type].text.strip()
            avg = tds[idx_avg].text.strip()

            # check if this row is one we need
            for out_country, (match_country, match_type) in TARGETS.items():
                if country_label == match_country and infl_type == match_type:
                    data.append({
                        "year": YEAR,
                        "country": out_country,
                        "inflation_type": infl_type,
                        "inflation_avg_percent": parse_percent(avg),
                        "source_url": url,
                    })

        df = pd.DataFrame(data)
        df.to_csv("inflation_2020.csv", index=False, encoding="utf-8")
        print("Saved inflation_2020.csv")
        print(df)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()