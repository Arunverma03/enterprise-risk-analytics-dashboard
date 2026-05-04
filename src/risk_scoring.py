import pandas as pd


IMPACT_SCORE_MAP = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}


CATEGORY_SCORE_MAP = {
    "Infrastructure": 2,
    "Civil Unrest": 3,
    "Natural Hazard": 3,
    "Industrial Incident": 4,
    "Security": 4
}


def calculate_risk_score(row):
    impact_score = IMPACT_SCORE_MAP.get(row["impact_level"], 1)
    category_score = CATEGORY_SCORE_MAP.get(row["category"], 1)

    risk_score = impact_score * category_score

    return risk_score


def assign_risk_rating(score):
    if score >= 12:
        return "Critical"
    elif score >= 8:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"


def add_risk_scores(df):
    df = df.copy()

    df["risk_score"] = df.apply(calculate_risk_score, axis=1)
    df["risk_rating"] = df["risk_score"].apply(assign_risk_rating)

    df["alert_priority_score"] = df["risk_score"] * 10

    return df


if __name__ == "__main__":
    input_path = "data/cleaned_risk_events.csv"
    output_path = "data/scored_risk_events.csv"

    df = pd.read_csv(input_path)
    scored_df = add_risk_scores(df)
    scored_df.to_csv(output_path, index=False)

    print("Risk scoring completed successfully.")
    print(f"Scored rows: {len(scored_df)}")
    print(f"Scored file saved at: {output_path}")