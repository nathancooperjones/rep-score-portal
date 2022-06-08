from datetime import datetime
import os

import boto3
import gspread_pandas
import pandas as pd
import streamlit as st


def upload_file_and_update_tracker(uploaded_file: st.uploaded_file_manager.UploadedFile) -> None:
    """TODO."""
    uploaded_filename, uploaded_file_extension = os.path.splitext(uploaded_file.name)
    full_filename = (
        uploaded_filename
        + '_'
        + str(int(datetime.now().timestamp()))
        + uploaded_file_extension
    )

    (
        boto3
        .client(
            's3',
            aws_access_key_id=st.secrets['aws']['access_key_id'],
            aws_secret_access_key=st.secrets['aws']['secret_access_key'],
        )
        .upload_fileobj(uploaded_file, 'trp-rep-score-assets', f'uploads/{full_filename}')
    )

    # try to trigger garbage collection early
    uploaded_file.close()
    del uploaded_file

    # set up Google API client
    sheet = read_google_spreadsheet(
        spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/',  # noqa: E501
        sheet=0,
    )

    asset_tracker_df = sheet.sheet_to_df(index=None)

    # uploaded, sent, recieved, notes
    asset_tracker_df = pd.concat(
        objs=[
            asset_tracker_df,
            pd.Series({
                'Asset Name': st.session_state.asset_information['name'],
                'Brand': st.session_state.asset_information['brand'],
                'Product': st.session_state.asset_information['product'],
                'Content Type': st.session_state.asset_information['content_type'],
                'Version': st.session_state.asset_information['version'],
                'Filename': full_filename,
                'Date Submitted': datetime.today().strftime('%m/%d/%Y'),
                'Status': 'Uploaded',
                'Marketing Brief Notes': st.session_state.asset_information['marketing_notes'],
                'Agency Creative Brief Notes': st.session_state.asset_information['agency_creative_notes'],  # noqa: E501
                'Creative Reviews Notes': st.session_state.asset_information['creative_review_notes'],  # noqa: E501
                'Notes': st.session_state.asset_information['notes'],
            })
        ],
        ignore_index=True,
    )

    # TODO: figure out how to do this without replacement
    sheet.df_to_sheet(
        df=asset_tracker_df,
        index=False,
        sheet='Sheet1',
        replace=True,
    )


def read_google_spreadsheet(spread: str, sheet: int = 0) -> pd.DataFrame:
    """TODO."""
    # set up Google API client
    sheet = gspread_pandas.spread.Spread(
        spread=spread,
        sheet=sheet,
        config={
            'type': st.secrets['gcp']['type'],
            'project_id': st.secrets['gcp']['project_id'],
            'private_key_id': st.secrets['gcp']['private_key_id'],
            'private_key': st.secrets['gcp']['private_key'],
            'client_email': st.secrets['gcp']['client_email'],
            'client_id': st.secrets['gcp']['client_id'],
            'auth_uri': st.secrets['gcp']['auth_uri'],
            'token_uri': st.secrets['gcp']['token_uri'],
            'auth_provider_x509_cert_url': st.secrets['gcp']['auth_provider_x509_cert_url'],
            'client_x509_cert_url': st.secrets['gcp']['client_x509_cert_url'],
        },
    )

    return sheet.sheet_to_df(index=None)
