import pandas as pd
import streamlit as st

from _version import __version__
from utils import reset_session_state_asset_information, reset_session_state_progress


def construct_sidebar() -> None:
    """Construct the sidebar."""
    with st.sidebar:
        st.caption('')

        _, col_2, _ = st.columns([1, 27, 1])

        with col_2:
            if st.secrets['login_logos'].get(st.session_state['username']) == 'Mars Petcare':
                st.image('../images/Mars Petcare Logo Square.png', use_column_width=True)
            else:
                st.image('../images/Mars Chocolate Logo.png', use_column_width=True)

        st.markdown('<br><br>', unsafe_allow_html=True)

        start_the_process_col_1, start_the_process_col_2 = st.columns([0.1, 300])

        with start_the_process_col_2:
            start_the_process_button = st.button('Submit an Asset')

        if start_the_process_button:
            st.session_state.sidebar_radio = 'Submit an Asset'

        st.markdown('<br>', unsafe_allow_html=True)

        submit_an_asset_pages_navigation_container = st.container()

        st.markdown('<br>', unsafe_allow_html=True)

        asset_overview_col_1, asset_overview_col_2 = st.columns([0.1, 300])
        explore_your_data_col_1, explore_your_data_col_2 = st.columns([0.1, 300])

        with asset_overview_col_2:
            asset_overview_button = st.button('Asset Overview')
        with explore_your_data_col_2:
            explore_your_data_button = st.button('Explore Your Data')

        if explore_your_data_button:
            st.session_state.sidebar_radio = 'Explore Your Data'
        elif asset_overview_button:
            st.session_state.sidebar_radio = 'Asset Overview'

        if st.session_state.get('sidebar_radio') == 'Explore Your Data':
            with explore_your_data_col_1:
                st.markdown('*')
        elif st.session_state.get('sidebar_radio') == 'Submit an Asset':
            with start_the_process_col_1:
                st.markdown('*')
        else:
            with asset_overview_col_1:
                st.markdown('*')

        _display_submit_an_asset_page_progress(
            submit_an_asset_pages_navigation_container=submit_an_asset_pages_navigation_container,
        )

        st.markdown('<br>', unsafe_allow_html=True)

        email_subject = 'Trouble with the Rep Score Portal'
        email_body = "Hi Rebecca,%0D%0A%0D%0AI'm having some trouble with...%0D%0A%0D%0AThanks!"

        contact_html = (f"""
            <a style="color: #003749;"
            href="mailto:rebecca@therepproject.org?subject={email_subject}&body={email_body}">
            Having issues?</a>
        """)

        st.markdown(contact_html, unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)

        col_1, col_2 = st.columns(2)

        with col_1:
            if st.session_state.get('sidebar_radio') == 'Submit an Asset':
                if st.button('Start over'):
                    reset_session_state_progress()
                    reset_session_state_asset_information()

                    st.session_state.refresh_app = True

                    st.experimental_rerun()
            else:
                if st.button('Refresh'):
                    st.session_state.refresh_app = True

                    if isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
                        del st.session_state.asset_tracker_df
                    if isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame):
                        del st.session_state.data_explorer_df
                    if isinstance(st.session_state.get('assigned_user_assets'), list):
                        del st.session_state.assigned_user_assets

                    st.experimental_rerun()

        with col_2:
            st.session_state.authenticator.logout('Logout', 'main')

        st.markdown('<br>', unsafe_allow_html=True)

        st.caption(f'<p style="color: black;">v{__version__}</p>', unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)


def _display_submit_an_asset_page_progress(
    submit_an_asset_pages_navigation_container: st.container,
) -> None:
    """
    Display the progress of the "Submit an Asset" pages in the sidebar.

    Parameters
    ----------
    submit_an_asset_pages_navigation_container: st.container
        Container in which to place the progress text

    """
    highlight_one = False
    highlight_two = False
    highlight_three = False
    highlight_four = False
    highlight_five = False
    highlight_six = False

    if st.session_state.get('sidebar_radio') == 'Submit an Asset':
        if 'page_one_complete' not in st.session_state.progress:
            highlight_one = True
        elif (
            'page_one_complete' in st.session_state.progress
            and 'page_two_complete' not in st.session_state.progress
        ):
            highlight_two = True
        elif (
            'page_two_complete' in st.session_state.progress
            and 'page_three_complete' not in st.session_state.progress
        ):
            highlight_three = True
        elif (
            'page_three_complete' in st.session_state.progress
            and 'page_four_complete' not in st.session_state.progress
        ):
            highlight_four = True
        elif (
            'page_four_complete' in st.session_state.progress
            and 'page_five_complete' not in st.session_state.progress
        ):
            highlight_five = True
        else:
            highlight_six = True

    navigation_string = (f"""
        <p{' style="color:#fff;"><strong' if highlight_one else ''}>1. Start the Process{'</strong>' if highlight_one else ''}</p>
        <p{' style="color:#fff;"><strong' if highlight_two else ''}>2. DEI Checklist: Marketing Brief{'</strong>' if highlight_two else ''}</p>
        <p{' style="color:#fff;"><strong' if highlight_three else ''}>3. DEI Checklist: Agency Creative Brief{'</strong>' if highlight_three else ''}</p>
        <p{' style="color:#fff;"><strong' if highlight_four else ''}>4. DEI Checklist: Creative Reviews{'</strong>' if highlight_four else ''}</p>
        <p{' style="color:#fff;"><strong' if highlight_five else ''}>5. Upload Asset{'</strong>' if highlight_five else ''}</p>
        <p{' style="color:#fff;"><strong' if highlight_six else ''}>6. Summary{'</strong>' if highlight_six else ''}</p>
    """)  # noqa: E501

    with submit_an_asset_pages_navigation_container:
        st.markdown(navigation_string, unsafe_allow_html=True)
