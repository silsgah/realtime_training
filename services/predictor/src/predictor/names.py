from loguru import logger


def get_mlflow_experiment_name(
    pair: str, days_in_pass: int, candle_seconds: int, prediction_horizon_seconds: int
) -> str:
    # Sanitize pair to avoid unsafe characters
    sanitized_pair = pair.replace('/', '_').replace(':', '_')

    logger.info(
        f'Setting up MLflow experiment for pair={sanitized_pair}, '
        f'days_in_pass={days_in_pass}, candle_seconds={candle_seconds}, '
        f'prediction_horizon_seconds={prediction_horizon_seconds}'
    )

    return f'{sanitized_pair}_{days_in_pass}d_{candle_seconds}s_{prediction_horizon_seconds}s'
