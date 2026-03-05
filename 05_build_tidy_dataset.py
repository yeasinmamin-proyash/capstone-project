import pandas as pd

def main():
    infl = pd.read_csv("inflation_annual_2010_2025.csv")
    rates = pd.read_csv("policy_rates_current.csv")

    # Ensure correct types
    infl["year"] = infl["year"].astype(int)
    infl["inflation_avg_percent"] = pd.to_numeric(infl["inflation_avg_percent"], errors="coerce")
    rates["current_policy_rate_percent"] = pd.to_numeric(rates["current_policy_rate_percent"], errors="coerce")

    # Make a date column from year so Tableau treats it like time
    infl["date"] = pd.to_datetime(infl["year"].astype(str) + "-01-01")

    # Long format for inflation
    infl_long = infl[["date", "year", "country", "inflation_avg_percent"]].copy()
    infl_long.rename(columns={"inflation_avg_percent": "value"}, inplace=True)
    infl_long["indicator"] = "Inflation (annual avg, %)"

    # Add a “current policy rate” snapshot for the latest year (so it can live in same file)
    latest_year = infl["year"].max()
    rates_long = rates[["country", "current_policy_rate_percent"]].copy()
    rates_long.rename(columns={"current_policy_rate_percent": "value"}, inplace=True)
    rates_long["indicator"] = "Policy rate (current, %)"
    rates_long["year"] = latest_year
    rates_long["date"] = pd.to_datetime(str(latest_year) + "-01-01")

    tidy = pd.concat([infl_long, rates_long], ignore_index=True)
    tidy.to_csv("macro_tidy_long.csv", index=False, encoding="utf-8")

    print("Saved: macro_tidy_long.csv")
    print(tidy.head(10))

if __name__ == "__main__":
    main()