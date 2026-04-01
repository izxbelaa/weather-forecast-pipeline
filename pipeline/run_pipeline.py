import subprocess
import sys


def run_step(module_name: str, label: str) -> None:
    print(f"\n--- Running: {label} ---")
    subprocess.run([sys.executable, "-m", module_name], check=True)


def main() -> None:
    run_step("backend.data_collector", "Data Collection")
    run_step("models.train_temp_model", "Temperature Model")
    run_step("models.train_rain_model", "Rain Model")
    run_step("models.generate_predictions", "Generate Predictions")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()