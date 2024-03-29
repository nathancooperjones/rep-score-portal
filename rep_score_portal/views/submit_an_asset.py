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
from input_output import append_new_row_in_asset_tracker, upload_file_to_s3
from utils import (
    change_upload_fields_colors,
    display_progress_bar_asset_tracker,
    edit_colors_of_selectbox,
    edit_colors_of_text_area,
    fetch_asset_data,
    get_content_types,
    get_countries_list,
    insert_line_break,
    remove_elements_from_progress_list,
    reset_session_state_asset_information,
    reset_session_state_progress,
)


def page_zero() -> None:
    st.markdown('## Before We Begin...')

    edit_colors_of_selectbox()

    asset_entered_before_option_str = (
        'Yes, a past version of this asset has been uploaded to the portal.'
    )

    seen_asset_before_status = st.radio(
        label='Has a version of this asset been uploaded to the Rep Score Portal before? :red[*]',
        options=[
            'No, a past version of this asset HAS NOT been uploaded to the portal before.',
            asset_entered_before_option_str,
        ],
        help=(
            'If you have uploaded a past version of the asset to the portal before, we can use the '
            "details you've already entered to autofill much of the asset submission process!"
        ),
    )

    if seen_asset_before_status == asset_entered_before_option_str:
        if not hasattr(st.session_state, 'asset_tracker_df'):
            fetch_asset_data()

        options = st.session_state.asset_tracker_df['Asset Name'].unique().tolist()

        if len(options) >= 1:
            selected_asset = st.selectbox(
                label=(
                    'Choose the asset whose details should be use to autofill the asset '
                    'submission process'
                ),
                options=options,
            )
        else:
            st.error(
                'We are unable to find an asset you have uploaded to the portal before! Please '
                'proceed to submit a new asset instead.'
            )

    if st.button('Continue to Step 1'):
        if seen_asset_before_status == asset_entered_before_option_str and selected_asset:
            selected_asset_df = (
                st.session_state.asset_tracker_df[
                    st.session_state.asset_tracker_df['Asset Name'] == selected_asset
                ]
                .iloc[-1]
            )

            st.session_state.asset_information['seen_asset_before'] = True
            st.session_state.asset_information['name'] = selected_asset_df['Asset Name']
            st.session_state.asset_information['brand'] = selected_asset_df['Brand']
            st.session_state.asset_information['product'] = selected_asset_df['Product']
            st.session_state.asset_information['countries_airing'] = (
                selected_asset_df['Region / Countries This Creative Will Air In']
                .replace('US', 'United States of America')  # 😐
                .split(', ')
            )
            st.session_state.asset_information['point_of_contact'] = (
                selected_asset_df['Point of Contact Email']
            )
            st.session_state.asset_information['creative_brief_filename'] = (
                selected_asset_df['Creative Brief Filename']
            )
            st.session_state.asset_information['version'] = int(selected_asset_df['Version']) + 1

            st.session_state.asset_information['marketing_1'] = (
                selected_asset_df[MARKETING_LABEL_1]
            )
            st.session_state.asset_information['marketing_2'] = (
                selected_asset_df[MARKETING_LABEL_2]
            )
            st.session_state.asset_information['marketing_3'] = (
                selected_asset_df[MARKETING_LABEL_3]
            )
            st.session_state.asset_information['marketing_4'] = (
                selected_asset_df[MARKETING_LABEL_4]
            )
            st.session_state.asset_information['agency_creative_1'] = (
                selected_asset_df[AGENCY_CREATIVE_LABEL_1]
            )
            st.session_state.asset_information['agency_creative_2'] = (
                selected_asset_df[AGENCY_CREATIVE_LABEL_2]
            )
            st.session_state.asset_information['agency_creative_3'] = (
                selected_asset_df[AGENCY_CREATIVE_LABEL_3]
            )
            st.session_state.asset_information['agency_creative_4'] = (
                selected_asset_df[AGENCY_CREATIVE_LABEL_4]
            )
            st.session_state.asset_information['agency_creative_5'] = (
                selected_asset_df[AGENCY_CREATIVE_LABEL_5]
            )
            st.session_state.asset_information['creative_review_1'] = (
                selected_asset_df[DEI_CREATIVE_REVIEWS_LABEL_1]
            )
            st.session_state.asset_information['creative_review_2'] = (
                selected_asset_df[DEI_CREATIVE_REVIEWS_LABEL_2]
            )
            st.session_state.asset_information['creative_review_3'] = (
                selected_asset_df[DEI_CREATIVE_REVIEWS_LABEL_3]
            )
            st.session_state.asset_information['creative_review_4'] = (
                selected_asset_df[DEI_CREATIVE_REVIEWS_LABEL_4]
            )
            st.session_state.asset_information['creative_review_5'] = (
                selected_asset_df[DEI_CREATIVE_REVIEWS_LABEL_5]
            )
            st.session_state.asset_information['notes'] = (
                selected_asset_df['Notes']
            )

            # post-processing - ensure every country entered is actually a country in the list
            st.session_state.asset_information['countries_airing'] = list(
                set(get_countries_list())
                & set(st.session_state.asset_information['countries_airing'])
            )

        st.session_state.progress.append('page_zero_complete')
        st.rerun()


