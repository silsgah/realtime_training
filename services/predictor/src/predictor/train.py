"""
The training script for the predictor service.

Has the following steps:
1. Fetch data from RisingWave
2. Add target column
3. Validate the data
4. Profile it
5. Split into train/test
6. Baseline model
7. XGBoost model with default hyperparameters
8. Validate final model
9. Push model
10. Hyperparameter tuning
"""

import os
from typing import Optional

import great_expectations as ge
import mlflow
import pandas as pd
from data_validation import validate_data
from dotenv import load_dotenv
from loguru import logger
from model_registry import get_model_name, push_model
from models import BaselineModel, get_model_candidates, get_model_obj
from risingwave import OutputFormat, RisingWave, RisingWaveConnOptions
from sklearn.metrics import mean_absolute_error

# Load environment variables from .env.local
load_dotenv(dotenv_path='.env.local')


def validate_ts_data(ts_data: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the technical indicators data.
    """
    ge_df = ge.from_pandas(ts_data)
    validation_result = ge_df.expect_column_values_to_be_between(
        column='close', min_value=0
    )
    if not validation_result.success:
        raise Exception('Column "close has values less than zero')


def generate_exploratory_data_analysis_report(
    ts_data: pd.DataFrame,
    output_html_path: str,
):
    """
    Generates an exploratory data analysis report for the technical indicators data.
    """
    from ydata_profiling import ProfileReport

    profile = ProfileReport(
        ts_data, tsmode=True, sortby='window_start_ms', title='Technical indicators EDA'
    )
    profile.to_file(output_html_path)


def load_ts_data_from_risingwave(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
    pair: str,
    days_in_pass: int,
    candle_seconds: int,
) -> pd.DataFrame:
    """
    Fetches technical indicators data from RisingWave for the given pair and time range.

    Args:
        host: str: The host of the RisingWave instance.
        port: int: The port of the RisingWave instance.
        user: str: The user to connect to RisingWave.
        password: str: The password to connect to RisingWave.
        database: str: The database to connect to RisingWave.
        pair: str: The trading pair to fetch data for.
        training_data_horizon_days: int: The number of days in the past to fetch data for.
        candle_seconds: int: The candle duration in seconds.

    Returns:
        pd.DataFrame: A DataFrame containing the technical indicators data for the given pair.
    """
    logger.info('Establishing connection to RisingWave')
    rw = RisingWave(
        RisingWaveConnOptions.from_connection_info(
            host=host, port=port, user=user, password=password, database=database
        )
    )
    query = f"""
    select
        *
    from
        public.technical_indicators
    where
        pair='{pair}'
        and candle_seconds='{candle_seconds}'
        and to_timestamp(window_start_ms / 1000) > now() - interval '{days_in_pass} days'
    order by
        window_start_ms;
    """

    ts_data = rw.fetch(query, format=OutputFormat.DATAFRAME)

    logger.info(
        f'Fetched {len(ts_data)} rows of data for {pair} in the last {days_in_pass} days'
    )

    return ts_data


def train(
    mlflow_tracking_uri: str,
    risingwave_host: str,
    risingwave_port: int,
    risingwave_user: str,
    risingwave_password: str,
    risingwave_database: str,
    risingwave_table: str,
    pair: str,
    training_data_horizon_days: int,
    candle_seconds: int,
    prediction_horizon_seconds: int,
    train_test_split_ratio: float,
    max_percentage_rows_with_missing_values: float,
    eda_report_html_path: str,
    data_profiling_n_rows: int,
    features: list[str],
    hyperparam_search_trials: int,
    model_name: Optional[str] = 'HuberRegressor',
    n_model_candidates: Optional[int] = 1,
    max_percentage_diff_mae_wrt_baseline: Optional[float] = 0.10,
):
    """
    Trains a predictor for the given pair and data, and if the model is good, it pushes
    it to the model registry.
    """

    logger.info(f'MLflow user: {os.getenv("MLFLOW_TRACKING_USERNAME")}')
    logger.info(f'MLflow password: {os.getenv("MLFLOW_TRACKING_PASSWORD")}')
    logger.info('Starting training process')
    logger.info('Setting up MLflow tracking URI')
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    logger.info(f"Setting up MLflow URI '{mlflow_tracking_uri}'")
    from names import get_mlflow_experiment_name

    mlflow_experiment_name = get_mlflow_experiment_name(
        pair, training_data_horizon_days, candle_seconds, prediction_horizon_seconds
    )
    logger.info(f"Setting up MLflow experiment with name '{mlflow_experiment_name}'")
    mlflow.set_experiment(mlflow_experiment_name)
    with mlflow.start_run():
        logger.info('Starting MLflow run')
        mlflow.log_param('features', features)
        mlflow.log_param('pair', pair)
        mlflow.log_param('candle_seconds', candle_seconds)
        mlflow.log_param('training_data_horizon_days', training_data_horizon_days)
        mlflow.log_param('prediction_horizon_seconds', prediction_horizon_seconds)
        mlflow.log_param('train_test_split_ratio', train_test_split_ratio)
        mlflow.log_param('data_profiling_n_rows', data_profiling_n_rows)
        mlflow.log_param('features', features)
        if model_name:
            mlflow.log_param('model_name', model_name)
        mlflow.log_param(
            'max_percentage_diff_mae_wrt_baseline', max_percentage_diff_mae_wrt_baseline
        )

        # Step 1. Load technical indicators data from RisingWave
        ts_data = load_ts_data_from_risingwave(
            host=risingwave_host,
            port=risingwave_port,
            user=risingwave_user,
            password=risingwave_password,
            database=risingwave_database,
            table=risingwave_table,
            pair=pair,
            days_in_pass=training_data_horizon_days,
            candle_seconds=candle_seconds,
        )
        logger.info(f'Loaded data shape: {ts_data.shape}')
        logger.info('Add target column')
        ts_data = ts_data[features]
        # step 2. Add target column
        ts_data['target'] = ts_data['close'].shift(
            -prediction_horizon_seconds // candle_seconds
        )
        ts_data = ts_data.dropna(subset=['target'])
        # step 3. Validate the data
        # log the data to MLflow
        logger.info('log the data to MLflow')
        dataset = mlflow.data.from_pandas(ts_data)
        mlflow.log_input(dataset, context='training')
        if ts_data.empty:
            raise ValueError('No data returned from RisingWave. Aborting training.')
        # log dataset size
        from sklearn.impute import SimpleImputer

        imputer = SimpleImputer(strategy='mean')  # or median, depending on your data
        ts_data[features] = imputer.fit_transform(ts_data[features])
        ts_data = validate_data(ts_data, max_percentage_rows_with_missing_values)
        validate_ts_data(ts_data)

        from data_validation import generate_data_drift_report

        generate_data_drift_report(ts_data, model_name)
        ts_data_to_profile = (
            ts_data.head(data_profiling_n_rows) if data_profiling_n_rows else ts_data
        )
        logger.info('Pushing EDA report to MLflow')
        # step 4. Profile the data
        generate_exploratory_data_analysis_report(
            ts_data_to_profile, output_html_path=eda_report_html_path
        )
        mlflow.log_artifact(local_path=eda_report_html_path, artifact_path='eda_report')
        # step 5. Split into train/test
        logger.info(f'Rows before dropna: {len(ts_data)}')
        ts_data = ts_data.dropna(
            subset=['sma_7', 'sma_14', 'sma_21', 'sma_60', 'ema_7', 'ema_14']
        )
        logger.info(f'Rows after dropna: {len(ts_data)}')
        logger.info('Checking for NaNs in features...')
        train_size = int(len(ts_data) * train_test_split_ratio)
        train_data = ts_data[:train_size]
        test_data = ts_data[train_size:]
        mlflow.log_param('train_data_shape', train_data.shape)
        mlflow.log_param('test_data_shape', test_data.shape)
        # split data into features and target
        # Step 6. Split data into features and target
        # Step 6. Split data into features and target
        X_train = train_data.drop(columns=['target'])
        y_train = train_data['target']
        X_test = test_data.drop(columns=['target'])
        y_test = test_data['target']
        mlflow.log_param('X_train_shape', X_train.shape)
        mlflow.log_param('y_train_shape', y_train.shape)
        mlflow.log_param('X_test_shape', X_test.shape)
        mlflow.log_param('y_test_shape', y_test.shape)
        # Step 7. Build a dummy baseline model
        baseline_model = BaselineModel()
        y_pred = baseline_model.predict(X_test)
        test_mae_baseline = mean_absolute_error(y_test, y_pred)
        mlflow.log_metric('test_mae_baseline', test_mae_baseline)
        logger.info(f'Test MAE for Baseline model: {test_mae_baseline:.4f}')
        # step 8.
        if model_name is None:
            model_names = get_model_candidates(
                X_train, y_train, X_test, y_test, n_candidates=n_model_candidates
            )
            model_name = model_names[0]

        model = get_model_obj(model_name)

        # step 9. Validate final model
        logger.info(f'Start training model {model} with hyperparameter search')
        model.fit(X_train, y_train, hyperparam_search_trials=hyperparam_search_trials)
        # validate the model
        y_pred = model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_pred)
        mlflow.log_metric('test_mae', test_mae)
        logger.info(f'TEST MAE for model {model}: {test_mae:.4f}')
        logger.info('Pushing model to the registry')
        mae_diff = (test_mae - test_mae_baseline) / test_mae_baseline
        if mae_diff <= max_percentage_diff_mae_wrt_baseline:
            logger.info(
                f'Model MAE is {mae_diff:.4f} < {max_percentage_diff_mae_wrt_baseline}'
            )
            logger.info('Pushing model to the registry')
            model_name = get_model_name(
                pair, candle_seconds, prediction_horizon_seconds
            )
            push_model(model, X_test, model_name)
        else:
            logger.info(
                f'The model {model_name} MAE is {mae_diff:.4f} > {max_percentage_diff_mae_wrt_baseline}'
            )
            logger.info('Model NOT PUSHED to the registry')


if __name__ == '__main__':
    from config import training_config as config

    train(
        mlflow_tracking_uri=config.mlflow_tracking_uri,
        risingwave_host=config.risingwave_host,
        risingwave_port=config.risingwave_port,
        risingwave_user=config.risingwave_user,
        risingwave_password=config.risingwave_password,
        risingwave_database=config.risingwave_database,
        risingwave_table=config.risingwave_table,
        pair=config.pair,
        training_data_horizon_days=config.training_data_horizon_days,
        candle_seconds=config.candle_seconds,
        prediction_horizon_seconds=config.prediction_horizon_seconds,
        train_test_split_ratio=config.train_test_split_ratio,
        max_percentage_rows_with_missing_values=config.max_percentage_rows_with_missing_values,
        data_profiling_n_rows=config.data_profiling_n_rows,
        eda_report_html_path=config.eda_report_html_path,
        features=config.features,
        hyperparam_search_trials=config.hyperparam_search_trials,
        model_name=config.model_name,
        n_model_candidates=config.n_model_candidates,
        max_percentage_diff_mae_wrt_baseline=config.max_percentage_diff_mae_wrt_baseline,
    )
