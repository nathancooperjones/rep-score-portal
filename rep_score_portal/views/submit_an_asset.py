import pandas as pd
import streamlit as st

from input_output import upload_file_and_update_tracker


def page_one():
    st.image('../images/Stage 1.png', use_column_width=True)

    st.markdown('## Start the Process')

    asset_name = st.text_input(label='Asset Name', placeholder='Ex: Pierre')
    asset_brand = st.text_input(label='Brand', placeholder='Ex: Mars')
    asset_product = st.text_input(label='Product', placeholder="Ex: M&M's")
    countries_airing = st.multiselect(
        label='Region(s) This Creative Will Air In',
        options=[
            'United States of America',
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
    )

    # TODO: finish this
    creative_brief = st.file_uploader(label='Creative Brief')

    st.markdown('<br>', unsafe_allow_html=True)

    if st.button('Continue to next step'):
        if (
            not asset_name
            or not asset_brand
            or not asset_product
            or not countries_airing
        ):
            st.error('Please fill out all fields before continuing.')
            st.stop()

        st.session_state.asset_information['name'] = asset_name
        st.session_state.asset_information['brand'] = asset_brand
        st.session_state.asset_information['product'] = asset_product
        st.session_state.asset_information['countries_airing'] = countries_airing

        st.session_state.progress.append('page_one_complete')
        st.experimental_rerun()


def page_two():
    st.image('../images/Stage 2.png', use_column_width=True)

    st.markdown('## Marketing Brief')

    st.caption('Please check all boxes below to continue or provide notes')

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
        if st.button('Continue to next step'):
            st.session_state.asset_information['marketing_notes'] = marketing_notes

            st.session_state.progress.append('page_two_complete')
            st.experimental_rerun()


def page_three():
    st.image('../images/Stage 3.png', use_column_width=True)

    st.markdown('## Agency Creative Brief')

    st.caption('Please check all boxes below to continue or provide notes')

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
        if st.button('Continue to next step'):
            st.session_state.asset_information['agency_creative_notes'] = agency_creative_notes

            st.session_state.progress.append('page_three_complete')
            st.experimental_rerun()


def page_four():
    st.image('../images/Stage 4.png', use_column_width=True)

    st.markdown('## DE&I Discussion in the Creative Reviews')

    st.caption('Please check all boxes below to continue or provide notes')

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
        if st.button('Continue to next step'):
            st.session_state.asset_information['creative_review_notes'] = creative_review_notes

            st.session_state.progress.append('page_four_complete')
            st.experimental_rerun()


def page_five():
    st.image('../images/Stage 5.png', use_column_width=True)

    st.markdown('## Upload Asset')

    st.write(
        'Use this portal to upload your content (advertisement, storyboard, working cut, '
        'final cut, etc.).'
    )

    uploaded_file = st.file_uploader(
        label='Select a file to upload',
        type=None,
        accept_multiple_files=False,
    )

    asset_content_type = st.selectbox(
        label='Content Type',
        options=['Storyboard', 'Working Cut', 'Final Cut'],
    )
    asset_version = st.number_input(label='Version', min_value=1)

    asset_notes = st.text_area(label='Notes', height=200)

    if uploaded_file:
        if st.button('Upload!'):
            st.session_state.asset_information['content_type'] = asset_content_type
            st.session_state.asset_information['version'] = asset_version
            st.session_state.asset_information['notes'] = asset_notes

            with st.spinner(text='Uploading file...'):
                upload_file_and_update_tracker(uploaded_file=uploaded_file)

            # TODO: add a function to do this
            if isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
                del st.session_state.asset_tracker_df

            st.session_state.progress.append('page_five_complete')
            st.experimental_rerun()


def page_six():
    st.image('../images/Stage 6.png', use_column_width=True)

    st.markdown('## Summary')

    asset_name = st.session_state.asset_information['name']

    st.write(f"""
        Your asset `{asset_name}` has been uploaded and we'll begin work on it soon. It should now
        show up in the "Asset Overview" page.
    """)

    with st.expander(label=st.session_state.asset_information.get('name'), expanded=True):
        st.write(f"**Asset Name**: {st.session_state.asset_information.get('name')}")
        st.write(f"**Brand**: {st.session_state.asset_information.get('brand')}")
        st.write(f"**Product**: {st.session_state.asset_information.get('product')}")
        st.write(f"**Content Type**: {st.session_state.asset_information.get('content_type')}")
        st.write(f"**Version**: {st.session_state.asset_information.get('version')}")

        st.caption('<p style="text-align:right;">Uploaded</p>', unsafe_allow_html=True)

        st.progress((1/3))

    marketing_notes = (
        st.session_state.asset_information['marketing_notes']
        if st.session_state.asset_information['marketing_notes']
        else 'N/A'
    )
    agency_creative_notes = (
        st.session_state.asset_information['agency_creative_notes']
        if st.session_state.asset_information['agency_creative_notes']
        else 'N/A'
    )
    creative_review_notes = (
        st.session_state.asset_information['creative_review_notes']
        if st.session_state.asset_information['creative_review_notes']
        else 'N/A'
    )

    st.write(f"""
        Notes submitted:

        * **Marketing Brief Notes**: {marketing_notes}
        * **Agency Creative Brief Notes**: {agency_creative_notes}
        * **Creative Reviews**: {creative_review_notes}
    """)

    st.markdown('<br>', unsafe_allow_html=True)

    if st.button('Back to home page'):
        st.session_state.refresh_app = True
        st.session_state.clear_radio = True
        # main()
        st.experimental_rerun()
