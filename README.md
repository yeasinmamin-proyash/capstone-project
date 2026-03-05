# Monetary Policy vs Inflation (2010–2025) — Selenium + Tableau

This capstone project scrapes macroeconomic data using Selenium and visualizes results in Tableau Public.

## Topic
Compare annual inflation trends (2010–2025) across major economies and relate them to current central bank policy rates (a simple “real rate” proxy = policy rate − inflation).

## Countries
Canada, France, Germany, Italy, Japan, United Kingdom, United States, Euro Area, Australia

## Data Source
Global-Rates:
- Historical inflation pages 
- Central bank policy rates table

## How to Run (VS Code)
1) Create venv + install packages:
```bash
py -m venv .venv
.venv\Scripts\activate
pip install selenium webdriver-manager pandas lxml
