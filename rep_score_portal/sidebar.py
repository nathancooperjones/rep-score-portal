import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

from _version import __version__
from utils import clear_session_state_asset_information, clear_session_state_progress


def construct_sidebar_prefix() -> None:
    with st.sidebar:
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)

        _, col_2, _ = st.columns([1, 27, 1])

        with col_2:
            st.image('../images/Mars Petcare Logo Square.png', use_column_width=True)

        st.markdown('<br>', unsafe_allow_html=True)


def construct_sidebar_suffix(authenticator: stauth.Authenticate) -> None:
    """TODO."""
    with st.sidebar:
        st.markdown('')

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

        if st.session_state.get('sidebar_radio') == 'Submit an Asset':
            # TODO: clean this up a bit
            if (
                'page_one_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p style="color:#fff;"><strong>1. Start the Process</strong></p>
                    <p>2. DEI Checklist: Marketing Brief<p>
                    <p>3. DEI Checklist: Agency Creative Brief<p>
                    <p>4. DEI Checklist: Creative Reviews<p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)
                with submit_an_asset_pages_navigation_container:
                    st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_one_complete' in st.session_state.progress
                and 'page_two_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p style="color:#fff;"><strong>2. DEI Checklist: Marketing Brief</strong></p>
                    <p>3. DEI Checklist: Agency Creative Brief<p>
                    <p>4. DEI Checklist: Creative Reviews<p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)
                with submit_an_asset_pages_navigation_container:
                    st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_two_complete' in st.session_state.progress
                and 'page_three_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p style="color:#fff;"><strong>3. DEI Checklist: Agency Creative Brief</strong></p>
                    <p>4. DEI Checklist: Creative Reviews<p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)  # noqa: E501
                with submit_an_asset_pages_navigation_container:
                    st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_three_complete' in st.session_state.progress
                and 'page_four_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p>3. DEI Checklist: Agency Creative Brief</p>
                    <p style="color:#fff;"><strong>4. DEI Checklist: Creative Reviews</strong></p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)
                with submit_an_asset_pages_navigation_container:
                    st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_four_complete' in st.session_state.progress
                and 'page_five_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p>3. DEI Checklist: Agency Creative Brief</p>
                    <p>4. DEI Checklist: Creative Reviews</p>
                    <p style="color:#fff;"><strong>5. Upload Asset</strong></p>
                    <p>6. Summary<p>
                """)
                with submit_an_asset_pages_navigation_container:
                    st.markdown(navigation_string, unsafe_allow_html=True)
            else:
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p>3. DEI Checklist: Agency Creative Brief</p>
                    <p>4. DEI Checklist: Creative Reviews</p>
                    <p>5. Upload Asset</p>
                    <p style="color:#fff;"><strong>6. Summary</strong></p>
                """)
                with submit_an_asset_pages_navigation_container:
                    st.markdown(navigation_string, unsafe_allow_html=True)
        else:
            navigation_string = ("""
                <p>1. Start the Process</p>
                <p>2. DEI Checklist: Marketing Brief<p>
                <p>3. DEI Checklist: Agency Creative Brief<p>
                <p>4. DEI Checklist: Creative Reviews<p>
                <p>5. Upload Asset<p>
                <p>6. Summary<p>
            """)
            with submit_an_asset_pages_navigation_container:
                st.markdown(navigation_string, unsafe_allow_html=True)

        if st.session_state.get('sidebar_radio') == 'Explore Your Data':
            st.markdown('<br>', unsafe_allow_html=True)

            st.session_state.sidebar_data_explorer_radio = st.radio(
                label='Select a visualization to view:',
                options=('Score Heatmap', 'Rep Score Progress', 'Qualitative Notes'),
                index=0,
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
                    clear_session_state_progress()
                    clear_session_state_asset_information()

                    st.session_state.refresh_app = True

                    # main()
                    st.experimental_rerun()
            else:
                if st.button('Refresh'):
                    st.session_state.refresh_app = True

                    if isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
                        del st.session_state.asset_tracker_df
                    if isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame):
                        del st.session_state.data_explorer_df

                    # main()
                    st.experimental_rerun()

        with col_2:
            authenticator.logout('Logout', 'main')

        st.markdown('<br>', unsafe_allow_html=True)

        st.caption(f'<p style="color: black;">v{__version__}</p>', unsafe_allow_html=True)
