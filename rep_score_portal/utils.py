from typing import Optional

import streamlit as st


def reset_session_state_progress() -> None:
    """Reset the ``st.session_state.progress`` list."""
    st.session_state.progress = list()


def reset_session_state_asset_information(reload_page: bool = True) -> None:
    """
    Reset the ``st.session_state.asset_information`` dictionary.

    Parameters
    ----------
    reload_page: bool
        Use Javascript to reload the page after resetting the ``asset_information`` variable.

    """
    st.session_state.asset_information = dict()

    if reload_page:
        # also reload the page while we are at it
        reload_javascript = ("""
            <script>
            window.location.reload();
            </script>
        """)

        st.components.v1.html(reload_javascript)


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
