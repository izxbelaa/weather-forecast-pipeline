from sklearn.metrics import (mean_absolute_error, mean_squared_error, accuracy_score, precision_score, recall_score, f1_score)
import numpy as np


def evaluate_temperature_model(y_true, y_pred):
    """
    Evaluate regression model for temperature prediction.
    """

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)

    print("\nTemperature Model Evaluation")
    print("-----------------------------")
    print(f"MAE  (Mean Absolute Error): {mae:.3f}")
    print(f"MSE  (Mean Squared Error):  {mse:.3f}")
    print(f"RMSE (Root MSE):           {rmse:.3f}")

    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse
        }


def evaluate_rain_model(y_true, y_pred):
    """
    Evaluate classification model for next-hour rain prediction.
    """

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print("\nRain Model Evaluation")
    print("-----------------------------")
    print(f"Accuracy : {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall   : {recall:.3f}")
    print(f"F1 Score : {f1:.3f}")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }