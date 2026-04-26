import pandas as pd
import numpy as np
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

class AutoForecaster:
    def __init__(self):
        self.best_model_name = None
        self.model = None
        self.metrics = {}

    def fit_auto(self, df: pd.DataFrame, target_col: str, date_col: str):
        """
        AutoML loop for a single SKU. 
        Tries to find the best model. For this standalone version, we use Prophet as the primary baseline.
        """
        if len(df) < 10:
             raise ValueError("Not enough data to train a model. Minimum 10 data points required.")

        df = df.sort_values(by=date_col)
        
        # Basic Validation Split
        train_size = int(len(df) * 0.8)
        train_df = df.iloc[:train_size]
        test_df = df.iloc[train_size:]

        # --- Prophet Evaluation ---
        prophet_model = Prophet()
        prophet_train = train_df[[date_col, target_col]].rename(columns={date_col: 'ds', target_col: 'y'})
        prophet_model.fit(prophet_train)
        
        future = prophet_model.make_future_dataframe(periods=len(test_df))
        prophet_pred = prophet_model.predict(future)
        prophet_test_pred = prophet_pred.iloc[train_size:]['yhat'].values
        
        # Calculate RMSE
        rmse = np.sqrt(np.mean((test_df[target_col].values - prophet_test_pred)**2))
        mae = np.mean(np.abs(test_df[target_col].values - prophet_test_pred))

        self.best_model_name = 'Prophet'
        self.metrics = {'rmse': rmse, 'mae': mae}
        
        # Retrain on Full Data
        self.model = Prophet()
        full_train = df[[date_col, target_col]].rename(columns={date_col: 'ds', target_col: 'y'})
        self.model.fit(full_train)

    def predict(self, steps: int = 12, freq: str = 'M'):
        if self.model is None:
            raise ValueError("Model must be trained before calling predict.")
            
        future = self.model.make_future_dataframe(periods=steps, freq=freq)
        forecast = self.model.predict(future)
        
        # Format the output
        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(steps)
        result.rename(columns={'ds': 'Date', 'yhat': 'Forecast', 'yhat_lower': 'Pessimistic', 'yhat_upper': 'Optimistic'}, inplace=True)
        return result
