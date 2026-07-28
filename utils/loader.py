"""
loader.py
---------
Handles reading the Netflix titles CSV from disk and caching the result
so the app stays fast on every rerun (Streamlit reruns the whole script
on each interaction).
"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from utils.cleaning import clean_netflix_data

DEFAULT_DATA_PATH = os.path.join("data", "netflix_titles.csv")


@st.cache_data(show_spinner="Loading Netflix data...")
def load_data(path: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the raw Netflix titles CSV and return a cleaned dataframe.

    Cached with st.cache_data so the (potentially expensive) read +
    clean pipeline only runs once per unique `path` argument, not on
    every widget interaction.

    Args:
        path: Path to the netflix_titles.csv file.

    Returns:
        Cleaned dataframe ready for filtering / visualization.

    Raises:
        FileNotFoundError: If the CSV cannot be found at `path`.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find dataset at '{path}'. "
            "Please place netflix_titles.csv inside the data/ folder."
        )

    raw_df = pd.read_csv(path)
    cleaned_df = clean_netflix_data(raw_df)
    return cleaned_df
