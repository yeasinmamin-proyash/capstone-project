import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TARGETS = {
    "Canada": "Canada",
    "France": "France",
    "Germany": "Germany",
    "Italy": "Italy",
    "Japan": "Japan",
    "United Kingdom": "United Kingdom",
    "United States": "United States",
    "Euro Area": "Europe",
    "Australia": "Australia",
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

def find_rate_table(driver):
    tables = driver.find_elements(By.TAG_NAME, "table")
    for t in tables:
        tx = t.text.lower()
        if ("country" in tx) and ("current" in tx):
            return t
    raise RuntimeError("Could not find central bank rates table.")

def main():
    url = "https://www.global-rates.com/en/interest-rates/central-banks/"
    driver = make_driver(headless=True)
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        table = find_rate_table(driver)
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
        idx_current = col_index(["current"])
        idx_previous = col_index(["previous"])  # might not exist
        idx_date = col_index(["date", "change"])  # page sometimes uses "Date"

        data = []
        for r in rows[1:]:
            tds = r.find_elements(By.TAG_NAME, "td")
            if not tds or len(tds) <= max(idx_country, idx_current):
                continue

            country_label = tds[idx_country].text.strip()
            current = tds[idx_current].text.strip()

          
            for out_country, match_label in TARGETS.items():
                if country_label == match_label:
                    data.append({
                        "country": out_country,
                        "current_policy_rate_percent": parse_percent(current),
                        "previous_policy_rate_percent": parse_percent(tds[idx_previous].text.strip()) if idx_previous is not None and idx_previous < len(tds) else None,
                        "last_change": tds[idx_date].text.strip() if idx_date is not None and idx_date < len(tds) else None,
                        "source_url": url
                    })

        df = pd.DataFrame(data)
        df.to_csv("policy_rates_current.csv", index=False, encoding="utf-8")
        print("Saved policy_rates_current.csv")
        print(df)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
