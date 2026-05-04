import pandas as pd
from sqlalchemy import create_engine


DATABASE_PATH = "database/risk_analytics.db"
TABLE_NAME = "risk_events"


def get_engine():
    """Create SQLite database engine."""
    return create_engine(f"sqlite:///{DATABASE_PATH}")


def save_to_database(csv_path):
    """Save scored risk events into SQLite database."""
    df = pd.read_csv(csv_path)

    engine = get_engine()

    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists="replace",
        index=False
    )

    print("Data saved to database successfully.")
    print(f"Rows inserted: {len(df)}")
    print(f"Database path: {DATABASE_PATH}")


def load_from_database():
    """Load risk events from SQLite database."""
    engine = get_engine()
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", engine)
    return df


if __name__ == "__main__":
    save_to_database("data/scored_risk_events.csv")

    loaded_df = load_from_database()
    print("\nPreview from database:")
    print(loaded_df.head())