def page_one() -> None:
    """Display the first page for the "Submit an Asset" process."""
    st.image('./static/Stage 1.png', use_column_width=True)

    # set up CSS for the creative brief upload input boxes
    creative_brief_filename_label = '... or enter a URL to the :blue[CREATIVE BRIEF]'

    change_upload_fields_colors(
        css_color='#0096DC',
        filename_label=creative_brief_filename_label,
    )

    st.markdown('## Start the Process')

    if st.button(label='← Previous Page', key='page_one_previous_page'):
        # reset to default
        st.session_state.asset_information['seen_asset_before'] = False

        remove_elements_from_progress_list(pages_to_remove=['page_zero_complete'])

        st.rerun()

    dei_resources_html = ("""
        <p>You can find a list of DEI resources
        <a style="color: #003749;" target="_blank"
        href="https://drive.google.com/file/d/1BIV123cWgiGRgKVvl-enGRTp37hA9Jqr/">
        here</a>.</p>
    """)

    st.markdown(dei_resources_html, unsafe_allow_html=True)

    asset_name = st.text_input(
        label='Asset Name :red[*]',
        value=st.session_state.asset_information['name'],
        placeholder='Ex: Pierre',
        help='Provide the name of the advertisement or other piece of content.',
    )
    asset_brand = st.text_input(
        label='Brand :red[*]',
        value=st.session_state.asset_information['brand'],
        placeholder='Ex: Mars',
    )
    asset_product = st.text_input(
        label='Product :red[*]',
        value=st.session_state.asset_information['product'],
        placeholder="Ex: M&M's",
    )
    countries_airing = st.multiselect(
        label='Region / Countries This Creative Will Air In :red[*]',
        options=get_countries_list(),
        default=st.session_state.asset_information['countries_airing'],
        help=(
            'Select the region(s) or countries that this advertisement will air in. Population '
            'comparisons are tailored to the region where the content will be aired.'
        ),
    )
    asset_point_of_contact = st.text_input(
        label='Point of Contact Email :red[*]',
        value=st.session_state.asset_information['point_of_contact'],
        placeholder='Ex: example@example.com',
        autocomplete='email',
        help='If we have questions about this asset, who should we reach out to?',
    )

    st.write('-----')

    st.write(
        '**Please either upload the :blue[CREATIVE BRIEF] or provide a URL to view your '
        ':blue[CREATIVE BRIEF]**'
    )

    insert_line_break()

    creative_brief = st.file_uploader(
        label='Select the :blue[CREATIVE BRIEF] to upload...',
        type=None,
        accept_multiple_files=False,
    )

    creative_brief_url = st.text_input(
        label=creative_brief_filename_label,
        value=st.session_state.asset_information['creative_brief_filename'],
        help=(
            'Rather than uploading a :blue[CREATIVE BRIEF], you can submit a URL to an '
            'already-uploaded :blue[CREATIVE BRIEF] that our coders can reference instead'
        ),
        placeholder='https://...',
    )

    st.write('-----')

    button_label = 'Continue to Step 2'

    if st.button(button_label):
        if (
            not asset_name
            or not asset_brand
            or not asset_product
            or not countries_airing
            or not asset_point_of_contact
        ):
            st.error('Please fill out all required fields before continuing.')
            st.stop()

        if creative_brief and creative_brief_url:
            st.error('Please either upload a :blue[CREATIVE BRIEF] _or_ provide a URL - not both.')
            st.stop()

        if creative_brief:
            with st.spinner(text='Uploading :blue[CREATIVE BRIEF]...'):
                creative_brief_filename = upload_file_to_s3(
                    uploaded_file=creative_brief,
                    s3_key='creative_briefs',
                )

                st.toast(body=f'Uploaded {creative_brief.name}!')
        else:
            creative_brief_filename = creative_brief_url

        st.session_state.asset_information['name'] = asset_name
        st.session_state.asset_information['brand'] = asset_brand
        st.session_state.asset_information['product'] = asset_product
        st.session_state.asset_information['countries_airing'] = countries_airing
        st.session_state.asset_information['point_of_contact'] = asset_point_of_contact
        st.session_state.asset_information['creative_brief_filename'] = creative_brief_filename

        st.session_state.progress.append('page_one_complete')

        st.rerun()


