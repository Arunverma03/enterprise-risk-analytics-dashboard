import pandas as pd
from datetime import datetime
from src.database import load_from_database


def generate_report():
    df = load_from_database()

    total_events = len(df)
    high_risk_events = len(df[df["risk_rating"].isin(["High", "Critical"])])
    avg_risk_score = round(df["risk_score"].mean(), 2)
    countries_affected = df["country"].nunique()

    top_category = df["category"].value_counts().idxmax()
    top_city = df["city"].value_counts().idxmax()
    max_risk_score = df["risk_score"].max()

    report = f"""
Enterprise Risk Analytics Automated Report
Generated On: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Summary Metrics:
- Total Events: {total_events}
- High/Critical Events: {high_risk_events}
- Average Risk Score: {avg_risk_score}
- Countries Affected: {countries_affected}

Key Insights:
- Most frequent risk category: {top_category}
- Most affected city: {top_city}
- Maximum risk score observed: {max_risk_score}

Recommended Action:
Prioritize High and Critical risk events, monitor affected cities closely, and allocate operational resources based on category concentration.
"""

    output_path = "reports/automated_risk_report.txt"

    with open(output_path, "w") as file:
        file.write(report)

    print("Automated report generated successfully.")
    print(f"Report saved at: {output_path}")


if __name__ == "__main__":
    generate_report()