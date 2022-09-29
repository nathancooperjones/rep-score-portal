import pandas as pd
import streamlit as st

from input_output import append_new_row_in_asset_tracker, upload_file_to_s3
from utils import (
    display_progress_bar_asset_tracker,
    edit_colors_of_selectbox,
    fetch_asset_data,
    get_content_types,
    get_countries_list,
    insert_line_break,
)


def page_zero() -> None:
    st.markdown('## Before We Begin...')

    edit_colors_of_selectbox()

    asset_entered_before_option_str = (
        'Yes, a past version of this asset has been uploaded to the portal.'
    )

    seen_asset_before_status = st.radio(
        label='Has a version of this asset been uploaded to the Rep Score Portal before?',
        options=[
            'No, a past version of this asset HAS NOT been uploaded to the portal before.',
            asset_entered_before_option_str,
        ],
        help=(
            'If you have uploaded a past version of the asset to the portal before, we can use the '
            "details you've already entered to auto-fill and skip much of the asset submission "
            'process!'
        ),
    )

    if seen_asset_before_status == asset_entered_before_option_str:
        fetch_asset_data()

        options = st.session_state.asset_tracker_df['Asset Name'].tolist()

        if len(options) >= 1:
            selected_asset = st.selectbox(
                label=(
                    'Choose the asset whose details should be use to auto-fill the asset '
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
                selected_asset_df['Region(s) This Creative Will Air In']
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

            # post-processing - ensure every country entered is actually a country in the list
            st.session_state.asset_information['countries_airing'] = list(
                set(get_countries_list())
                & set(st.session_state.asset_information['countries_airing'])
            )

        st.session_state.progress.append('page_zero_complete')
        st.experimental_rerun()


def page_one() -> None:
    """Display the first page for the "Submit an Asset" process."""
    st.image('../images/Stage 1.png', use_column_width=True)

    st.markdown('## Start the Process')

    asset_name = st.text_input(
        label='Asset Name',
        value=st.session_state.asset_information['name'],
        placeholder='Ex: Pierre',
    )
    asset_brand = st.text_input(
        label='Brand',
        value=st.session_state.asset_information['brand'],
        placeholder='Ex: Mars',
    )
    asset_product = st.text_input(
        label='Product',
        value=st.session_state.asset_information['product'],
        placeholder="Ex: M&M's",
    )
    countries_airing = st.multiselect(
        label='Region(s) This Creative Will Air In',
        options=get_countries_list(),
        default=st.session_state.asset_information['countries_airing'],
    )
    asset_point_of_contact = st.text_input(
        label='Point of Contact Email',
        value=st.session_state.asset_information['point_of_contact'],
        placeholder='Ex: example@example.com',
        autocomplete='email',
        help='If we have questions about this asset, who should we reach out to?',
    )

    st.write('-----')

    st.write(
        '**Please either upload the creative brief or provide a URL to view your creative brief**'
    )

    insert_line_break()

    creative_brief = st.file_uploader(
        label='Select the creative brief to upload...',
        type=None,
        accept_multiple_files=False,
    )

    creative_brief_url = st.text_input(
        label='... or enter a URL to the creative brief',
        value=st.session_state.asset_information['creative_brief_filename'],
        help=(
            'Rather than uploading a creative brief, you can submit a URL to an already-uploaded '
            'creative brief that our coders can reference instead'
        ),
        placeholder='https://...',
    )

    st.write('-----')

    button_label = 'Continue to Step 2'

    if st.session_state.asset_information['seen_asset_before']:
        button_label = 'Skip ahead to Step 5'

    if st.button(button_label):
        if (
            not asset_name
            or not asset_brand
            or not asset_product
            or not countries_airing
            or not asset_point_of_contact
        ):
            st.error('Please fill out all fields before continuing.')
            st.stop()

        if creative_brief and creative_brief_url:
            st.error('Please either upload a creative brief _or_ provide a URL - not both.')
            st.stop()

        if creative_brief:
            with st.spinner(text='Uploading creative brief...'):
                creative_brief_filename = upload_file_to_s3(
                    uploaded_file=creative_brief,
                    s3_key='creative_briefs',
                )
        else:
            creative_brief_filename = creative_brief_url

        st.session_state.asset_information['name'] = asset_name
        st.session_state.asset_information['brand'] = asset_brand
        st.session_state.asset_information['product'] = asset_product
        st.session_state.asset_information['countries_airing'] = countries_airing
        st.session_state.asset_information['point_of_contact'] = asset_point_of_contact
        st.session_state.asset_information['creative_brief_filename'] = creative_brief_filename

        st.session_state.progress.append('page_one_complete')

        if st.session_state.asset_information['seen_asset_before']:
            st.session_state.progress.append('page_two_complete')
            st.session_state.progress.append('page_three_complete')
            st.session_state.progress.append('page_four_complete')

        st.experimental_rerun()


def page_two() -> None:
    """Display the second page for the "Submit an Asset" process."""
    st.image('../images/Stage 2.png', use_column_width=True)

    st.markdown('## Marketing Brief')

    st.caption('Please check all boxes below or provide notes to continue')

    marketing_1 = st.checkbox(
        'DE&I can be reflected in our High Value Communities or audience definitions'
    )
    marketing_2 = st.checkbox(
        'All additional growth audience(s) are considered, or prioritized'
    )
    marketing_3 = st.checkbox(
        'We have the opportunity to personalize our work to different DE&I communities'
    )
    marketing_4 = st.checkbox(
        'This project (or business opportunity) intersects with social issues'
    )

    marketing_notes = st.text_area(label='Notes on Marketing Brief')

    if (
        (
            marketing_1
            and marketing_2
            and marketing_3
            and marketing_4
        ) or marketing_notes
    ):
        if st.button('Continue to Step 3'):
            st.session_state.asset_information['marketing_notes'] = marketing_notes

            st.session_state.progress.append('page_two_complete')
            st.experimental_rerun()


def page_three() -> None:
    """Display the third page for the "Submit an Asset" process."""
    st.image('../images/Stage 3.png', use_column_width=True)

    st.markdown('## Agency Creative Brief')

    st.caption('Please check all boxes below or provide notes to continue')

    agency_creative_1 = st.checkbox(
        'We have considered where we are sourcing data and inspiration for this project'
    )
    agency_creative_2 = st.checkbox(
        'We are getting a full picture of the audience, getting a more diverse perspective'
    )
    agency_creative_3 = st.checkbox(
        'We dispel any relevant stereotypes about the audience'
    )
    agency_creative_4 = st.checkbox(
        'We are gaining input or inspiration from the audience'
    )
    agency_creative_5 = st.checkbox(
        'Our creative references and thought starters are as diverse, equal, and inclusive as the '
        'work we hope to make'
    )

    agency_creative_notes = st.text_area(label='Notes on Agency Creative')

    if (
        (
            agency_creative_1
            and agency_creative_2
            and agency_creative_3
            and agency_creative_4
            and agency_creative_5
        ) or agency_creative_notes
    ):
        if st.button('Continue to Step 4'):
            st.session_state.asset_information['agency_creative_notes'] = agency_creative_notes

            st.session_state.progress.append('page_three_complete')
            st.experimental_rerun()


def page_four() -> None:
    """Display the fourth page for the "Submit an Asset" process."""
    st.image('../images/Stage 4.png', use_column_width=True)

    st.markdown('## DE&I Discussion in the Creative Reviews')

    st.caption('Please check all boxes below or provide notes to continue')

    creative_review_1 = st.checkbox(
        'We can reasonably make the work more inclusive, equitable, and representative at this '
        'stage'
    )
    creative_review_2 = st.checkbox(
        'The work is not reinforcing negative stereotypes'
    )
    creative_review_3 = st.checkbox(
        'There are no cultural references we are misappropriating'
    )
    creative_review_4 = st.checkbox(
        'We are inclusive with regard to age, body type, disability, ethnicity, gender, and sexual '
        'orientation'
    )
    creative_review_5 = st.checkbox(
        'We, and our clients, made choices that lead to more inclusive and equitable work'
    )

    creative_review_notes = st.text_area(label='Notes on Creative Reviews')

    if (
        (
            creative_review_1
            and creative_review_2
            and creative_review_3
            and creative_review_4
            and creative_review_5
        ) or creative_review_notes
    ):
        if st.button('Continue to Step 5'):
            st.session_state.asset_information['creative_review_notes'] = creative_review_notes

            st.session_state.progress.append('page_four_complete')
            st.experimental_rerun()


def page_five() -> None:
    """Display the fifth page for the "Submit an Asset" process."""
    st.image('../images/Stage 5.png', use_column_width=True)

    st.markdown('## Upload Asset')

    st.write(
        'Use this portal to upload your content (advertisement, storyboard, working cut, '
        'final cut, etc.).'
    )

    st.write('-----')

    st.write('**Please either upload your asset below or provide a URL to view your asset**')

    insert_line_break()

    uploaded_file = st.file_uploader(
        label='Select a file to upload...',
        type=None,
        accept_multiple_files=False,
    )

    asset_url = st.text_input(
        label='... or enter a URL to the asset',
        help=(
            'Rather than uploading an asset, you can submit a URL to an already-uploaded asset '
            'that our coders can reference instead'
        ),
        placeholder='https://...',
    )

    st.write('-----')

    asset_content_type = st.selectbox(
        label='Content Type',
        options=get_content_types(),
    )
    asset_version = st.number_input(
        label='Version',
        value=st.session_state.asset_information['version'],
        min_value=1,
    )

    asset_notes = st.text_area(label='Notes', height=200)

    if uploaded_file or asset_url:
        if st.button('Upload!'):
            if uploaded_file and asset_url:
                st.error('Please either upload an asset _or_ provide a URL - not both.')
                st.stop()

            st.session_state.asset_information['content_type'] = asset_content_type
            st.session_state.asset_information['version'] = asset_version
            st.session_state.asset_information['notes'] = asset_notes

            if uploaded_file:
                with st.spinner(text='Uploading asset...'):
                    asset_filename = upload_file_to_s3(
                        uploaded_file=uploaded_file,
                        s3_key='uploads',
                    )

                file_uploaded_to_s3 = True
            else:
                asset_filename = asset_url
                file_uploaded_to_s3 = False

            with st.spinner(text='Setting up asset tracking...'):
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
                    marketing_notes=st.session_state.asset_information.get('marketing_notes', ''),
                    agency_creative_notes=(
                        st.session_state.asset_information.get('agency_creative_notes', '')
                    ),
                    creative_review_notes=(
                        st.session_state.asset_information.get('creative_review_notes', '')
                    ),
                    notes=st.session_state.asset_information['notes'],
                )

            st.session_state.progress.append('page_five_complete')
            st.experimental_rerun()


def page_six() -> None:
    """Display the final page for the "Submit an Asset" process."""
    if isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
        del st.session_state.asset_tracker_df
        del st.session_state.assigned_user_assets

    st.image('../images/Stage 6.png', use_column_width=True)

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

    marketing_notes = (
        st.session_state.asset_information['marketing_notes']
        if st.session_state.asset_information.get('marketing_notes')
        else 'N/A'
    )
    agency_creative_notes = (
        st.session_state.asset_information['agency_creative_notes']
        if st.session_state.asset_information.get('agency_creative_notes')
        else 'N/A'
    )
    creative_review_notes = (
        st.session_state.asset_information['creative_review_notes']
        if st.session_state.asset_information.get('creative_review_notes')
        else 'N/A'
    )
    upload_notes = (
        st.session_state.asset_information['notes']
        if st.session_state.asset_information.get('notes')
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

    st.write("""
        Notes submitted:

        * **Marketing Brief Notes**:
    """)
    st.text(marketing_notes)

    st.write('* **Agency Creative Brief Notes**:')
    st.text(agency_creative_notes)

    st.write('* **Creative Reviews Notes**:')
    st.text(creative_review_notes)

    st.write('* **Upload Notes**:')
    st.text(upload_notes)

    insert_line_break()

    if st.button('Back to home page'):
        st.session_state.refresh_app = True
        st.session_state.clear_radio = True

        st.experimental_rerun()
