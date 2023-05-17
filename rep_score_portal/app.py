import copy

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

from footer import display_footer
from sidebar import construct_sidebar
from utils import (
    fetch_asset_data,
    insert_line_break,
    reset_session_state_asset_information,
    reset_session_state_progress,
)
from views.asset_overview import home_page
from views.explore_your_data import page_seven
from views.submit_an_asset import (
    # flake8... 🤦‍♂️
    page_five,
    page_four,
    page_one,
    page_six,
    page_three,
    page_two,
    page_zero,
)


st.set_page_config(page_title='Rep Score Portal', page_icon='🌀')


hide_streamlit_style = """
    <style>
        footer {
            visibility: hidden;
        }
        [title='View fullscreen'] {
            visibility: hidden;
        }

        h1 > div > a > svg {
            display: none;
        }
        h2 > div > a > svg {
            display: none;
        }
        h3 > div > a > svg {
            display: none;
        }
        h4 > div > a > svg {
            display: none;
        }
        h5 > div > a > svg {
            display: none;
        }
        h6 > div > a > svg {
            display: none;
        }

        .stRadio > label {
            font-size: 16px;
        }

        p {
            margin-bottom: 0.75rem;
        }

        @font-face{
            font-family:"LEMON MILK";
            src:url("https://trp-other.s3.amazonaws.com/fonts/LEMONMILK-Medium.otf") format("woff"),
            url("https://trp-other.s3.amazonaws.com/fonts/LEMONMILK-Medium.otf") format("opentype"),
            url("https://trp-other.s3.amazonaws.com/fonts/LEMONMILK-Medium.otf") format("truetype");
        }

        h1,h2,h3,h4,h5,h6 {
            font-family: 'LEMON MILK', sans-serif;
        }

        .stProgress > div > div > div {
            background-color: #F89C84;
            height: 1.5rem;
            margin-top: -0.5rem;
        }

        .stProgress > div > div > div > div {
            background-color: #F89C84;
        }

        div[role="progressbar"] > div > div {
            background-color: #FFD4B4;
        }

        div[role="progressbar"] > div > div > div {
            background-color: #F89C84;
        }

        .streamlit-expanderHeader {
            font-size: 16px;
            color: #683474;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .streamlit-expanderContent > div {
            line-height: 1.3rem;
        }

        .stTextArea > div > div {
            background-color: #C8C8C8;
        }

        div.stButton > button:first-child {
            background-color: #683474;
            border-color: #000000;
            color: #FAF4EB;
        }
        div.stButton > button:focus:not(:active) {
            background-color: #683474;
            border-color: #000000;
            color: #FAF4EB;
        }

        div.stButton > button:first-child > div > p {
            font-size: 20px;
        }

        .stTextInput > div > span {
            display: none;
        }

        .stMultiSelect > div > div > div > div > span > span {
            max-width: 250px;
        }

        div[data-baseweb="calendar"] > div > div > div > div {
            color: #333333;
        }
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.image('./static/Rep Score Portal Banner.png')


def determine_page() -> None:
    if st.session_state.get('clear_radio'):
        del st.session_state.clear_radio

        st.session_state.sidebar_radio = 'Asset Overview'

    if st.session_state.get('refresh_app'):
        del st.session_state.refresh_app

        st.experimental_rerun()

    fetch_asset_data()

    if st.session_state.get('sidebar_radio') == 'Submit an Asset':
        if 'page_five_complete' in st.session_state.progress:
            page_six()
        elif 'page_four_complete' in st.session_state.progress:
            page_five()
        elif 'page_three_complete' in st.session_state.progress:
            page_four()
        elif 'page_two_complete' in st.session_state.progress:
            page_three()
        elif 'page_one_complete' in st.session_state.progress:
            page_two()
        elif (
            'page_zero_complete' in st.session_state.progress
            or not isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame)
            or len(st.session_state.asset_tracker_df) == 0
        ):
            page_one()
        else:
            page_zero()
    elif st.session_state.get('sidebar_radio') == 'Explore Your Data':
        page_seven()
    else:
        if 'page_five_complete' in st.session_state.progress:
            reset_session_state_progress()
            reset_session_state_asset_information()

        home_page()


login_trouble_message_placeholder = None

if not st.session_state.get('authentication_status'):
    # this is likely the first time we are running the app - let's double check that
    authenticator = stauth.Authenticate(
        credentials=copy.deepcopy(
            x=st.secrets['logins']['credentials'].__dict__['__nested_secrets__'],  # oof
        ),
        cookie_name=st.secrets['authenticator']['cookie_name'],
        key=st.secrets['authenticator']['key'],
        cookie_expiry_days=st.secrets['authenticator']['cookie_expiry_days'],
        preauthorized=None,
    )

    authenticator.login(form_name='Login', location='main')

    if 'authenticator' not in st.session_state:
        st.session_state.authenticator = authenticator

    if st.session_state.get('authentication_status') is False:
        st.error('The username and/or password entered is incorrect - please try again.')
    elif st.session_state.get('authentication_status') is None:
        st.info('Please enter your username and password, then click the "Login" button.')

    insert_line_break()

    email_subject = 'Trouble Logging Into the Rep Score Portal'
    email_body = (
        "Hi Rebecca,%0D%0A%0D%0AI'm having some trouble logging into the Rep Score Portal. Can you "
        'please help me reset my portal login information?%0D%0A%0D%0AThank you!'
    )

    contact_html = (f"""
        <a style="color: #003749;"
        href="mailto:{st.secrets['authenticator']['contact_email_address']}?subject={email_subject}
        &body={email_body}">
        Having issues logging in?</a>
    """)

    login_trouble_message_placeholder = st.empty()
    login_trouble_message_placeholder.markdown(contact_html, unsafe_allow_html=True)

if st.session_state.get('authentication_status'):
    if login_trouble_message_placeholder is not None:
        # if not ``None``, then assume it is of type ``st.empty()``
        login_trouble_message_placeholder.empty()

    if 'progress' not in st.session_state:
        reset_session_state_progress()

    if 'asset_information' not in st.session_state:
        reset_session_state_asset_information()

    construct_sidebar()

    display_footer()

    determine_page()

# NOTE: anything past this point and NOT in the ``if`` block above will be displayed regardless of
# login status
