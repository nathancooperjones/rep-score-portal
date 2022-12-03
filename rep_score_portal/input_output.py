from datetime import datetime
import os
from typing import List

import boto3
import gspread_pandas
import pandas as pd
import streamlit as st

from config import (
    AGENCY_CREATIVE_LABEL_1,
    AGENCY_CREATIVE_LABEL_2,
    AGENCY_CREATIVE_LABEL_3,
    AGENCY_CREATIVE_LABEL_4,
    AGENCY_CREATIVE_LABEL_5,
    DEI_CREATIVE_REVIEWS_LABEL_1,
    DEI_CREATIVE_REVIEWS_LABEL_2,
    DEI_CREATIVE_REVIEWS_LABEL_3,
    DEI_CREATIVE_REVIEWS_LABEL_4,
    DEI_CREATIVE_REVIEWS_LABEL_5,
    MARKETING_LABEL_1,
    MARKETING_LABEL_2,
    MARKETING_LABEL_3,
    MARKETING_LABEL_4,
)


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


def upload_file_to_s3(uploaded_file: st.runtime.uploaded_file_manager, s3_key: str) -> str:
    """
    Upload a file to S3 to ``s3://trp-rep-score-assets/{s3_key}/{modified_filename}``.

    Parameters
    ----------
    uploaded_file: st.runtime.uploaded_file_manager
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
    username: str,
    brand: str,
    product: str,
    countries_airing: List[str],
    content_type: str,
    version: str,
    point_of_contact: str,
    creative_brief_filename: str,
    asset_filename: str,
    file_uploaded_to_s3: bool,
    marketing_1_notes: str,
    marketing_2_notes: str,
    marketing_3_notes: str,
    marketing_4_notes: str,
    agency_creative_1_notes: str,
    agency_creative_2_notes: str,
    agency_creative_3_notes: str,
    agency_creative_4_notes: str,
    agency_creative_5_notes: str,
    creative_review_1_notes: str,
    creative_review_2_notes: str,
    creative_review_3_notes: str,
    creative_review_4_notes: str,
    creative_review_5_notes: str,
    notes: str,
) -> None:
    """
    Append a new row to the asset tracker Google Spreadsheet.

    Parameters
    ----------
    asset_name: str
    username: str
    brand: str
    product: str
    countries_airing: list
    content_type: str
    version: str
    point_of_contact: str
    creative_brief_filename: str
    asset_filename: str
    marketing_1_notes: str
    marketing_2_notes: str
    marketing_3_notes: str
    marketing_4_notes: str
    agency_creative_1_notes: str
    agency_creative_2_notes: str
    agency_creative_3_notes: str
    agency_creative_4_notes: str
    agency_creative_5_notes: str
    creative_review_1_notes: str
    creative_review_2_notes: str
    creative_review_3_notes: str
    creative_review_4_notes: str
    creative_review_5_notes: str
    notes: str

    Side Effects
    ------------
    Appends a new row to the asset tracking Google Spreadsheet.

    """
    sheet = read_google_spreadsheet(
        spread=st.secrets['spreadsheets']['portal_backend_url'],
        sheet=0,
    )

    if not isinstance(countries_airing, list):
        countries_airing = [countries_airing]

    new_row_df = pd.DataFrame(
        data=[
            {
                'Asset Name': asset_name,
                'Username': username,
                'Status': 'Uploaded',
                'Brand': brand,
                'Product': product,
                'Region(s) This Creative Will Air In': ', '.join(countries_airing),
                'Content Type': content_type,
                'Version': version,
                'Point of Contact Email': point_of_contact,
                'Creative Brief Filename': creative_brief_filename,
                'Asset Filename': asset_filename,
                'File Uploaded to S3': file_uploaded_to_s3,
                'Date Submitted': datetime.today().strftime('%m/%d/%Y'),
                MARKETING_LABEL_1: marketing_1_notes,
                MARKETING_LABEL_2: marketing_2_notes,
                MARKETING_LABEL_3: marketing_3_notes,
                MARKETING_LABEL_4: marketing_4_notes,
                AGENCY_CREATIVE_LABEL_1: agency_creative_1_notes,
                AGENCY_CREATIVE_LABEL_2: agency_creative_2_notes,
                AGENCY_CREATIVE_LABEL_3: agency_creative_3_notes,
                AGENCY_CREATIVE_LABEL_4: agency_creative_4_notes,
                AGENCY_CREATIVE_LABEL_5: agency_creative_5_notes,
                DEI_CREATIVE_REVIEWS_LABEL_1: creative_review_1_notes,
                DEI_CREATIVE_REVIEWS_LABEL_2: creative_review_2_notes,
                DEI_CREATIVE_REVIEWS_LABEL_3: creative_review_3_notes,
                DEI_CREATIVE_REVIEWS_LABEL_4: creative_review_4_notes,
                DEI_CREATIVE_REVIEWS_LABEL_5: creative_review_5_notes,
                'Notes': notes,
            }
        ],
    )

    new_row_index = sheet.get_sheet_dims()[0] + 1

    sheet.df_to_sheet(
        df=new_row_df,
        index=False,
        headers=None,
        start=(new_row_index, 1),
        replace=False,
    )


def get_assigned_user_assets(username: str) -> List[str]:
    """
    Retrieve a list of assets that have been assigned for the user to view details on.

    Parameters
    ----------
    username: str

    Returns
    -------
    allowed_assets: list
        List of assigned assets or assets uploaded by that specific user. If none are assigned, an
        empty list will be returned

    """
    tracker_df = (
        read_google_spreadsheet(
            spread=st.secrets['spreadsheets']['project_tracker_url'],
            sheet=3,
        )
        .sheet_to_df(index=None)
    )

    specific_user_tracker_df = tracker_df[tracker_df['Username'] == username]

    if len(specific_user_tracker_df) > 0:
        allowed_assets_tracker = [
            x.strip()
            for x in specific_user_tracker_df['Access To'].item().split(',')
            if x.strip() != 'None'
        ]
    else:
        allowed_assets_tracker = []

    backend_df = (
        read_google_spreadsheet(
            spread=st.secrets['spreadsheets']['portal_backend_url'],
            sheet=0,
        )
        .sheet_to_df(index=None)
    )

    specific_user_backend_df = backend_df[backend_df['Username'] == username]

    if len(specific_user_backend_df) > 0:
        allowed_assets_backend = specific_user_backend_df['Asset Name'].tolist()
    else:
        allowed_assets_backend = []

    return list(set(allowed_assets_tracker) | set(allowed_assets_backend))
