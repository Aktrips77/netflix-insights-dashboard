"""
app.py
------
Netflix Insights Dashboard - main Streamlit entry point.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.charts import (
    content_added_over_time,
    movie_duration_histogram,
    movies_vs_tv_pie,
    rating_distribution_bar,
    top_countries_bar,
    top_genres_bar,
)
from utils.cleaning import apply_filters, explode_column
from utils.insights import build_key_insights
from utils.loader import load_data

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Netflix Insights Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CUSTOM CSS — Premium dark theme with Netflix red accents
# =============================================================================
def inject_custom_css() -> None:
    """Inject the dashboard's custom dark / Netflix-red styling."""
    st.markdown(
        """
        <style>
            /* --- Global background & text ------------------------------ */
            .stApp {
                background-color: #0E0E0E;
                color: #F5F5F1;
            }

            /* --- Sidebar ------------------------------------------------ */
            section[data-testid="stSidebar"] {
                background-color: #141414;
                border-right: 1px solid #2A2A2A;
            }

            /* --- Headings ------------------------------------------------ */
            h1, h2, h3, h4 {
                color: #F5F5F1 !important;
                font-weight: 700 !important;
            }

            /* --- KPI Cards ------------------------------------------------ */
            .kpi-card {
                background: linear-gradient(145deg, #1F1F1F, #161616);
                border: 1px solid #2A2A2A;
                border-radius: 16px;
                padding: 20px 18px;
                text-align: center;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
                transition: transform 0.15s ease-in-out;
            }
            .kpi-card:hover {
                transform: translateY(-3px);
                border-color: #E50914;
            }
            .kpi-value {
                font-size: 32px;
                font-weight: 800;
                color: #E50914;
                margin: 0;
            }
            .kpi-label {
                font-size: 13px;
                color: #B3B3B3;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 6px;
            }

            /* --- Section containers --------------------------------------- */
            .section-card {
                background-color: #1A1A1A;
                border: 1px solid #262626;
                border-radius: 18px;
                padding: 22px 24px;
                margin-bottom: 22px;
            }

            /* --- Key insights -------------------------------------------- */
            .insight-card {
                background: linear-gradient(145deg, #241416, #1A1A1A);
                border-left: 3px solid #E50914;
                border-radius: 12px;
                min-height: 112px;
                padding: 16px;
            }
            .insight-title {
                color: #F5F5F1;
                font-size: 14px;
                font-weight: 700;
                margin: 0 0 7px;
            }
            .insight-text {
                color: #C7C7C7;
                font-size: 13px;
                line-height: 1.45;
                margin: 0;
            }

            /* --- Netflix logo/title block ---------------------------------- */
            .netflix-logo {
                font-size: 30px;
                font-weight: 900;
                color: #E50914;
                letter-spacing: 1px;
                margin-bottom: 0px;
            }
            .netflix-subtitle {
                font-size: 13px;
                color: #B3B3B3;
                margin-top: -6px;
                margin-bottom: 18px;
            }

            /* --- DataFrame / table tweaks ------------------------------------ */
            .stDataFrame {
                border-radius: 12px;
                overflow: hidden;
            }

            /* --- Buttons / inputs -------------------------------------------- */
            .stTextInput > div > div > input {
                background-color: #1F1F1F;
                color: #F5F5F1;
                border-radius: 10px;
            }
            div[data-baseweb="select"] > div {
                background-color: #1F1F1F;
                border-radius: 10px;
            }

            /* --- Hide default Streamlit chrome we don't want --------------- */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# KPI CARD RENDERER
# =============================================================================
def render_kpi_card(column, label: str, value: str) -> None:
    """Render a single KPI card inside the given Streamlit column."""
    with column:
        st.markdown(
            f"""
            <div class="kpi-card">
                <p class="kpi-value">{value}</p>
                <p class="kpi-label">{label}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_kpis(df: pd.DataFrame) -> None:
    """Compute and display the top-row KPI cards."""
    total_titles = len(df)
    total_movies = int((df["type"] == "Movie").sum())
    total_tv_shows = int((df["type"] == "TV Show").sum())

    countries_exploded = explode_column(df, "country_list")
    total_countries = countries_exploded["country_list"].nunique()

    genres_exploded = explode_column(df, "genre_list")
    total_genres = genres_exploded["genre_list"].nunique()

    cols = st.columns(5)
    render_kpi_card(cols[0], "Total Titles", f"{total_titles:,}")
    render_kpi_card(cols[1], "Movies", f"{total_movies:,}")
    render_kpi_card(cols[2], "TV Shows", f"{total_tv_shows:,}")
    render_kpi_card(cols[3], "Countries", f"{total_countries:,}")
    render_kpi_card(cols[4], "Genres", f"{total_genres:,}")


def render_key_insights(df: pd.DataFrame) -> None:
    """Display reproducible observations calculated from the active filters."""
    insights = build_key_insights(df)
    if not insights:
        return

    st.markdown("### 📈 Key Insights")
    columns = st.columns(len(insights))
    for column, insight in zip(columns, insights):
        with column:
            st.markdown(
                f"""
                <div class="insight-card">
                    <p class="insight-title">{insight['title']}</p>
                    <p class="insight-text">{insight['text']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# SIDEBAR — logo, title & filters
# =============================================================================
def render_sidebar(df: pd.DataFrame) -> dict:
    """
    Render the sidebar (logo + filters) and return the selected filter
    values as a dictionary.
    """
    with st.sidebar:
        st.markdown('<p class="netflix-logo">🎬 NETFLIX</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="netflix-subtitle">Insights Dashboard</p>',
            unsafe_allow_html=True,
        )
        st.divider()

        st.subheader("Filters")

        # --- Content Type filter ------------------------------------------
        content_types = st.multiselect(
            "Content Type",
            options=sorted(df["type"].dropna().unique().tolist()),
            default=[],
            help="Leave empty to include all content types.",
        )

        # --- Country filter -------------------------------------------------
        exploded_countries = explode_column(df, "country_list")
        country_options = sorted(exploded_countries["country_list"].unique().tolist())
        countries = st.multiselect(
            "Country",
            options=country_options,
            default=[],
            help="Leave empty to include all countries.",
        )

        # --- Release Year filter ---------------------------------------------
        valid_years = df["release_year"].dropna()
        min_year = int(valid_years.min()) if not valid_years.empty else 2000
        max_year = int(valid_years.max()) if not valid_years.empty else 2021

        year_range = st.slider(
            "Release Year",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
        )

        st.divider()
        st.caption("Built with Streamlit + Plotly Express")

    return {
        "content_types": content_types,
        "countries": countries,
        "year_range": year_range,
    }


# =============================================================================
# SEARCH SECTION
# =============================================================================
def render_search_section(df: pd.DataFrame) -> None:
    """Render a search-by-title box and matching results."""
    st.markdown("### 🔍 Search Titles")
    query = st.text_input(
        "Search by title",
        placeholder="e.g. Stranger, Roma, Dark...",
        label_visibility="collapsed",
    )

    if query:
        results = df[df["title"].str.contains(query, case=False, na=False)]
        st.caption(f"Found {len(results)} matching title(s)")
        if not results.empty:
            st.dataframe(
                results[
                    ["title", "type", "release_year", "rating", "duration", "listed_in"]
                ].reset_index(drop=True),
                use_container_width=True,
                height=250,
            )
    else:
        st.caption("Type a title above to search the filtered catalog.")


# =============================================================================
# DATA TABLE SECTION
# =============================================================================
def render_data_table(df: pd.DataFrame) -> None:
    """Render the full interactive data table for the filtered dataset."""
    st.markdown("### 📋 Browse Full Dataset")
    display_cols = [
        "title",
        "type",
        "director",
        "country",
        "release_year",
        "rating",
        "duration",
        "listed_in",
        "date_added",
    ]
    display_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(
        df[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=420,
    )


# =============================================================================
# MAIN APP
# =============================================================================
def main() -> None:
    inject_custom_css()

    st.title("🎬 Netflix Insights Dashboard")
    st.caption(
        "An interactive, production-quality exploration of the Netflix titles "
        "catalog — content mix, genres, countries, ratings and trends."
    )

    # --- Load data (cached) --------------------------------------------------
    try:
        df = load_data()
    except FileNotFoundError as err:
        st.error(str(err))
        st.stop()

    if df.empty:
        st.warning("The loaded dataset is empty. Please check your CSV file.")
        st.stop()

    # --- Sidebar filters -------------------------------------------------------
    filters = render_sidebar(df)
    filtered_df = apply_filters(
        df,
        content_types=filters["content_types"] or None,
        countries=filters["countries"] or None,
        year_range=filters["year_range"],
    )

    if filtered_df.empty:
        st.warning("No titles match the selected filters. Try widening your selection.")
        st.stop()

    # --- KPI Cards ------------------------------------------------------------
    render_kpis(filtered_df)
    st.write("")
    render_key_insights(filtered_df)
    st.write("")

    # --- Row 1: Movies vs TV | Top Genres -------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(movies_vs_tv_pie(filtered_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(top_genres_bar(filtered_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Row 2: Top Countries | Content Added Over Time -----------------------
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(top_countries_bar(filtered_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(content_added_over_time(filtered_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Row 3: Rating Distribution | Movie Duration Histogram -----------------
    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(rating_distribution_bar(filtered_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col6:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.plotly_chart(movie_duration_histogram(filtered_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Search section ----------------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    render_search_section(filtered_df)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Full data table -----------------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    render_data_table(filtered_df)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
