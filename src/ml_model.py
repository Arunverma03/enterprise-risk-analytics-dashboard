import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib


DATA_PATH = "data/scored_risk_events.csv"
MODEL_PATH = "models/risk_rating_model.pkl"


def train_model():
    df = pd.read_csv(DATA_PATH)

    features = ["category", "event_type", "impact_level", "country", "city"]
    target = "risk_rating"

    X = df[features]
    y = df[target]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), features)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    print("Model training completed.")
    print(f"Accuracy: {accuracy_score(y_test, predictions):.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    joblib.dump(pipeline, MODEL_PATH)

    print(f"Model saved at: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()