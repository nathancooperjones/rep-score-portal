import streamlit as st


def clear_session_state_progress():
    """TODO."""
    st.session_state.progress = list()


def clear_session_state_asset_information():
    """TODO."""
    st.session_state.asset_information = dict()
