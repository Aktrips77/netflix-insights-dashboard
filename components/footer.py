"""Footer component for the Netflix Insights Dashboard."""

from __future__ import annotations

import streamlit as st


def render_footer() -> None:
    """Render a small attribution footer without imitating Netflix branding."""
    st.markdown(
        '''<footer class="dashboard-footer">
            Netflix Insights Dashboard · Built for data exploration with Streamlit and Plotly
        </footer>''',
        unsafe_allow_html=True,
    )
