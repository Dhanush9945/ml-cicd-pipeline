"""
ML Model Training Script for CI/CD Pipeline
Trains a Random Forest classifier on Iris dataset
"""

import argparse
import os
import json
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import boto3
import traceback


def train_model(args):
    """Train the ML model"""
    try:
        print("===== STARTING MODEL TRAINING =====")

        # 🔹 Environment debugging (VERY useful in SageMaker)
        print("\nEnvironment variables:")
        for k, v in os.environ.items():
            print(f"{k} = {v}")

        print("\nArguments received:")
        print(args)

        # 🔹 Load data
        print("\nLoading Iris dataset...")
        iris = load_iris()
        X = pd.DataFrame(iris.data, columns=iris.feature_names)
        y = pd.Series(iris.target)

        print(f"Dataset shape: {X.shape}")
        print(f"Target distribution:\n{y.value_counts()}")

        # 🔹 Split data
        print("\nSplitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")

        # 🔹 Train model
        print("\nTraining Random Forest model...")
        print(f"Hyperparameters → n_estimators={args.n_estimators}, max_depth={args.max_depth}")

        model = RandomForestClassifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=42
        )

        model.fit(X_train, y_train)
        print("Model training completed.")

        # 🔹 Evaluate
        print("\nEvaluating model...")
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        train_accuracy = accuracy_score(y_train, train_pred)
        test_accuracy = accuracy_score(y_test, test_pred)

        print(f"Training Accuracy: {train_accuracy:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")

        print("\nClassification Report:")
        print(classification_report(y_test, test_pred))

        # 🔹 Save model
        print("\nSaving model...")
        model_dir = args.model_dir
        print(f"Model directory: {model_dir}")

        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, "model.pkl")
        joblib.dump(model, model_path)

        print(f"Model saved to: {model_path}")

        # 🔹 Save metrics
        print("\nSaving metrics...")
        metrics = {
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth
        }

        metrics_path = os.path.join(model_dir, "metrics.json")
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        print(f"Metrics saved to: {metrics_path}")

        # 🔹 Quality gate
        print("\nChecking model quality...")
        if test_accuracy < 0.85:
            print(f"ERROR: Model accuracy {test_accuracy} below threshold 0.85")
            exit(1)

        print("\n===== TRAINING COMPLETED SUCCESSFULLY =====")

        return model, metrics

    except Exception as e:
        print("\n===== TRAINING FAILED =====")
        print("Error:", str(e))
        print("Traceback:")
        print(traceback.format_exc())
        raise


if __name__ == "__main__":
    print("\n===== SCRIPT START =====")

    parser = argparse.ArgumentParser()

    # Hyperparameters
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=5)

    # SageMaker specific arguments
    parser.add_argument("--model-dir", type=str,
                        default=os.environ.get("SM_MODEL_DIR", "./model"))
    parser.add_argument("--train", type=str,
                        default=os.environ.get("SM_CHANNEL_TRAIN", "./data"))
    parser.add_argument("--output-data-dir", type=str,
                        default=os.environ.get("SM_OUTPUT_DATA_DIR", "./output"))

    args = parser.parse_args()

    print("\nParsed arguments:", args)

    train_model(args)