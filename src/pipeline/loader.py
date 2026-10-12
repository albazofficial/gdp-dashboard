"""
Data Normalization & Ingestion Pipeline.
Transforms matrix World Bank datasets into typed columnar time-series records.
"""

from pathlib import Path
import pandas as pd


def load_and_transform_gdp_data(filepath: Path) -> pd.DataFrame:
    """
    Loads raw matrix GDP dataset, validates schema, and melts annual attributes
    into standardized columnar records.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Source file missing at: {filepath}")

    raw_df = pd.read_csv(filepath)
    
    required_identifiers = ['Country Name', 'Country Code']
    for col in required_identifiers:
        if col not in raw_df.columns:
            raise ValueError(f"Schema violation: missing identifier '{col}'")

    year_columns = [col for col in raw_df.columns if col.isdigit()]
    if not year_columns:
        raise ValueError("Schema violation: no annual time-series columns detected.")

    melted_df = raw_df.melt(
        id_vars=required_identifiers,
        value_vars=year_columns,
        var_name='Year',
        value_name='GDP'
    )

    melted_df['Year'] = pd.to_numeric(melted_df['Year'], errors='coerce')
    melted_df['GDP'] = pd.to_numeric(melted_df['GDP'], errors='coerce')

    return melted_df.dropna(subset=['Year'])
