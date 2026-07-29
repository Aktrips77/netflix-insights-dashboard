"""Netflix Insights Dashboard Streamlit entry point."""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd
import streamlit as st

from components.footer import render_footer
from components.metric_cards import render_kpis
from components.sidebar import render_sidebar
from utils.charts import (
    content_added_over_time,
    movie_duration_histogram,
    movies_vs_tv_pie,
    rating_distribution_bar,
    top_countries_bar,
    top_genres_bar,
)
from utils.cleaning import apply_filters
from utils.insights import build_key_insights
from utils.loader import load_data


st.set_page_config(
    page_title="Netflix Insights Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    """Load the reusable dashboard stylesheet."""
    stylesheet = Path(__file__).parent / "assets" / "styles.css"
    st.markdown(f"<style>{stylesheet.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header(total_titles: int) -> None:
    """Render the page title and active-catalog summary."""
    st.markdown('<p class="hero-eyebrow">DATA EXPLORATION</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Netflix Insights Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="hero-copy">Explore <strong>{total_titles:,}</strong> title(s) in the active catalog view.</p>',
        unsafe_allow_html=True,
    )


def render_key_insights(df: pd.DataFrame) -> None:
    """Display rule-based observations in responsive groups of three."""
    insights = build_key_insights(df)
    if not insights:
        return

    st.markdown('<p class="section-label">Key insights</p>', unsafe_allow_html=True)
    for start in range(0, len(insights), 3):
        columns = st.columns(3)
        for column, insight in zip(columns, insights[start : start + 3]):
            with column:
                st.markdown(
                    f'''<div class="insight-card">
                        <p class="insight-title">{html.escape(insight['title'])}</p>
                        <p class="insight-text">{html.escape(insight['text'])}</p>
                    </div>''',
                    unsafe_allow_html=True,
                )


def render_chart(chart_function, df: pd.DataFrame) -> None:
    """Render a chart in a consistent bordered dashboard container."""
    with st.container(border=True):
        st.plotly_chart(chart_function(df), use_container_width=True, config={"displaylogo": False})


def render_catalog_table(df: pd.DataFrame) -> None:
    """Render sortable filtered data and a CSV download control."""
    st.markdown('<p class="section-label">Catalog explorer</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.caption("Sidebar filters and title search apply to this sortable table and download.")
        display_columns = [
            "title", "type", "director", "country", "release_year", "rating",
            "duration", "listed_in", "date_added",
        ]
        export_df = df[[column for column in display_columns if column in df.columns]].copy()
        st.download_button(
            "Download filtered catalog (CSV)",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="netflix_filtered_catalog.csv",
            mime="text/csv",
        )
        st.dataframe(export_df.reset_index(drop=True), use_container_width=True, height=430)


def main() -> None:
    """Load data, apply filters, and compose the dashboard."""
    inject_styles()
    try:
        with st.spinner("Loading Netflix catalog..."):
            df = load_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.info("Add `netflix_titles.csv` to the `data/` folder and reload the page.")
        st.stop()
    except Exception as error:  # pragma: no cover - defensive UI boundary
        st.error("The dataset could not be processed. Please verify its CSV format.")
        st.exception(error)
        st.stop()

    if df.empty:
        st.warning("The dataset is empty. Add records to the CSV and reload the dashboard.")
        st.stop()

    filters = render_sidebar(df)
    filtered_df = apply_filters(df, **filters)
    if filtered_df.empty:
        st.warning("No titles match these filters. Try clearing a filter or widening the release-year range.")
        st.stop()

    render_header(len(filtered_df))
    render_kpis(filtered_df)
    render_key_insights(filtered_df)

    st.markdown('<p class="section-label">Catalog composition</p>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        render_chart(movies_vs_tv_pie, filtered_df)
    with right:
        render_chart(top_genres_bar, filtered_df)

    st.markdown('<p class="section-label">Global catalog trends</p>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        render_chart(top_countries_bar, filtered_df)
    with right:
        render_chart(content_added_over_time, filtered_df)

    st.markdown('<p class="section-label">Audience and duration</p>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        render_chart(rating_distribution_bar, filtered_df)
    with right:
        render_chart(movie_duration_histogram, filtered_df)

    render_catalog_table(filtered_df)
    render_footer()


if __name__ == "__main__":
    main()
