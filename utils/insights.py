"""Rule-based insight generation for the Netflix dashboard."""

from __future__ import annotations

import pandas as pd

from utils.cleaning import explode_column


def build_key_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    """Return concise, data-backed observations for the filtered catalog.

    The function intentionally uses deterministic rules rather than an LLM so
    every statement can be reproduced from the displayed data.
    """
    if df.empty:
        return []

    total_titles = len(df)
    movie_share = (df["type"].eq("Movie").sum() / total_titles) * 100

    insights = [
        {
            "title": "Content mix",
            "text": f"Movies make up {movie_share:.0f}% of the selected catalog.",
        }
    ]

    countries = explode_column(df, "country_list")["country_list"].value_counts()
    if not countries.empty:
        insights.append(
            {
                "title": "Leading country",
                "text": (
                    f"{countries.index[0]} appears on {countries.iloc[0]:,} "
                    "title(s), the highest country contribution."
                ),
            }
        )

    genres = explode_column(df, "genre_list")["genre_list"].value_counts()
    if not genres.empty:
        insights.append(
            {
                "title": "Most common genre",
                "text": (
                    f"The most common genre is {genres.index[0]}, appearing on "
                    f"{genres.iloc[0]:,} title(s)."
                ),
            }
        )

    added_by_year = df.dropna(subset=["year_added"]).groupby("year_added").size()
    if not added_by_year.empty:
        peak_year = int(added_by_year.idxmax())
        insights.append(
            {
                "title": "Catalog growth peak",
                "text": (
                    f"Netflix added the most selected titles in {peak_year} "
                    f"({added_by_year.max():,} title(s))."
                ),
            }
        )

    valid_release_years = df["release_year"].dropna()
    if not valid_release_years.empty:
        oldest_year = int(valid_release_years.min())
        newest_year = int(valid_release_years.max())
        oldest_title = df.loc[df["release_year"].eq(oldest_year), "title"].iloc[0]
        newest_title = df.loc[df["release_year"].eq(newest_year), "title"].iloc[0]
        insights.extend(
            [
                {
                    "title": "Oldest title",
                    "text": f"{oldest_title} is the earliest release in this view ({oldest_year}).",
                },
                {
                    "title": "Newest title",
                    "text": f"{newest_title} is the latest release in this view ({newest_year}).",
                },
            ]
        )

    return insights
