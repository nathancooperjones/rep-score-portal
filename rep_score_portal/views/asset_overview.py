import warnings

import pandas as pd
import st_aggrid
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
    TOO_FILTERED_DOWN_ERROR_MESSAGE,
)
from utils import (
    create_filters_selectboxes,
    display_progress_bar_asset_tracker,
    edit_colors_of_selectbox,
    fetch_asset_data,
    insert_line_break,
)


def home_page() -> None:
    """Display the "Asset Overview" page."""
    st.markdown('## Asset Overview')

    fetch_asset_data()

    tab_1, tab_2 = st.tabs(['Asset Information', 'Progress of All Available Assets'])

    with tab_1:
        view_asset_information()
    with tab_2:
        view_progress_of_all_available_assets()

    if not st.session_state.get('hacky_experimental_rerun_for_asset_overview_first_page_load'):
        st.session_state.hacky_experimental_rerun_for_asset_overview_first_page_load = True
        st.rerun()


def view_asset_information() -> None:
    """View all details and uploaded notes about a specific version of an assigned asset."""
    if (
        not isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame)
        or len(st.session_state.asset_tracker_df) == 0
    ):
        st.error(
            'You have not been assigned to view a submitted asset yet. Please either 1) submit a '
            'new asset on the "Submit an Asset" page or 2) click the "Having issues?" link and '
            'contact Rebecca Cooper be assigned to an existing asset.'
        )
        st.stop()

    asset_selected = st.selectbox(
        label="Select an asset whose details you'd like to view",
        options=['-'] + sorted(st.session_state.asset_tracker_df['Asset Name'].unique()),
    )

    if asset_selected and asset_selected != '-':
        df_to_display = (
            st.session_state.asset_tracker_df[
                st.session_state.asset_tracker_df['Asset Name'] == asset_selected
            ]
            .rename(columns={'Username': 'Submitted By'})
        )

        if len(df_to_display) == 0:
            st.error('Hmm... something went wrong here. Sorry, please refresh and try again.')
            st.stop()

        cols_to_display = [
            'Asset Name',
            'Date Submitted',
            'Version',
            'Submitted By',
            'Status',
            'Brand',
            'Product',
            'Region / Countries This Creative Will Air In',
            'Content Type',
        ]

        grid_options = st_aggrid.grid_options_builder.GridOptionsBuilder.from_dataframe(
            dataframe=df_to_display[cols_to_display],
        )
        grid_options.configure_selection(selection_mode='single')
        grid_options = grid_options.build()

        # random, but... ¯\_(ツ)_/¯
        height = 63 + (len(df_to_display) * 28)

        if len(df_to_display) > 1:
            st.caption('Click a row below to view more details about that asset.')

        with warnings.catch_warnings():
            # oof
            warnings.filterwarnings('ignore', module=r'.*st_aggrid*')

            data = st_aggrid.AgGrid(
                data=df_to_display,
                gridOptions=grid_options,
                update_mode=st_aggrid.shared.GridUpdateMode.SELECTION_CHANGED,
                height=height,
                enable_enterprise_modules=False,
            )

        if len(data['selected_rows']) > 0 or len(df_to_display) == 1:
            if len(df_to_display) == 1:
                # auto-select the only possible row - don't make the user have to waste a click
                row_selected = df_to_display.iloc[0]
            else:
                row_selected = data['selected_rows'][0]

            non_note_cols_to_display = [
                'Submitted By',
                'Version',
                'Brand',
                'Product',
                'Region / Countries This Creative Will Air In',
                'Content Type',
                'Point of Contact Email',
                'Date Submitted',
            ]

            note_cols_to_display = [
                MARKETING_LABEL_1,
                MARKETING_LABEL_2,
                MARKETING_LABEL_3,
                MARKETING_LABEL_4,
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
                'Notes',
            ]

            st.markdown(body=f'### {row_selected["Asset Name"]}')

            for col in non_note_cols_to_display:
                st.markdown(body=f'**{col}**: {row_selected[col]}')

            insert_line_break()

            for col in note_cols_to_display:
                st.markdown(body=f'**{col if col != "Notes" else "Notes:"}**')

                if row_selected[col] and row_selected[col] != 'N/A':
                    st.text(body=f'{row_selected[col]}')
                else:
                    st.text(body='N/A')


def view_progress_of_all_available_assets() -> None:
    """View coding progress of all pending and assigned uploaded assets."""
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

    st.markdown('### Submitted Assets')

    if (
        not isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame)
        or len(st.session_state.asset_tracker_df) == 0
    ):
        st.error(
            'You have not been assigned to view a submitted asset yet. Please either 1) submit a '
            'new asset on the "Submit an Asset" page or 2) click the "Having issues?" link and '
            'contact Rebecca Cooper be assigned to an existing asset.'
        )
        st.stop()

    edit_colors_of_selectbox()

    asset_tracker_df = create_filters_selectboxes(
        df=st.session_state.asset_tracker_df,
        key_prefix='view_progress_of_all_available_assets',
        selectbox_label='Filter tracker by...',
        filter_by_cols=[
            'Asset Name',
            'Brand',
            'Product',
            'Content Type',
            'Version',
            'Date Submitted',
        ],
        date_col='Date Submitted',
    )

    insert_line_break()

    if len(asset_tracker_df) == 0:
        st.error(TOO_FILTERED_DOWN_ERROR_MESSAGE)
        return

    for _, row in asset_tracker_df.iterrows():
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