def page_two() -> None:
    """Display the second page for the "Submit an Asset" process."""
    st.image('./static/Stage 2.png', use_column_width=True)

    # set up CSS for the asset upload input boxes
    asset_upload_filename_label = '... or enter URL(s) to the :orange[ASSET(S)]'

    change_upload_fields_colors(
        css_color='#FFBD59',
        filename_label=asset_upload_filename_label,
    )

    st.markdown('## Upload Asset')

    edit_colors_of_text_area()

    if st.button(label='← Previous Page', key='page_two_previous_page'):
        remove_elements_from_progress_list(pages_to_remove=['page_one_complete'])

        st.rerun()

    st.write(
        'Use this portal to upload your content (advertisement, storyboard, working cut, '
        'final cut, etc.).'
    )

    st.write('-----')

    st.write(
        '**Please either upload your :orange[ASSET(S)] below or provide URL(s) to view your '
        ':orange[ASSET(S)]** :red[*]'
    )

    insert_line_break()

    uploaded_files = st.file_uploader(
        label='Select :orange[ASSET] file(s) to upload...',
        type=None,
        accept_multiple_files=True,
    )

    asset_url = st.text_input(
        label=asset_upload_filename_label,
        help=(
            'Rather than uploading :orange[ASSET(S)], you can submit URL(s) to already-uploaded '
            ':orange[ASSET(S)] that our coders can reference instead. For multiple URLs, separate '
            'each with a comma.'
        ),
        placeholder='https://...',
    )

    st.write('-----')

    asset_content_type = st.selectbox(
        label='Content Type :red[*]',
        options=get_content_types(),
    )
    asset_version = st.number_input(
        label='Version :red[*]',
        value=st.session_state.asset_information['version'],
        min_value=1,
    )

    notes = st.text_area(
        label='Notes',
        value=st.session_state.asset_information.get('notes', ''),
        height=200,
        help=(
            'Use this space to record any additional notes. This box has carried over as you '
            'advanced through the submission process.'
        ),
    )

    if uploaded_files or asset_url:
        if st.button('Upload!'):
            if uploaded_files and asset_url:
                st.error('Please either upload an :orange[ASSET] _or_ provide a URL - not both.')
                st.stop()

            st.session_state.asset_information['content_type'] = asset_content_type
            st.session_state.asset_information['version'] = asset_version
            st.session_state.asset_information['notes'] = notes

            if uploaded_files:
                asset_filename_list = list()

                with st.spinner(
                    text=f'Uploading :orange[ASSET{"S" if len(uploaded_files) > 1 else ""}]...',
                ):
                    for uploaded_file in uploaded_files:
                        asset_filename_list.append(
                            upload_file_to_s3(
                                uploaded_file=uploaded_file,
                                s3_key='uploads',
                            )
                        )

                        st.toast(body=f'Uploaded {uploaded_file.name}!')

                if len(asset_filename_list) == 1:
                    asset_filename = asset_filename_list[0]
                else:
                    asset_filename = ', '.join(asset_filename_list)

                file_uploaded_to_s3 = True
            else:
                asset_filename = asset_url
                file_uploaded_to_s3 = False

            with st.spinner(text='Setting up :orange[ASSET] tracking...'):
                append_new_row_in_asset_tracker(
                    asset_name=st.session_state.asset_information['name'],
                    username=st.session_state['username'],
                    brand=st.session_state.asset_information['brand'],
                    product=st.session_state.asset_information['product'],
                    countries_airing=st.session_state.asset_information['countries_airing'],
                    content_type=st.session_state.asset_information['content_type'],
                    version=st.session_state.asset_information['version'],
                    point_of_contact=st.session_state.asset_information['point_of_contact'],
                    creative_brief_filename=(
                        st.session_state.asset_information['creative_brief_filename']
                    ),
                    asset_filename=asset_filename,
                    file_uploaded_to_s3=file_uploaded_to_s3,
                    marketing_1_notes=st.session_state.asset_information['marketing_1'],
                    marketing_2_notes=st.session_state.asset_information['marketing_2'],
                    marketing_3_notes=st.session_state.asset_information['marketing_3'],
                    marketing_4_notes=st.session_state.asset_information['marketing_4'],
                    agency_creative_1_notes=st.session_state.asset_information['agency_creative_1'],
                    agency_creative_2_notes=st.session_state.asset_information['agency_creative_2'],
                    agency_creative_3_notes=st.session_state.asset_information['agency_creative_3'],
                    agency_creative_4_notes=st.session_state.asset_information['agency_creative_4'],
                    agency_creative_5_notes=st.session_state.asset_information['agency_creative_5'],
                    creative_review_1_notes=st.session_state.asset_information['creative_review_1'],
                    creative_review_2_notes=st.session_state.asset_information['creative_review_2'],
                    creative_review_3_notes=st.session_state.asset_information['creative_review_3'],
                    creative_review_4_notes=st.session_state.asset_information['creative_review_4'],
                    creative_review_5_notes=st.session_state.asset_information['creative_review_5'],
                    notes=st.session_state.asset_information['notes'],
                )

            st.session_state.progress.append('page_two_complete')
            st.rerun()


