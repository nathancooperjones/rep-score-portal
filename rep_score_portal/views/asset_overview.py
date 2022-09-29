import streamlit as st

from utils import (
    display_progress_bar_asset_tracker,
    edit_colors_of_selectbox,
    fetch_asset_data,
    insert_line_break,
)


def home_page() -> None:
    """Display the "Asset Overview" page."""
    st.markdown('## Asset Overview')

    fetch_asset_data()

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

    if len(st.session_state.asset_tracker_df) == 0:
        st.error(
            'You have not been assigned to view a submitted asset yet. Please either 1) submit a '
            'new asset on the "Submit an Asset" page or 2) click the "Having issues?" link and '
            'contact Rebecca Cooper be assigned to an existing asset.'
        )
    else:
        edit_colors_of_selectbox()

        filter_by = st.selectbox(
            label='Filter tracker by...',
            options=['None', 'Asset Name', 'Brand', 'Product', 'Content Type', 'Version'],
            help='Only display assets with the specified attribute',
        )

        if filter_by != 'None':
            field_selected = st.multiselect(
                label='Select values to display',
                options=sorted(st.session_state.asset_tracker_df[filter_by].unique()),
                default=sorted(st.session_state.asset_tracker_df[filter_by].unique()),
            )

        insert_line_break()

        if filter_by != 'None' and field_selected is not None:
            asset_tracker_df = st.session_state.asset_tracker_df[
                st.session_state.asset_tracker_df[filter_by].isin(field_selected)
            ]

            if len(asset_tracker_df) == 0:
                st.error(
                    "Hmm... we couldn't find any existing assets with those filters applied. "
                    'Please try again with a different set of filters.'
                )
                st.stop()
        else:
            asset_tracker_df = st.session_state.asset_tracker_df.copy()

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
