"""Sidebar controls for the Netflix Insights Dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.cleaning import explode_column


def render_sidebar(df: pd.DataFrame) -> dict:
    """Render global dashboard filters and return their selected values."""
    with st.sidebar:
        st.markdown('<p class="brand">NETFLIX</p>', unsafe_allow_html=True)
        st.markdown('<p class="brand-subtitle">INSIGHTS DASHBOARD</p>', unsafe_allow_html=True)
        st.caption("Explore the catalog with live, global filters.")
        st.divider()

        st.subheader("Filter catalog")
        title_query = st.text_input(
            "Search title",
            placeholder="e.g. Dark, Roma, Stranger...",
            help="Search applies to every KPI, insight, chart, and table.",
        )
        content_types = st.multiselect(
            "Content type", sorted(df["type"].dropna().unique().tolist())
        )
        countries = st.multiselect(
            "Country",
            sorted(explode_column(df, "country_list")["country_list"].unique().tolist()),
        )
        genres = st.multiselect(
            "Genre",
            sorted(explode_column(df, "genre_list")["genre_list"].unique().tolist()),
        )
        ratings = st.multiselect(
            "Rating", sorted(df["rating"].dropna().unique().tolist())
        )

        valid_years = df["release_year"].dropna()
        min_year = int(valid_years.min())
        max_year = int(valid_years.max())
        year_range = st.slider(
            "Release year", min_value=min_year, max_value=max_year, value=(min_year, max_year)
        )

        st.divider()
        st.caption("Built with Streamlit, Pandas, and Plotly")

    return {
        "content_types": content_types,
        "countries": countries,
        "genres": genres,
        "ratings": ratings,
        "year_range": year_range,
        "title_query": title_query,
    }
