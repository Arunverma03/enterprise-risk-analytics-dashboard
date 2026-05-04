from src.data_cleaning import load_data, clean_data, save_clean_data
from src.risk_scoring import add_risk_scores
from src.database import save_to_database


RAW_DATA_PATH = "data/risk_events.csv"
CLEANED_DATA_PATH = "data/cleaned_risk_events.csv"
SCORED_DATA_PATH = "data/scored_risk_events.csv"


def run_pipeline():
    print("Starting Enterprise Risk Analytics Pipeline...")

    raw_df = load_data(RAW_DATA_PATH)
    print(f"Raw data loaded: {len(raw_df)} rows")

    cleaned_df = clean_data(raw_df)
    save_clean_data(cleaned_df, CLEANED_DATA_PATH)
    print(f"Cleaned data saved: {len(cleaned_df)} rows")

    scored_df = add_risk_scores(cleaned_df)
    scored_df.to_csv(SCORED_DATA_PATH, index=False)
    print(f"Risk scoring completed: {len(scored_df)} rows")

    save_to_database(SCORED_DATA_PATH)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()