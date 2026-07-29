# 🎬 Netflix Insights Dashboard

A production-quality, interactive **Streamlit** dashboard for exploring the
Netflix titles catalog — content mix, genres, countries, ratings, and
growth over time. Built with a premium dark theme and Netflix-red accents.

---

## ✨ Features

- **Sidebar filters** — Content Type, Country, Release Year (range slider)
- **KPI cards** — Total Titles, Movies, TV Shows, Countries, Genres
- **Movies vs TV Shows** — interactive donut/pie chart
- **Top 10 Genres** — horizontal bar chart
- **Top 10 Countries** — horizontal bar chart
- **Content Added Over Time** — line chart by year, split by content type
- **Rating Distribution** — bar chart across all content ratings
- **Movie Duration Distribution** — histogram of runtime in minutes
- **Search by Title** — instant, case-insensitive title search
- **Interactive data table** — sortable/filterable full dataset browser

All charts are built with **Plotly Express** and are fully interactive
(hover tooltips, zoom, legend toggling).

---

## 🗂️ Project Structure

```
netflix-insights-dashboard/
│
├── app.py                  # Main Streamlit application (entry point)
├── requirements.txt        # Python dependencies
├── README.md                # This file
├── data/
│   └── netflix_titles.csv   # Dataset (Movie/TV Show catalog)
├── utils/
│   ├── loader.py             # Cached CSV loading
│   ├── cleaning.py           # Missing-value handling, parsing, filters
│   └── charts.py             # Plotly Express chart builders
└── assets/                   # Static assets (logos, images, etc.)
```

---

## 🚀 Getting Started

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the dataset

Place your `netflix_titles.csv` file inside the `data/` folder. The
expected columns (standard Kaggle "Netflix Movies and TV Shows" schema)
are:

```
show_id, type, title, director, cast, country, date_added,
release_year, rating, duration, listed_in, description
```

> A small sample dataset with the same schema is already included in
> `data/netflix_titles.csv` so the app runs out of the box. Replace it
> with the full dataset for the complete experience.

### 4. Run the app

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser (usually at
`http://localhost:8501`).

---

## 🧱 Architecture Notes

- **`utils/loader.py`** — Reads the CSV and applies cleaning via
  `st.cache_data`, so the (potentially expensive) load + clean pipeline
  only runs once per session, not on every widget interaction.
- **`utils/cleaning.py`** — Centralizes all data-hygiene logic: safe
  handling of missing values, datetime parsing, splitting multi-value
  fields (`country`, `listed_in`) into lists, extracting numeric movie
  durations / TV show season counts, and sidebar filter application.
- **`utils/charts.py`** — One function per chart, each returning a
  themed `plotly.graph_objects.Figure`. Keeping chart logic here keeps
  `app.py` focused purely on layout and orchestration.
- **`app.py`** — Composes the sidebar, KPI cards, chart grid, search
  box, and data table using Streamlit's column-based responsive layout.

---

## 🎨 Design

- Dark background (`#0E0E0E`) with elevated card surfaces (`#1A1A1A` /
  `#1F1F1F`) and Netflix red (`#E50914`) accents.
- Rounded, shadowed KPI and section cards with subtle hover states.
- Wide layout (`st.set_page_config(layout="wide")`) for a true dashboard
  feel on desktop, while Streamlit's column system reflows on smaller
  screens.

---

## 🛠️ Tech Stack

| Tool             | Purpose                          |
|------------------|-----------------------------------|
| Streamlit        | App framework / UI                |
| Pandas           | Data loading & transformation      |
| NumPy            | Numeric helpers                    |
| Plotly Express   | Interactive charting               |

---

## 📌 Notes

- All missing/NaN values are handled defensively — the app will not
  crash on incomplete rows; they're normalized to `"Unknown"` or
  excluded from relevant aggregations.
- Multi-value fields (e.g. a title listed under several countries or
  genres) are exploded so "Top 10" charts count each occurrence
  correctly rather than only the first value.

---

## Portfolio Highlights

- Global filters for content type, country, genre, rating, release year, and title search.
- Filter-aware KPI cards and rule-based insights, including content mix, catalog leaders, and oldest/newest releases.
- Interactive, responsive Plotly charts with unified Netflix-inspired styling.
- A sortable catalog explorer with a download of the current filtered result set.

## Screenshots

Add screenshots of the deployed dashboard here after deployment. Recommended views:

1. Full dashboard overview with the default catalog.
2. A filtered genre or country analysis.
3. Catalog explorer and CSV download action.

## Deploy to Streamlit Community Cloud

1. Fork or push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app from the repository.
3. Select the `main` branch and set `app.py` as the entry point.
4. Deploy. Streamlit installs dependencies from `requirements.txt` automatically.

## Future Improvements

- Add automated unit tests for cleaning and filtering logic.
- Add drill-down detail views for countries and genres.
- Add a dataset refresh date and data-source attribution in the interface.
