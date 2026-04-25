from sklearn.metrics import (accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score, mean_absolute_error, mean_squared_error, precision_score, recall_score,)
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
    Evaluate multi-class classification model for next-hour rain prediction.
    """

    accuracy = accuracy_score(y_true, y_pred)
    balanced_accuracy = balanced_accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    labels = [0, 1, 2]
    label_names = ["No Rain", "Light Rain", "Moderate/Heavy Rain"]

    print("\nRain Model Evaluation")
    print("-----------------------------")
    print(f"Accuracy : {accuracy:.3f}")
    print(f"Balanced Accuracy  : {balanced_accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall   : {recall:.3f}")
    print(f"F1 Score : {f1:.3f}")
    print(f"Macro F1 Score     : {macro_f1:.3f}")

    print("\nConfusion Matrix")
    print("Rows = actual, columns = predicted")
    print(confusion_matrix(y_true, y_pred, labels=labels))

    print("\nPer-Class Report")
    print(classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=label_names,
        zero_division=0,
    ))

    return {
        "accuracy": accuracy,
        "balanced_accuracy": balanced_accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "macro_f1": macro_f1,
    }