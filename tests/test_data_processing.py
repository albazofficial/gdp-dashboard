import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

# Guarantee root resolution in test runner
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.metrics import calculate_cagr, calculate_yoy_growth, calculate_volatility
from src.pipeline.loader import load_and_transform_gdp_data


def test_calculate_cagr_standard():
    start_val = 100.0
    end_val = 200.0
    years = 10
    cagr = calculate_cagr(start_val, end_val, years)
    assert pytest.approx(cagr, 0.001) == 0.07177


@pytest.mark.parametrize("start,end,years", [
    (0.0, 100.0, 5),      # Zero base guard
    (-50.0, 100.0, 5),    # Negative base guard
    (100.0, 200.0, 0),    # Zero timeline guard
    (100.0, 200.0, -3),   # Negative timeline guard
    (np.nan, 200.0, 5),   # NaN guard
])
def test_calculate_cagr_invalid_boundaries(start, end, years):
    assert np.isnan(calculate_cagr(start, end, years))


def test_calculate_yoy_growth():
    series = pd.Series([100.0, 110.0, 132.0])
    growth = calculate_yoy_growth(series)
    assert pytest.approx(growth.iloc[1], 0.01) == 10.0
    assert pytest.approx(growth.iloc[2], 0.01) == 20.0


def test_calculate_volatility_rolling():
    growth = pd.Series([2.0, 4.0, 2.0, 5.0, 1.0])
    vol = calculate_volatility(growth, window=3)
    assert len(vol) == len(growth)
    assert not np.isnan(vol.iloc[-1])


def test_load_and_transform_gdp_data():
    sample_file = ROOT_DIR / 'data/gdp_data.csv'
    if sample_file.exists():
        df = load_and_transform_gdp_data(sample_file)
        assert 'Country Name' in df.columns
        assert 'Year' in df.columns
        assert 'GDP' in df.columns
        assert len(df) > 0
