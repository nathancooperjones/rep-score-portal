import pandas as pd
import streamlit as st

from _version import __version__
from utils import (
    insert_line_break,
    reset_session_state_asset_information,
    reset_session_state_progress,
)


def construct_sidebar() -> None:
    """Construct the sidebar."""
    with st.sidebar:
        st.caption('')

        _, col_2, _ = st.columns([1, 27, 1])

        with col_2:
            user_login_logo = st.secrets['login_logos'].get(st.session_state['username'])

            if user_login_logo == 'Mars Petcare':
                st.image('./static/Mars Petcare Logo Square.png', use_column_width=True)
            elif user_login_logo == 'ExxonMobil':
                st.image('./static/ExxonMobil Logo.png', use_column_width=True)
            elif user_login_logo == 'BBDO Creative Compass':
                st.image('./static/BBDO Creative Compass Logo.png', use_column_width=True)
            else:
                st.image('./static/Mars Logo.png', use_column_width=True)

        _, name_display_col_2 = st.columns([0.1, 300])

        with name_display_col_2:
            st.markdown(f'Welcome back, **{st.session_state["name"]}**!')

        insert_line_break()

        start_the_process_col_1, start_the_process_col_2 = st.columns([0.1, 300])

        with start_the_process_col_2:
            start_the_process_button = st.button('Submit an Asset')

        if start_the_process_button:
            st.session_state.sidebar_radio = 'Submit an Asset'

        insert_line_break()

        submit_an_asset_pages_navigation_container = st.container()

        insert_line_break()

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

        insert_line_break()

        email_subject = 'Trouble with the Rep Score Portal'
        email_body = "Hi Rebecca,%0D%0A%0D%0AI'm having some trouble with...%0D%0A%0D%0AThanks!"

        contact_html = (f"""
            <a style="color: #003749;"
            href="mailto:{st.secrets['authenticator']['contact_email_address']}?
            subject={email_subject}&body={email_body}">
            Having issues?</a>
        """)

        st.markdown(contact_html, unsafe_allow_html=True)

        insert_line_break()

        sidebar_col_1, sidebar_col_2 = st.columns(2)

        with sidebar_col_1:
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

        with sidebar_col_2:
            # HARD-CODED ``streamlit_authenticator.Authenticate.logout`` method to add injected
            # logic into the button action:
            # https://github.com/mkhorasani/Streamlit-Authenticator/blob/v0.2.2/streamlit_authenticator/authenticate.py#L198  # noqa: E501
            if st.button('Logout', key='streamlit_authenticator_logout'):
                st.session_state.authenticator.cookie_manager.delete(
                    st.session_state.authenticator.cookie_name
                )

                # injected logic - wipe all data from the previous session
                for key in st.session_state.keys():
                    del st.session_state[key]

                st.session_state['logout'] = True
                st.session_state['name'] = None
                st.session_state['username'] = None
                st.session_state['authentication_status'] = None

                reset_session_state_progress()
                reset_session_state_asset_information()

        insert_line_break()

        st.caption(
            body=f'<p style="font-size: 10px; color: black;">v{__version__}</p>',
            unsafe_allow_html=True,
        )

        insert_line_break()
        insert_line_break()


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
        if (
            'page_zero_complete' in st.session_state.progress
            and 'page_one_complete' not in st.session_state.progress
        ):
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
        elif (
            'page_five_complete' in st.session_state.progress
            and 'page_six_complete' not in st.session_state.progress
        ):
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
