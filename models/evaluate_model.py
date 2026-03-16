from sklearn.metrics import mean_absolute_error, mean_squared_error
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
    Evaluate regression model for next-hour precipitation prediction.
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)

    print("\nRainfall Model Evaluation")
    print("-----------------------------")
    print(f"MAE  (Mean Absolute Error): {mae:.3f} mm")
    print(f"MSE  (Mean Squared Error):  {mse:.3f} mm^2")
    print(f"RMSE (Root MSE):           {rmse:.3f} mm")

    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse
    }
    