"""
Core Econometric & Mathematical Engine.
Pure functions for growth calculations, volatility, and boundaries.
"""

from typing import Union
import numpy as np
import pandas as pd


def calculate_cagr(start_val: float, end_val: float, num_years: int) -> float:
    """
    Computes Compound Annual Growth Rate (CAGR) with boundary guards.
    Formula: (End / Start) ** (1 / n) - 1
    """
    if (
        num_years <= 0 
        or pd.isna(start_val) 
        or pd.isna(end_val) 
        or start_val <= 0 
        or end_val < 0
    ):
        return np.nan
        
    return float(((end_val / start_val) ** (1 / num_years)) - 1)


def calculate_yoy_growth(series: pd.Series) -> pd.Series:
    """
    Computes Year-over-Year (YoY) percentage delta.
    """
    if series.empty:
        return series
    return series.pct_change() * 100.0


def calculate_volatility(growth_series: pd.Series, window: int = 5) -> pd.Series:
    """
    Calculates rolling standard deviation of YoY growth as economic volatility proxy.
    """
    if growth_series.empty or window <= 1:
        return pd.Series(dtype=float)
    return growth_series.rolling(window=window, min_periods=1).std()
