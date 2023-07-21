from typing import Iterable, List, Optional, Union


import pandas as pd
import streamlit as st

from input_output import get_assigned_user_assets, read_google_spreadsheet


def reset_session_state_progress() -> None:
    """Reset the ``st.session_state.progress`` list."""
    st.session_state.progress = list()


def reset_session_state_asset_information() -> None:
    """Reset the ``st.session_state.asset_information`` dictionary."""
    st.session_state.asset_information = {
        'seen_asset_before': False,
        'name': '',
        'brand': '',
        'product': '',
        'countries_airing': [],
        'point_of_contact': '',
        'creative_brief_filename': '',
        'version': 1,
        'marketing_1': '',
        'marketing_2': '',
        'marketing_3': '',
        'marketing_4': '',
        'agency_creative_1': '',
        'agency_creative_2': '',
        'agency_creative_3': '',
        'agency_creative_4': '',
        'agency_creative_5': '',
        'creative_review_1': '',
        'creative_review_2': '',
        'creative_review_3': '',
        'creative_review_4': '',
        'creative_review_5': '',
        'notes': '',
    }


def edit_colors_of_selectbox() -> None:
    """Color ``.stSelectbox`` CSS classes with a white fill and a black border."""
    selectbox_color_css = ("""
        <style>
        .stSelectbox > div > div {
            background-color: #FFFFFF;
            border-bottom-color: #000000;
            border-top-color: #000000;
            border-right-color: #000000;
            border-left-color: #000000;
        }
        </style>
    """)

    st.markdown(selectbox_color_css, unsafe_allow_html=True)


def edit_colors_of_text_area() -> None:
    """Color ``.stTextArea`` CSS classes with a light gray fill."""
    text_area_color_css = ("""
        <style>
        .stTextArea > div > div > div {
            background-color: #D7D7D7;
        }
        </style>
    """)

    st.markdown(text_area_color_css, unsafe_allow_html=True)


def remove_elements_from_progress_list(pages_to_remove: Union[str, Iterable[str]]) -> None:
    """
    Remove every element in ``pages_to_remove`` if it exists in ``st.session_state.progress``. If an
    element does not exist, the element will not be removed and an error will _NOT_ be raised.

    Parameters
    ----------
    pages_to_remove: str or list of str

    Side Effects
    ------------
    Modifies the elements in the ``st.session_state.progress`` list if any of ``pages_to_remove``
    existed in it before.

    """
    if isinstance(pages_to_remove, str):
        pages_to_remove = [pages_to_remove]

    for page in pages_to_remove:
        if page in st.session_state.progress:
            st.session_state.progress.remove(page)


def insert_line_break() -> None:
    """Insert line break in Streamlit app."""
    st.markdown('<br>', unsafe_allow_html=True)


def get_content_types() -> List[str]:
    """Get an ordered list of valid content types."""
    return [
        'Script',
        'Storyboard',
        'Animatic',
        'Rough Cut',
        'Final Cut',
        'Video',
    ]


def display_progress_bar_asset_tracker(
    asset_name: str,
    brand: Optional[str],
    product: Optional[str],
    content_type: Optional[str],
    version: Optional[str],
    status: str,
    progress_value: float,
) -> None:
    """
    Display the asset tracker expander with a progress bar visualization.

    Parameters
    ----------
    asset_name: str
    brand: str
    product: str
    content_type: str
    version: str
    status: str
    progress_value: float
        Float value between 0 and 1 to pass to ``st.progress``

    """
    with st.expander(label=asset_name, expanded=True):
        # st.write(f"**Brand**: {brand if brand else 'N/A'}")
        # st.write(f"**Product**: {product if product else 'N/A'}")
        # st.write(f"**Content Type**: {content_type if content_type else 'N/A'}")
        st.write(f"**Version**: {version if version else 'N/A'}")

        st.caption(f'<p style="text-align:right;">{status}</p>', unsafe_allow_html=True)

        st.progress(progress_value)


def check_for_assigned_assets() -> None:
    """Check for this user's assigned assets while displaying a ``st.spinner``."""
    with st.spinner(text='Checking for assigned assets...'):
        if not st.session_state['username']:
            st.session_state.assigned_user_assets = None
        elif not isinstance(st.session_state.get('assigned_user_assets'), list):
            st.session_state.assigned_user_assets = get_assigned_user_assets(
                username=st.session_state['username'],
            )

        if st.session_state['username'] in st.secrets['login_groups']['admins']:
            st.session_state.assigned_user_assets.append('_all_')


