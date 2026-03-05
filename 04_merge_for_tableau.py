import pandas as pd

def main():
    infl = pd.read_csv("inflation_annual_2010_2025.csv")
    rates = pd.read_csv("policy_rates_current.csv")

    latest_year = infl["year"].max()
    latest = infl[infl["year"] == latest_year][["country", "inflation_avg_percent"]]

    merged = latest.merge(rates, on="country", how="left")
    merged["real_rate_proxy"] = merged["current_policy_rate_percent"] - merged["inflation_avg_percent"]
    merged.to_csv("latest_inflation_vs_policy_rate.csv", index=False)

    print("Saved latest_inflation_vs_policy_rate.csv")

if __name__ == "__main__":
    main()