def page_three() -> None:
    """Display the final page for the "Submit an Asset" process."""
    if isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
        del st.session_state.asset_tracker_df
        del st.session_state.assigned_user_assets

    st.image('./static/Stage 3.png', use_column_width=True)

    st.markdown('## Summary')

    asset_name = st.session_state.asset_information['name']

    st.write(f"""
        Your asset `{asset_name}` has been uploaded and we'll begin work on it soon. It should now
        show up in the "Asset Overview" page.
    """)

    display_progress_bar_asset_tracker(
        asset_name=st.session_state.asset_information.get('name'),
        brand=st.session_state.asset_information.get('brand'),
        product=st.session_state.asset_information.get('product'),
        content_type=st.session_state.asset_information.get('content_type'),
        version=st.session_state.asset_information.get('version'),
        status='Uploaded',
        progress_value=(1/3),
    )

    upload_notes = (
        st.session_state.asset_information['notes']
        if st.session_state.asset_information.get('notes', '')
        else 'N/A'
    )

    progress_bar_css = ("""
        <style>
        div[data-testid="stText"] {
            width:200px;
            margin:0 auto;
            white-space: pre-wrap;      /* CSS3 */
            white-space: -moz-pre-wrap; /* Firefox */
            white-space: -o-pre-wrap;   /* Opera 7 */
            word-wrap: break-word;      /* IE */
        }
        </style>
    """)

    st.markdown(progress_bar_css, unsafe_allow_html=True)

    st.write('Notes submitted:')
    st.text(upload_notes)

    insert_line_break()

    if st.button('Back to home page'):
        reset_session_state_progress()
        reset_session_state_asset_information()

        st.session_state.refresh_app = True
        st.session_state.clear_radio = True

        st.rerun()
