import pandas as pd
import streamlit as st

from input_output import read_google_spreadsheet
from utils import display_progress_bar_asset_tracker


def home_page() -> None:
    """Display the "Asset Overview" page."""
    st.markdown('## Asset Overview')

    with st.spinner(text='Fetching the latest asset data...'):
        if not isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
            st.session_state.asset_tracker_df = (
                read_google_spreadsheet(
                    spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/',  # noqa: E501
                    sheet=0,
                )
                .sheet_to_df(index=None)
            )

    if st.session_state.asset_information.get('name'):
        st.markdown('### In Progress Assets')

        if (
            'page_one_complete' not in st.session_state.progress
        ):
            progress_value = ((0/6) / 3)
        elif (
            'page_one_complete' in st.session_state.progress
            and 'page_two_complete' not in st.session_state.progress
        ):
            progress_value = ((1/6) / 3)
        elif (
            'page_two_complete' in st.session_state.progress
            and 'page_three_complete' not in st.session_state.progress
        ):
            progress_value = ((2/6) / 3)
        elif (
            'page_three_complete' in st.session_state.progress
            and 'page_four_complete' not in st.session_state.progress
        ):
            progress_value = ((3/6) / 3)
        elif (
            'page_four_complete' in st.session_state.progress
            and 'page_five_complete' not in st.session_state.progress
        ):
            progress_value = ((4/6) / 3)
        else:
            progress_value = ((1/3))

        display_progress_bar_asset_tracker(
            asset_name=st.session_state.asset_information.get('name'),
            brand=st.session_state.asset_information.get('brand'),
            product=st.session_state.asset_information.get('product'),
            content_type=st.session_state.asset_information.get('content_type'),
            version=st.session_state.asset_information.get('version'),
            status='Not yet uploaded',
            progress_value=progress_value,
        )

        st.write('-----')

    # TODO: add filtering here too

    st.markdown('### Submitted Assets')

    for _, row in st.session_state.asset_tracker_df.iterrows():
        if row['Status'] == 'Uploaded':
            progress_value = ((1/3))
        elif row['Status'] == 'In progress':
            progress_value = ((2/3))
        elif row['Status'] == 'Complete':
            progress_value = ((3/3))

        display_progress_bar_asset_tracker(
            asset_name=row['Asset Name'],
            brand=row['Brand'],
            product=row['Product'],
            content_type=row['Content Type'],
            version=row['Version'],
            status=row["Status"],
            progress_value=progress_value,
        )