def fetch_asset_data() -> None:
    """
    Fetch the latest _assigned_ asset data and assign the resulting Pandas DataFrame to the
    ``st.session_state.asset_tracker_df`` variable.

    """
    check_for_assigned_assets()

    if (
        isinstance(st.session_state.get('assigned_user_assets'), list)
        and len(st.session_state.assigned_user_assets) > 0
    ):
        with st.spinner(text='Fetching the latest asset data...'):
            if not isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
                asset_tracker_df = (
                    read_google_spreadsheet(
                        spread=st.secrets['spreadsheets']['portal_backend_url'],
                        sheet=0,
                    )
                    .sheet_to_df(index=None)
                )

                asset_tracker_df['Date Submitted'] = (
                    pd
                    .to_datetime(arg=asset_tracker_df['Date Submitted'], format='mixed')
                    .dt
                    .date
                )

                if st.session_state['username'] not in st.secrets['login_groups']['admins']:
                    st.session_state.asset_tracker_df = asset_tracker_df[
                        asset_tracker_df['Asset Name'].isin(st.session_state.assigned_user_assets)
                    ]
                else:
                    st.session_state.asset_tracker_df = asset_tracker_df
    else:
        st.session_state.asset_tracker_df = None


def create_filters_selectboxes(
    df: pd.DataFrame,
    key_prefix: str,
    selectbox_label: str,
    filter_by_cols: Iterable[str],
    date_col: str = 'Date Submitted',
) -> pd.DataFrame:
    """
    Create two filter selectboxes to filter the assets displayed in a visualization.

    The first selectbox will allow the user to filter by the fields in ``filter_by_cols`` (plus an
    initial option called "-"), which should all be valid columns in ``df``.

    The second selectbox will appear if any non-"-" option is selected, allowing the user to select
    the proper fields from a ``multiselect`` input (or ``date_input`` for ``date_col``).

    Parameters
    ----------
    df: pd.DataFrame
    key_prefix: str
        Prefix for the selectbox keys, needed when this is used in multiple tabs on the same page.
        Every tab calling this function must provide a different value for this argument
    selectbox_label: str
        Label value to display in the initial selectbox rendered by this function
    filter_by_cols: list
        Columns in ``df`` to allow filtering by
    date_col: str
        Column in ``df`` and ``filter_by_cols`` containing a date field to filter by, used to
        present a better selectbox for the second-round filter

    Returns
    -------
    filtered_df: pd.DataFrame
        Filtered-down DataFrame ready for visualization

    """
    filter_by = st.selectbox(
        label=selectbox_label,
        options=['-'] + filter_by_cols,
        help='Only display assets with the specified attribute',
        key=f'{key_prefix}_filter_by_selectbox',
    )

    field_selected = None
    min_date = None
    max_date = None

    if filter_by != '-':
        if filter_by == date_col:
            col_1, col_2 = st.columns(2)

            with col_1:
                min_date = st.date_input(
                    label='Earliest submitted date to consider',
                    value=df[date_col].min(),
                    key=f'{key_prefix}_min_date_date_input',
                )

            with col_2:
                max_date = st.date_input(
                    label='Latest submitted date to consider',
                    key=f'{key_prefix}_max_date_date_input',
                )
        else:
            filter_by_options = sorted(df[filter_by].unique())

            field_selected = st.multiselect(
                label='Select values to display',
                options=filter_by_options,
                default=filter_by_options,
                key=f'{key_prefix}_field_selected_multiselect',
            )

    filtered_df = df

    if (
        filter_by != '-'
        and (field_selected is not None or min_date is not None or max_date is not None)
    ):
        if filter_by == date_col:
            filtered_df = df[(df[date_col] >= min_date) & (df[date_col] <= max_date)]
        else:
            filtered_df = df[df[filter_by].isin(field_selected)]

    return filtered_df


def change_upload_fields_colors(css_color: str, filename_label: str) -> None:
    """
    Use custom CSS code to change the colors of both the upload box and filename field needed for
    files that can be uploading during the "Submit an Asset" process.

    Parameters
    ----------
    css_color: str
        Color to change the upload box and URL field to
    filename_label: str
        The ``label`` argument passed to the field for accepting a URL to an already-uploaded file

    """
    upload_inputs_css = f"""
        <style>
            div[data-testid="stFileUploader"] > section {{
                background-color: {css_color};
            }}

            div[data-testid="stFileUploader"] > section > div > span {{
                color: #000000;
            }}

            input[aria-label="{filename_label}"] {{
                background-color: {css_color};
            }}
        </style>
    """

    st.markdown(upload_inputs_css, unsafe_allow_html=True)


