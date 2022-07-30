from typing import List, Optional

import streamlit as st

from input_output import get_assigned_user_assets


def reset_session_state_progress() -> None:
    """Reset the ``st.session_state.progress`` list."""
    st.session_state.progress = list()


def reset_session_state_asset_information() -> None:
    """Reset the ``st.session_state.asset_information`` dictionary."""
    st.session_state.asset_information = dict()


def edit_colors_of_selectbox() -> None:
    """Color ``.stSelectbox`` CSS classes with a white fill and a black border."""
    text_area_color_css = ("""
        <style>
        .stSelectbox > div > div {
            background-color: #FFFFFF;
            border-bottom-color: #000000;
            border-top-color: #000000;
            border-right-color: #000000;
            border-left-color: #000000;
        }
        </style>
    """)

    st.markdown(text_area_color_css, unsafe_allow_html=True)


def display_progress_bar_asset_tracker(
    asset_name: str,
    brand: Optional[str],
    product: Optional[str],
    content_type: Optional[str],
    version: Optional[str],
    status: str,
    progress_value: float,
) -> None:
    """
    Display the asset tracker expander with a progress bar visualization.

    Parameters
    ----------
    asset_name: str
    brand: str
    product: str
    content_type: str
    version: str
    status: str
    progress_value: float
        Float value between 0 and 1 to pass to ``st.progress``

    """
    with st.expander(label=asset_name, expanded=True):
        st.write(f"**Brand**: {brand if brand else 'N/A'}")
        st.write(f"**Product**: {product if product else 'N/A'}")
        st.write(f"**Content Type**: {content_type if content_type else 'N/A'}")
        st.write(f"**Version**: {version if version else 'N/A'}")

        st.caption(f'<p style="text-align:right;">{status}</p>', unsafe_allow_html=True)

        st.progress(progress_value)


def check_for_assigned_assets() -> None:
    """Check for this user's assigned assets while displaying a ``st.spinner``."""
    with st.spinner(text='Checking for assigned assets...'):
        if not isinstance(st.session_state.get('assigned_user_assets'), list):
            st.session_state.assigned_user_assets = get_assigned_user_assets(
                username=st.session_state['username'],
            )


def insert_line_break() -> None:
    """Insert line break in Streamlit app."""
    st.markdown('<br>', unsafe_allow_html=True)


def get_content_types() -> List[str]:
    """Get an ordered list of valid content types."""
    return [
        'Storyboard',
        'Working Cut',
        'Rough Cut',
        'Final Cut',
    ]
