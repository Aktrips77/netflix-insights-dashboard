"""
charts.py
---------
All Plotly Express chart builders for the Netflix Insights Dashboard.
Every function returns a `plotly.graph_objects.Figure` styled to match
the dark, Netflix-inspired theme used across the dashboard.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.cleaning import explode_column

# --- Shared color palette -----------------------------------------------
NETFLIX_RED = "#E50914"
DARK_BG = "#141414"
CARD_BG = "#1F1F1F"
TEXT_COLOR = "#F5F5F1"
MUTED_TEXT = "#B3B3B3"
ACCENT_SCALE = ["#E50914", "#B00610", "#8C0A11", "#F5F5F1", "#564D4D"]


def _apply_dark_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply consistent dark styling to any Plotly figure."""
    fig.update_layout(
        title=title,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_COLOR, family="Helvetica, Arial, sans-serif"),
        title_font=dict(size=18, color=TEXT_COLOR),
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#000000", font_color=TEXT_COLOR),
    )
    fig.update_xaxes(gridcolor="#333333", zerolinecolor="#333333", color=MUTED_TEXT)
    fig.update_yaxes(gridcolor="#333333", zerolinecolor="#333333", color=MUTED_TEXT)
    return fig


def movies_vs_tv_pie(df: pd.DataFrame) -> go.Figure:
    """Interactive pie chart comparing Movie vs. TV Show counts."""
    counts = df["type"].value_counts().reset_index()
    counts.columns = ["type", "count"]

    fig = px.pie(
        counts,
        names="type",
        values="count",
        hole=0.55,
        color="type",
        color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#F5F5F1"},
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont_size=14,
        marker=dict(line=dict(color=DARK_BG, width=2)),
    )
    return _apply_dark_theme(fig, "Movies vs TV Shows")


def top_genres_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart of the top N genres by number of titles."""
    exploded = explode_column(df, "genre_list")
    genre_counts = (
        exploded["genre_list"]
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    genre_counts.columns = ["genre", "count"]
    genre_counts = genre_counts.sort_values("count")  # ascending for horizontal bars

    fig = px.bar(
        genre_counts,
        x="count",
        y="genre",
        orientation="h",
        color="count",
        color_continuous_scale=["#564D4D", NETFLIX_RED],
        text="count",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Titles")
    return _apply_dark_theme(fig, f"Top {top_n} Genres")


def top_countries_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart of the top N content-producing countries."""
    exploded = explode_column(df, "country_list")
    country_counts = (
        exploded["country_list"]
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    country_counts.columns = ["country", "count"]
    country_counts = country_counts.sort_values("count")

    fig = px.bar(
        country_counts,
        x="count",
        y="country",
        orientation="h",
        color="count",
        color_continuous_scale=["#564D4D", NETFLIX_RED],
        text="count",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Titles")
    return _apply_dark_theme(fig, f"Top {top_n} Countries")


def content_added_over_time(df: pd.DataFrame) -> go.Figure:
    """Line chart showing number of titles added to Netflix per year."""
    valid = df.dropna(subset=["year_added"])
    yearly = (
        valid.groupby(["year_added", "type"])
        .size()
        .reset_index(name="count")
        .sort_values("year_added")
    )
    yearly["year_added"] = yearly["year_added"].astype(int)

    fig = px.line(
        yearly,
        x="year_added",
        y="count",
        color="type",
        markers=True,
        color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#F5F5F1"},
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(xaxis_title="Year Added", yaxis_title="Titles Added")
    return _apply_dark_theme(fig, "Content Added Over Time")


def rating_distribution_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart showing the distribution of content ratings."""
    rating_counts = df["rating"].value_counts().reset_index()
    rating_counts.columns = ["rating", "count"]
    rating_counts = rating_counts.sort_values("count", ascending=False)

    fig = px.bar(
        rating_counts,
        x="rating",
        y="count",
        color="count",
        color_continuous_scale=["#564D4D", NETFLIX_RED],
        text="count",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Rating", yaxis_title="Titles")
    return _apply_dark_theme(fig, "Rating Distribution")


def movie_duration_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram of movie durations (in minutes)."""
    movies = df[(df["type"] == "Movie") & (df["duration_minutes"].notna())]

    fig = px.histogram(
        movies,
        x="duration_minutes",
        nbins=30,
        color_discrete_sequence=[NETFLIX_RED],
    )
    fig.update_traces(marker_line_color=DARK_BG, marker_line_width=1)
    fig.update_layout(
        xaxis_title="Duration (minutes)",
        yaxis_title="Number of Movies",
        bargap=0.05,
    )
    return _apply_dark_theme(fig, "Movie Duration Distribution")
