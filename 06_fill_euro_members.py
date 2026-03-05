import pandas as pd

EU_MEMBERS = ["France", "Germany", "Italy"]

def main():
    tidy = pd.read_csv("macro_tidy_long.csv")

    latest_year = tidy["year"].max()

    # Get Euro Area policy rate value (for latest year)
    euro_rate = tidy[
        (tidy["year"] == latest_year)
        & (tidy["country"] == "Euro Area")
        & (tidy["indicator"] == "Policy rate (current, %)")
    ]["value"]

    if euro_rate.empty:
        raise RuntimeError("Euro Area policy rate row not found in macro_tidy_long.csv")

    euro_rate_value = float(euro_rate.iloc[0])

    # Add missing member rows if they don't exist
    for c in EU_MEMBERS:
        exists = not tidy[
            (tidy["year"] == latest_year)
            & (tidy["country"] == c)
            & (tidy["indicator"] == "Policy rate (current, %)")
        ].empty

        if not exists:
            tidy = pd.concat(
                [tidy, pd.DataFrame([{
                    "date": f"{latest_year}-01-01",
                    "year": latest_year,
                    "country": c,
                    "value": euro_rate_value,
                    "indicator": "Policy rate (current, %)"
                }])],
                ignore_index=True
            )

    tidy.to_csv("macro_tidy_long.csv", index=False)
    print("Updated macro_tidy_long.csv (filled Euro members with ECB rate)")

if __name__ == "__main__":
    main()