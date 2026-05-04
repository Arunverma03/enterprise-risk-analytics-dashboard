import pandas as pd


def load_data(file_path):
    """Load raw risk event data from CSV."""
    df = pd.read_csv(file_path)
    return df


def clean_data(df):
    """Clean and prepare risk event data."""
    df = df.copy()

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove rows with critical missing values
    df = df.dropna(subset=["date", "event_summary", "category", "impact_level", "country", "city"])

    # Clean text columns
    text_columns = [
        "event_summary",
        "recommended_action",
        "category",
        "event_type",
        "impact_level",
        "country",
        "city",
    ]

    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()

    # Convert coordinates
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    return df


def save_clean_data(df, output_path):
    """Save cleaned data to CSV."""
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    input_path = "data/risk_events.csv"
    output_path = "data/cleaned_risk_events.csv"

    data = load_data(input_path)
    cleaned_data = clean_data(data)
    save_clean_data(cleaned_data, output_path)

    print("Data cleaning completed successfully.")
    print(f"Cleaned rows: {len(cleaned_data)}")
    print(f"Cleaned file saved at: {output_path}")