def get_countries_list() -> List[str]:
    """Return a list of all countries."""
    return [
        'United States of America',
        'Latin America',
        'Europe',
        'Global',
        'Afghanistan',
        'Albania',
        'Algeria',
        'Andorra',
        'Angola',
        'Antigua and Barbuda',
        'Argentina',
        'Armenia',
        'Australia',
        'Austria',
        'Azerbaijan',
        'The Bahamas',
        'Bahrain',
        'Bangladesh',
        'Barbados',
        'Belarus',
        'Belgium',
        'Belize',
        'Benin',
        'Bhutan',
        'Bolivia',
        'Bosnia and Herzegovina',
        'Botswana',
        'Brazil',
        'Brunei',
        'Bulgaria',
        'Burkina Faso',
        'Burundi',
        'Cambodia',
        'Cameroon',
        'Canada',
        'Cape Verde',
        'Central African Republic',
        'Chad',
        'Chile',
        'China',
        'Colombia',
        'Comoros',
        'Congo, Republic of the',
        'Congo, Democratic Republic of the',
        'Costa Rica',
        "Cote d'Ivoire",
        'Croatia',
        'Cuba',
        'Cyprus',
        'Czech Republic',
        'Denmark',
        'Djibouti',
        'Dominica',
        'Dominican Republic',
        'East Timor (Timor-Leste)',
        'Ecuador',
        'Egypt',
        'El Salvador',
        'Equatorial Guinea',
        'Eritrea',
        'Estonia',
        'Ethiopia',
        'Fiji',
        'Finland',
        'France',
        'Gabon',
        'The Gambia',
        'Georgia',
        'Germany',
        'Ghana',
        'Greece',
        'Grenada',
        'Guatemala',
        'Guinea',
        'Guinea-Bissau',
        'Guyana',
        'Haiti',
        'Honduras',
        'Hungary',
        'Iceland',
        'India',
        'Indonesia',
        'Iran',
        'Iraq',
        'Ireland',
        'Israel',
        'Italy',
        'Jamaica',
        'Japan',
        'Jordan',
        'Kazakhstan',
        'Kenya',
        'Kiribati',
        'Korea, North',
        'Korea, South',
        'Kosovo',
        'Kuwait',
        'Kyrgyzstan',
        'Laos',
        'Latvia',
        'Lebanon',
        'Lesotho',
        'Liberia',
        'Libya',
        'Liechtenstein',
        'Lithuania',
        'Luxembourg',
        'Macedonia',
        'Madagascar',
        'Malawi',
        'Malaysia',
        'Maldives',
        'Mali',
        'Malta',
        'Marshall Islands',
        'Mauritania',
        'Mauritius',
        'Mexico',
        'Micronesia, Federated States of',
        'Moldova',
        'Monaco',
        'Mongolia',
        'Montenegro',
        'Morocco',
        'Mozambique',
        'Myanmar (Burma)',
        'Namibia',
        'Nauru',
        'Nepal',
        'Netherlands',
        'New Zealand',
        'Nicaragua',
        'Niger',
        'Nigeria',
        'Norway',
        'Oman',
        'Pakistan',
        'Palau',
        'Panama',
        'Papua New Guinea',
        'Paraguay',
        'Peru',
        'Philippines',
        'Poland',
        'Portugal',
        'Qatar',
        'Romania',
        'Russia',
        'Rwanda',
        'Saint Kitts and Nevis',
        'Saint Lucia',
        'Saint Vincent and the Grenadines',
        'Samoa',
        'San Marino',
        'Sao Tome and Principe',
        'Saudi Arabia',
        'Senegal',
        'Serbia',
        'Seychelles',
        'Sierra Leone',
        'Singapore',
        'Slovakia',
        'Slovenia',
        'Solomon Islands',
        'Somalia',
        'South Africa',
        'South Sudan',
        'Spain',
        'Sri Lanka',
        'Sudan',
        'Suriname',
        'Swaziland',
        'Sweden',
        'Switzerland',
        'Syria',
        'Taiwan',
        'Tajikistan',
        'Tanzania',
        'Thailand',
        'Togo',
        'Tonga',
        'Trinidad and Tobago',
        'Tunisia',
        'Turkey',
        'Turkmenistan',
        'Tuvalu',
        'Uganda',
        'Ukraine',
        'United Arab Emirates',
        'United Kingdom',
        'Uruguay',
        'Uzbekistan',
        'Vanuatu',
        'Vatican City (Holy See)',
        'Venezuela',
        'Vietnam',
        'Yemen',
        'Zambia',
        'Zimbabwe',
    ]
