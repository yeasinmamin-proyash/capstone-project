from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # remove to see browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://example.com")
    print("TITLE:", driver.title)
    driver.quit()

if __name__ == "__main__":
    main()