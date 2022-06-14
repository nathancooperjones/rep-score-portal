import random
import string

import streamlit as st
import streamlit_authenticator as stauth

from footer import display_footer
from sidebar import construct_sidebar_prefix, construct_sidebar_suffix
from utils import reset_session_state_asset_information, reset_session_state_progress
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
)


st.set_page_config(page_title='Rep Score Portal', page_icon='🌀')


hide_streamlit_style = """
    <link href="http://fonts.cdnfonts.com/css/lemon-milk" rel="stylesheet">
    <style>
        #MainMenu {visibility: hidden;}
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
            src:url("https://nathancooperjones.com/LEMONMILK-Medium.otf") format("woff"),
            url("https://nathancooperjones.com/LEMONMILK-Medium.otf") format("opentype"),
            url("https://nathancooperjones.com/LEMONMILK-Medium.otf") format("truetype");
        }

        h1,h2,h3,h4,h5,h6 {
            font-family: 'LEMON MILK', sans-serif;
        }

        .stProgress > div > div > div {
            background-color: gray;
            height: 1.5rem;
            margin-top: -0.5rem;
        }

        .stProgress > div > div > div > div {
            background-color: green;
        }

        div[role="progressbar"] > div > div {
            background-color: gray;
        }

        div[role="progressbar"] > div > div > div {
            background-color: green;
        }

        .streamlit-expanderHeader {
            font-size: 16px;
            color: #EA3423;
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
            background-color: #2A2526;
            color: #FAF4EB;
            font-size: 20px;
        }
        div.stButton > button:focus:not(:active) {
            background-color: #2A2526;
            color: #FAF4EB;
            font-size: 20px;
        }
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)


random.seed(42)


usernames = list(st.secrets['logins'].keys())
passwords = list(st.secrets['logins'].values())

authenticator = stauth.Authenticate(
    names=usernames,
    usernames=usernames,
    passwords=stauth.Hasher(passwords).generate(),
    cookie_name='trp_rep_score_cookie',
    key=''.join(random.choices(string.ascii_letters + string.digits, k=50)),
    cookie_expiry_days=7,
)


construct_sidebar_prefix()

st.image('../images/Rep Score Portal Banner.png')


name, authentication_status, username = authenticator.login('Login', 'main')


def determine_page():
    if st.session_state.get('clear_radio'):
        del st.session_state.clear_radio

        st.session_state.sidebar_radio = 'Asset Overview'

    if st.session_state.get('refresh_app'):
        del st.session_state.refresh_app

        st.experimental_rerun()

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
        else:
            page_one()
    elif st.session_state.get('sidebar_radio') == 'Explore Your Data':
        page_seven()
    else:
        if 'page_five_complete' in st.session_state.progress:
            reset_session_state_progress()
            reset_session_state_asset_information()

        home_page()


if authentication_status is False:
    st.error('Username and/or password is incorrect - please try again.')
    st.stop()
elif authentication_status is None:
    st.warning('Please enter your username and password.')
    st.stop()
else:
    if 'important' not in st.session_state:
        st.session_state.important = dict()

        st.session_state.important['username'] = username
        st.session_state.important['name'] = name

    if 'progress' not in st.session_state:
        reset_session_state_progress()

    if 'asset_information' not in st.session_state:
        reset_session_state_asset_information(reload_page=False)

    construct_sidebar_suffix(authenticator=authenticator)

    display_footer()

    determine_page()
