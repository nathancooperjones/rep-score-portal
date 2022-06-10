from datetime import datetime
import os

import boto3
import gspread_pandas
import pandas as pd
import streamlit as st


def read_google_spreadsheet(spread: str, sheet: int = 0) -> pd.DataFrame:
    """
    Read a Google Spreadsheet as a Pandas DataFrame.

    Parameters
    ----------
    spread: str
        URL of the Google Spreadsheet to read in
    sheet: int
        Sheet of the Google Spreadsheet to read in

    Returns
    -------
    gspread_pandas.spread.Spread

    """
    return gspread_pandas.spread.Spread(
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


def upload_file_to_s3(uploaded_file: st.uploaded_file_manager.UploadedFile, s3_key: str) -> str:
    """
    Upload a file to S3 to ``s3://trp-rep-score-assets/{s3_key}/{modified_filename}``.

    Parameters
    ----------
    uploaded_file: st.uploaded_file_manager.UploadedFile
    s3_key: str

    Returns
    -------
    modified_filename: str
        Modified filename of the format
        ``{uploaded_file.name}_{current_timestamp}.{uploaded_file.extension}``

    Side Effects
    ------------
    Writes a file to S3.

    """
    uploaded_filename, uploaded_file_extension = os.path.splitext(uploaded_file.name)

    modified_filename = (
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
        .upload_fileobj(
            uploaded_file,
            'trp-rep-score-assets',
            os.path.join(s3_key, modified_filename),
        )
    )

    # try to trigger garbage collection early on the upload
    uploaded_file.close()
    del uploaded_file

    return modified_filename


def append_new_row_in_asset_tracker(
    asset_name: str,
    brand: str,
    product: str,
    content_type: str,
    version: str,
    creative_brief_filename: str,
    asset_filename: str,
    file_uploaded_to_s3: bool,
    marketing_notes: str,
    agency_creative_notes: str,
    creative_review_notes: str,
    notes: str,
) -> None:
    """
    Append a new row to the asset tracker Google Spreadsheet.

    Parameters
    ----------
    asset_name: str
    brand: str
    product: str
    content_type: str
    version: str
    creative_brief_filename: str
    asset_filename: str
    marketing_notes: str
    agency_creative_notes: str
    creative_review_notes: str
    notes: str

    Side Effects
    ------------
    Appends a new row to the asset tracking Google Spreadsheet.

    """
    sheet = read_google_spreadsheet(
        spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/',  # noqa: E501
        sheet=0,
    )

    asset_tracker_df = pd.concat(
        objs=[
            sheet.sheet_to_df(index=None),
            pd.Series({
                'Asset Name': asset_name,
                'Status': 'Uploaded',
                'Brand': brand,
                'Product': product,
                'Content Type': content_type,
                'Version': version,
                'Creative Brief Filename': creative_brief_filename,
                'Asset Filename': asset_filename,
                'File Uploaded to S3': file_uploaded_to_s3,
                'Date Submitted': datetime.today().strftime('%m/%d/%Y'),
                'Marketing Brief Notes': marketing_notes,
                'Agency Creative Brief Notes': agency_creative_notes,
                'Creative Reviews Notes': creative_review_notes,
                'Notes': notes,
            }).to_frame().transpose()
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
