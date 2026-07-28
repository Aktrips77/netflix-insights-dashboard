"""
cleaning.py
-----------
All data-cleaning / preprocessing logic for the Netflix Insights Dashboard
lives in this module. Keeping it separate from loader.py and app.py makes
the transformation logic easy to test and reuse.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def clean_netflix_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and enrich the raw Netflix titles dataframe.

    Steps performed:
        1. Normalize column names.
        2. Handle missing values safely (no crashes on NaN).
        3. Parse `date_added` into a real datetime column.
        4. Extract `year_added` / `month_added` for time-series charts.
        5. Split multi-value columns (`country`, `listed_in`, `cast`)
           into clean lists for later explode operations.
        6. Extract a numeric `duration_minutes` for movies and
           `duration_seasons` for TV shows.

    Args:
        df: Raw dataframe loaded directly from netflix_titles.csv.

    Returns:
        A cleaned, enriched copy of the dataframe.
    """
    data = df.copy()

    # --- 1. Normalize column names (defensive, in case of stray spaces) ---
    data.columns = [c.strip().lower() for c in data.columns]

    # --- 2. Safe fill of missing values for categorical text columns ---
    text_cols = ["director", "cast", "country", "rating", "listed_in", "duration"]
    for col in text_cols:
        if col in data.columns:
            data[col] = data[col].fillna("Unknown").astype(str).str.strip()
            # Replace empty strings (after strip) with "Unknown" as well
            data[col] = data[col].replace("", "Unknown")

    if "type" in data.columns:
        data["type"] = data["type"].fillna("Unknown").astype(str).str.strip()

    if "title" in data.columns:
        data["title"] = data["title"].fillna("Untitled").astype(str).str.strip()

    if "description" in data.columns:
        data["description"] = data["description"].fillna("").astype(str)

    # --- 3. Parse date_added into a real datetime column ---
    if "date_added" in data.columns:
        data["date_added"] = pd.to_datetime(
            data["date_added"].astype(str).str.strip(), errors="coerce"
        )
    else:
        data["date_added"] = pd.NaT

    # --- 4. Derive year/month added for time-series analysis ---
    data["year_added"] = data["date_added"].dt.year
    data["month_added"] = data["date_added"].dt.month_name()

    # --- 5. Ensure release_year is numeric, drop impossible years ---
    if "release_year" in data.columns:
        data["release_year"] = pd.to_numeric(
            data["release_year"], errors="coerce"
        )
    else:
        data["release_year"] = np.nan

    # --- 6. Split multi-value columns into clean Python lists ---
    def _split_to_list(value: str) -> list[str]:
        if not isinstance(value, str) or value in ("Unknown", ""):
            return ["Unknown"]
        return [item.strip() for item in value.split(",") if item.strip()]

    data["country_list"] = data["country"].apply(_split_to_list)
    data["genre_list"] = data["listed_in"].apply(_split_to_list)

    # Primary (first-listed) country / genre, used for simple grouping
    data["primary_country"] = data["country_list"].apply(lambda lst: lst[0])
    data["primary_genre"] = data["genre_list"].apply(lambda lst: lst[0])

    # --- 7. Extract numeric duration for movies vs. TV shows ---
    def _extract_movie_minutes(row) -> float:
        if row["type"] == "Movie" and isinstance(row["duration"], str):
            digits = "".join(ch for ch in row["duration"] if ch.isdigit())
            return float(digits) if digits else np.nan
        return np.nan

    def _extract_tv_seasons(row) -> float:
        if row["type"] == "TV Show" and isinstance(row["duration"], str):
            digits = "".join(ch for ch in row["duration"] if ch.isdigit())
            return float(digits) if digits else np.nan
        return np.nan

    data["duration_minutes"] = data.apply(_extract_movie_minutes, axis=1)
    data["duration_seasons"] = data.apply(_extract_tv_seasons, axis=1)

    return data


def explode_column(df: pd.DataFrame, list_col: str) -> pd.DataFrame:
    """
    Explode a column containing lists (e.g. country_list, genre_list) into
    one row per list item. Useful for accurate "top N" aggregations when
    a title belongs to multiple countries/genres.

    Args:
        df: Cleaned dataframe.
        list_col: Name of the column containing list values.

    Returns:
        Exploded dataframe (one row per list element).
    """
    exploded = df.explode(list_col)
    exploded = exploded[exploded[list_col] != "Unknown"]
    return exploded


def apply_filters(
    df: pd.DataFrame,
    content_types: list[str] | None = None,
    countries: list[str] | None = None,
    year_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """
    Apply sidebar filter selections to the cleaned dataframe.

    Args:
        df: Cleaned dataframe.
        content_types: List of selected content types ("Movie", "TV Show").
        countries: List of selected countries (matches primary_country
            as well as any country in country_list).
        year_range: (min_year, max_year) inclusive range on release_year.

    Returns:
        Filtered dataframe.
    """
    filtered = df.copy()

    if content_types:
        filtered = filtered[filtered["type"].isin(content_types)]

    if countries:
        filtered = filtered[
            filtered["country_list"].apply(
                lambda lst: any(c in countries for c in lst)
            )
        ]

    if year_range:
        min_year, max_year = year_range
        filtered = filtered[
            (filtered["release_year"] >= min_year)
            & (filtered["release_year"] <= max_year)
        ]

    return filtered
