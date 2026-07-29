"""KPI card rendering for the dashboard."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from utils.cleaning import explode_column


def _metric_card(column, icon: str, label: str, value: int) -> None:
    """Render one accessible, consistently styled KPI card."""
    with column:
        st.markdown(
            f'''<div class="metric-card">
                <span class="metric-icon" aria-hidden="true">{icon}</span>
                <p class="metric-value">{value:,}</p>
                <p class="metric-label">{html.escape(label)}</p>
            </div>''',
            unsafe_allow_html=True,
        )


def render_kpis(df: pd.DataFrame) -> None:
    """Calculate and display the five headline catalog metrics."""
    countries = explode_column(df, "country_list")["country_list"].nunique()
    genres = explode_column(df, "genre_list")["genre_list"].nunique()
    metrics = [
        ("◉", "Total titles", len(df)),
        ("▶", "Movies", int(df["type"].eq("Movie").sum())),
        ("▣", "TV shows", int(df["type"].eq("TV Show").sum())),
        ("◎", "Countries", countries),
        ("◇", "Genres", genres),
    ]
    columns = st.columns(len(metrics))
    for column, (icon, label, value) in zip(columns, metrics):
        _metric_card(column, icon, label, value)
