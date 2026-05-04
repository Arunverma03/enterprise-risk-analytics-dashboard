import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


DATA_PATH = "data/scored_risk_events.csv"
MODEL_PATH = "models/risk_rating_model.pkl"


def evaluate_model():
    df = pd.read_csv(DATA_PATH)

    features = ["category", "event_type", "impact_level", "country", "city"]
    target = "risk_rating"

    X = df[features]
    y = df[target]

    model = joblib.load(MODEL_PATH)

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions)
    matrix = confusion_matrix(y_test, predictions)

    print("Model Evaluation Completed")
    print(f"Accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(report)
    print("\nConfusion Matrix:")
    print(matrix)


if __name__ == "__main__":
    evaluate_model()
    