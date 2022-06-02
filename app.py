from datetime import datetime
import json
import os
import random
import string

import altair as alt
import boto3
import gspread_pandas
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

from footer import display_footer


st.set_page_config(page_title='Rep Score Portal', page_icon='🌀')


hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)


random.seed(42)

authenticator = stauth.Authenticate(
    names=['Test User'],
    usernames=['user'],
    passwords=stauth.Hasher(['test']).generate(),
    cookie_name='trp_rep_score_cookie',
    key=''.join(random.choices(string.ascii_letters + string.digits, k=50)),
    cookie_expiry_days=7,
)

with st.sidebar:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    _, col_2, _ = st.columns([1, 30, 1])

    with col_2:
        st.image('images/Mars Petcare Logo Square.png', use_column_width=True)

    st.markdown('<br>', unsafe_allow_html=True)


name, authentication_status, username = authenticator.login('Login', 'main')


def upload_file_and_update_tracker(uploaded_file: st.uploaded_file_manager.UploadedFile) -> None:
    """TODO."""
    with open('credentials/aws_credentials.json', 'r') as fp:
        aws_credentials_dict = json.load(fp)

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
            aws_access_key_id=aws_credentials_dict['aws_access_key_id'],
            aws_secret_access_key=aws_credentials_dict['aws_secret_access_key'],
        )
        .upload_fileobj(uploaded_file, 'trp-rep-score-assets', f'uploads/{full_filename}')
    )

    # set up Google API client
    sheet = gspread_pandas.spread.Spread(
        spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/edit',  # noqa: E501
        sheet=0,
        config=(
            gspread_pandas.conf.get_config(conf_dir='.', file_name='credentials/credentials.json')
        ),
    )

    asset_tracker_df = sheet.sheet_to_df(index=None)

    # uploaded, sent, recieved, notes
    asset_tracker_df = asset_tracker_df.append(
        other=pd.Series({
            'Asset Name': st.session_state.asset_information['name'],
            'Brand': st.session_state.asset_information['brand'],
            'Product': st.session_state.asset_information['product'],
            'Content Type': st.session_state.asset_information['content_type'],
            'Version': st.session_state.asset_information['version'],
            'Filename': full_filename,
            'Date Submitted': datetime.today().strftime('%m/%d/%Y'),
            'Status': 'Uploaded',
            'Notes': st.session_state.asset_information['notes'],
        }),
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
        config=gspread_pandas.conf.get_config(
            conf_dir='.',
            file_name='credentials/credentials.json',
        ),
    )

    return sheet.sheet_to_df(index=None)


def plot_color_maps(df: pd.DataFrame) -> alt.vegalite.v4.api.Chart:
    """TODO."""
    if len(df) == 0:
        st.write("We couldn't find any existing assets to view yet - sorry!")
        return

    df = df.rename(columns={
        'Product ': 'Product',
        'TOTAL (GENDER)': 'GENDER',
        'TOTAL (RACE)': 'RACE',
        'TOTAL (LGBTQ)': 'LGBTQ+ ',  # the space is intentional, sadly
        'TOTAL (Disability)': 'DISABILITY',
        'TOTAL (50+)': 'AGE',
        'TOTAL (Fat)': 'BODY SIZE',
    })

    if st.session_state.sidebar_data_explorer_radio == 'Score Heatmap':
        cols_to_select_subset = [
            'Ad Name',
            'Brand',
            'Product',
            'Content Type',
            'Date Submitted',
            'Qual Notes',
            'GENDER',
            'RACE',
            'LGBTQ+ ',
            'DISABILITY',
            'AGE',
            'BODY SIZE',
            'Ad Total Score',
        ]

        df_to_plot = (
            df[cols_to_select_subset]
            .set_index(
                ['Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted', 'Qual Notes']
            )
            .stack()
            .reset_index()
            .rename(columns={0: 'Score', 'level_6': 'Variable'})
        )

        df_to_plot['Date Submitted'] = pd.to_datetime(df_to_plot['Date Submitted']).dt.date

        filter_by = st.selectbox(
            label='Filter visualization by...',
            options=['None', 'Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted'],
        )

        field_selected = None
        min_date = None
        max_date = None

        text_area_color_css = ("""
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

        st.markdown(text_area_color_css, unsafe_allow_html=True)

        if filter_by != 'None':
            if filter_by == 'Date Submitted':
                col_1, col_2 = st.columns(2)

                with col_1:
                    min_date = st.date_input(
                        label='Earliest submitted date to consider',
                        value=df_to_plot['Date Submitted'].min(),
                    )

                with col_2:
                    max_date = st.date_input(label='Latest submitted date to consider')
            else:
                field_selected = st.multiselect(
                    label='Choose a field to compare against',
                    options=sorted(df_to_plot[filter_by].unique()),
                    default=sorted(df_to_plot[filter_by].unique()),
                )

        st.write('')

        if filter_by != 'None' and (field_selected or min_date or max_date):
            if filter_by == 'Date Submitted':
                df_to_plot = df_to_plot[
                    (df_to_plot['Date Submitted'] >= min_date)
                    & (df_to_plot['Date Submitted'] <= max_date)
                ]
            else:
                df_to_plot = df_to_plot[df_to_plot[filter_by].isin(field_selected)]

        if len(df_to_plot) == 0:
            st.write("We couldn't find any existing assets with those filters applied!")
            return

        df_to_plot['color'] = [
            '#7ED957' if float(x) >= 80
            else '#FFDE59' if 60 <= float(x) < 80
            else '#EA3423'
            for x in df_to_plot['Score']
        ]

        overall_df_to_plot = df_to_plot[df_to_plot['Variable'] == 'Ad Total Score']
        subset_df_to_plot = df_to_plot[df_to_plot['Variable'] != 'Ad Total Score']

        base = (
            alt
            .Chart(overall_df_to_plot)
            .encode(
                x='Variable',
                y='Ad Name',
            )
        )

        chart = (
            base
            .mark_rect(size=100, stroke='black', strokeWidth=0.5)
            .encode(
                alt.X(
                    shorthand='Variable',
                    axis=alt.Axis(
                        orient='top',
                        labelAngle=-45,
                        tickSize=0,
                        labelPadding=10,
                        title=None,
                    )
                ),
                alt.Y(
                    shorthand='Ad Name',
                    axis=alt.Axis(tickSize=0, labelPadding=10, titlePadding=20)
                ),
                color=alt.Color('color', scale=None),
                tooltip=['Ad Name', 'Brand', 'Product', 'Score'],
            ).properties(
                height=300,
            )
        )

        text = base.mark_text().encode(text='Score')

        full_plot = (
            (chart + text)
            .configure_axis(
                labelFontSize=15,
                labelFontWeight=alt.FontWeight('bold'),
                titleFontSize=15,
                titleFontWeight=alt.FontWeight('normal'),
            )
        )

        st.altair_chart(full_plot, use_container_width=True)

        st.caption(
            '\\* Note that when multiple versions of an asset have been submitted, the most-recent '
            'version will be displayed above. To see multiple versions plotted over time, click '
            '"Rep Score Progress" on the left sidebar.'
        )

        st.write('-----')

        if st.checkbox('Break down by identity'):
            sort = [
                'GENDER',
                'RACE',
                'LGBTQ+ ',
                'DISABILITY',
                'AGE',
                'BODY SIZE',
            ]

            subset_base = (
                alt
                .Chart(subset_df_to_plot)
                .encode(
                    alt.X(
                        shorthand='Variable',
                        sort=sort,
                        axis=alt.Axis(
                            orient='top',
                            labelAngle=-45,
                            tickSize=0,
                            labelPadding=10,
                            title=None,
                        )
                    ),
                    alt.Y(
                        shorthand='Ad Name',
                        axis=alt.Axis(tickSize=0, labelPadding=10, titlePadding=20)
                    ),
                )
            )

            subset_chart = (
                subset_base
                .mark_rect(size=100, stroke='black', strokeWidth=0.5)
                .encode(
                    color=alt.Color('color', scale=None),
                    tooltip=['Ad Name', 'Brand', 'Product', 'Variable', 'Score'],
                ).properties(
                    height=300,
                )
            )

            subset_text = subset_base.mark_text().encode(text='Score')

            subset_plot = (
                (subset_chart + subset_text)
                .configure_axis(
                    labelFontSize=15,
                    labelFontWeight=alt.FontWeight('bold'),
                    titleFontSize=15,
                    titleFontWeight=alt.FontWeight('normal'),
                )
            )

            st.altair_chart(subset_plot, use_container_width=True)

    elif st.session_state.sidebar_data_explorer_radio == 'Rep Score Progress':
        x_axis = st.selectbox(
            label='Select field to view by',
            options=['Content Type', 'Date Submitted'],
        )

        if x_axis == 'Date Submitted':
            x_axis = 'Date Submitted Month Year'

        st.write('')

        progress_df = st.session_state.data_explorer_df[
            st.session_state.data_explorer_df[['Ad Name', 'Brand', 'Product ']]
            .duplicated(keep=False)
        ]

        progress_df = progress_df[[
            'Content Type',
            'Ad Total Score',
            'Ad Name',
            'Brand',
            'Product ',
            'Date Submitted',
        ]]

        progress_df['Ad Total Score'] = progress_df['Ad Total Score'].astype(float)
        progress_df['Date Submitted Month Year'] = (
            pd
            .to_datetime(progress_df['Date Submitted'])
            .dt
            .date
            .apply(lambda x: x.strftime('%b %Y'))
        )

        progress_chart = (
            alt
            .Chart(progress_df)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    shorthand=x_axis,
                    sort=['Storyboard', 'Working Cut', 'Final Cut'],
                    axis=alt.Axis(
                        labelAngle=-45,
                        labelPadding=5,
                    )
                ),
                y='Ad Total Score',
                color='Ad Name',
                strokeDash='Ad Name',
                tooltip=['Ad Name', 'Brand', 'Product ', 'Date Submitted', 'Ad Total Score'],
            ).properties(
                height=500,
            ).configure_point(
                size=100,
            )
        )

        st.altair_chart(progress_chart, use_container_width=True)

        st.write('-----')

    elif st.session_state.sidebar_data_explorer_radio == 'Qualitative Notes':
        notes_df = df.copy()

        notes_df = notes_df.drop_duplicates(
            subset=['Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted', 'Qual Notes']
        )

        for _, row in notes_df.iterrows():
            with st.expander(f'"{row["Ad Name"]}" Notes', expanded=False):
                notes = 'No notes! 🎉'

                if row['Qual Notes']:
                    notes = row['Qual Notes']

                st.write(notes)


def home_page():
    st.markdown('## Asset Overview')

    with st.spinner(text='Fetching the latest asset data...'):
        if not isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
            st.session_state.asset_tracker_df = read_google_spreadsheet(
                spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/edit',  # noqa: E501
                sheet=0,
            )

    if st.session_state.asset_information.get('name'):
        st.markdown('### In Progress Assets')

        with st.expander(label=st.session_state.asset_information.get('name'), expanded=True):
            # TODO: handle nulls better here
            st.write(f"**Asset Name**: {st.session_state.asset_information.get('name')}")
            st.write(f"**Brand**: {st.session_state.asset_information.get('brand')}")
            st.write(f"**Product**: {st.session_state.asset_information.get('product')}")
            st.write(f"**Content Type**: {st.session_state.asset_information.get('content_type')}")
            st.write(f"**Version**: {st.session_state.asset_information.get('version')}")

            # TODO: be more specific here
            st.caption('<p style="text-align:right;">Not yet uploaded</p>', unsafe_allow_html=True)

            if (
                'page_one_complete' not in st.session_state.progress
            ):
                st.progress((0/6) / 3)
            elif (
                'page_one_complete' in st.session_state.progress
                and 'page_two_complete' not in st.session_state.progress
            ):
                st.progress((1/6) / 3)
            elif (
                'page_two_complete' in st.session_state.progress
                and 'page_three_complete' not in st.session_state.progress
            ):
                st.progress((2/6) / 3)
            elif (
                'page_three_complete' in st.session_state.progress
                and 'page_four_complete' not in st.session_state.progress
            ):
                st.progress((3/6) / 3)
            elif (
                'page_four_complete' in st.session_state.progress
                and 'page_five_complete' not in st.session_state.progress
            ):
                st.progress((4/6) / 3)
            else:
                # TODO: no 5/9?
                st.progress((1/3))

        st.write('-----')

    # TODO: add filtering here too

    st.markdown('### Submitted Assets')

    for _, row in st.session_state.asset_tracker_df.iterrows():
        with st.expander(label=row['Asset Name'], expanded=True):
            st.write(f"**Asset Name**: {row['Asset Name']}")
            st.write(f"**Brand**: {row['Brand']}")
            st.write(f"**Product**: {row['Product']}")
            st.write(f"**Content Type**: {row['Content Type']}")
            st.write(f"**Version**: {row['Version']}")

            st.caption(f'<p style="text-align:right;">{row["Status"]}</p>', unsafe_allow_html=True)

            if row['Status'] == 'Uploaded':
                st.progress((1/3))
            elif row['Status'] == 'In progress':
                st.progress((2/3))
            elif row['Status'] == 'Complete':
                st.progress((3/3))


def page_one():
    st.image('images/Stage 1.png', use_column_width=True)

    st.markdown('## Start the Process')

    asset_name = st.text_input(label='Asset Name', placeholder='Ex: Pierre')
    asset_brand = st.text_input(label='Brand', placeholder='Ex: Mars')
    asset_product = st.text_input(label='Product', placeholder="Ex: M&M's")

    if st.button('Continue to next step'):
        if (
            not asset_name
            or not asset_brand
            or not asset_product
        ):
            st.error('Please fill out all fields before continuing.')
            st.stop()

        st.session_state.asset_information['name'] = asset_name
        st.session_state.asset_information['brand'] = asset_brand
        st.session_state.asset_information['product'] = asset_product

        st.session_state.progress.append('page_one_complete')
        st.experimental_rerun()


def page_two():
    st.image('images/Stage 2.png', use_column_width=True)

    st.markdown('## Marketing Brief')

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

    if (
        marketing_1
        and marketing_2
        and marketing_3
        and marketing_4
    ):
        if st.button('Continue to next step'):
            st.session_state.progress.append('page_two_complete')
            st.experimental_rerun()


def page_three():
    st.image('images/Stage 3.png', use_column_width=True)

    st.markdown('## Agency Creative Brief')

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

    if (
        agency_creative_1
        and agency_creative_2
        and agency_creative_3
        and agency_creative_4
        and agency_creative_5
    ):
        if st.button('Continue to next step'):
            st.session_state.progress.append('page_three_complete')
            st.experimental_rerun()


def page_four():
    st.image('images/Stage 4.png', use_column_width=True)

    st.markdown('## DE&I Discussion in the Creative Reviews')

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

    if (
        creative_review_1
        and creative_review_2
        and creative_review_3
        and creative_review_4
        and creative_review_5
    ):
        if st.button('Continue to next step'):
            st.session_state.progress.append('page_four_complete')
            st.experimental_rerun()


def page_five():
    st.image('images/Stage 5.png', use_column_width=True)

    st.markdown('## Upload Asset')

    st.write(
        'Use this portal to upload your content (advertisement, storyboard, working cut, '
        'final cut, etc.).'
    )

    text_area_color_css = ("""
        <style>
        .stTextArea > div > div {
            background-color: #C8C8C8;
        }
        </style>
    """)

    st.markdown(text_area_color_css, unsafe_allow_html=True)

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
    st.image('images/Stage 6.png', use_column_width=True)

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

    st.write("""
        In the meantime, please view the qualitative discussion guide on driving
        DEI into both the production and performance review below.

        **Production**:
        * What steps are we taking to be inclusive, representative and equitable in director and
            production partner search?
        * For every every triple bid, can we include one underrepresented maker in the mix?
        * Can we offer veterans on-set opportunities as PA's for US productions?
        * Can we commit to DOUBLE THE LINE, and agree to double 1 role to give an opportunity to an
            underrepresented maker?
        * How can we authentically embrace diverse casting and locations representative of our DE&I
            objectives?

        **Performance Review**:
        * How is our work being received by different DE&I communities?
        * How can we optimize our campaigns against these learnings?
        * How can we use The Representation Project's learnings to improve DE&I portfolio-wide?
    """)

    if st.button('Back to home page'):
        st.session_state.refresh_app = True
        st.session_state.clear_radio = True
        main()


def page_seven():
    st.markdown('## Explore Your Data')

    if not isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame):
        with st.spinner(text='Fetching the latest rep score data...'):
            data_explorer_df = read_google_spreadsheet(
                spread='https://docs.google.com/spreadsheets/d/1AxYTVCUs0PRfPcmMZRP3jYPwtmrHps-C9ndyS3SJTxM/',  # noqa: E501
                sheet=0,
            )

        data_explorer_df = data_explorer_df[data_explorer_df['Cat No. '].str.len() > 0]

        st.session_state.data_explorer_df = data_explorer_df

        st.session_state.data_explorer_df_no_duplicates = (
            data_explorer_df
            .sort_values(by=['Date Submitted'])
            .drop_duplicates(subset=['Ad Name', 'Brand', 'Product '], keep='last')
        )

    plot_color_maps(df=st.session_state.data_explorer_df_no_duplicates)


def main():
    if st.session_state.get('clear_radio'):
        del st.session_state.clear_radio

        st.session_state.sidebar_radio = 'Asset Overview'

    if st.session_state.get('refresh_app'):
        del st.session_state.refresh_app

        st.experimental_rerun()

    if st.session_state.get('sidebar_radio') == 'Submit an Asset':
        if 'page_five_complete' in st.session_state.progress:
            page_six()
        elif 'page_four_complete' in st.session_state.progress:
            page_five()
        elif 'page_three_complete' in st.session_state.progress:
            page_four()
        elif 'page_two_complete' in st.session_state.progress:
            page_three()
        elif 'page_one_complete' in st.session_state.progress:
            page_two()
        else:
            page_one()
    elif st.session_state.get('sidebar_radio') == 'Explore Your Data':
        page_seven()
    else:
        if 'page_five_complete' in st.session_state.progress:
            clear_session_state_asset_information()
            clear_session_state_progress()

        home_page()


def clear_session_state_progress():
    """TODO."""
    st.session_state.progress = list()


def clear_session_state_asset_information():
    """TODO."""
    st.session_state.asset_information = dict()


if authentication_status is False:
    st.error('Username and/or password is incorrect!')
    st.stop()
elif authentication_status is None:
    st.warning('Please enter your username and password.')
    st.stop()
else:
    font_css = (
        """
        <link href="//db.onlinewebfonts.com/c/542bb456af90c620bc50b375166d10b4?family=Lemon/Milk" rel="stylesheet" type="text/css"/>

        <style>
            @import url(//db.onlinewebfonts.com/c/542bb456af90c620bc50b375166d10b4?family=Lemon/Milk);
            @font-face {font-family: "LemonMilk"; src: url("//db.onlinewebfonts.com/t/542bb456af90c620bc50b375166d10b4.eot"); src: url("//db.onlinewebfonts.com/t/542bb456af90c620bc50b375166d10b4.eot?#iefix") format("embedded-opentype"), url("//db.onlinewebfonts.com/t/542bb456af90c620bc50b375166d10b4.woff2") format("woff2"), url("//db.onlinewebfonts.com/t/542bb456af90c620bc50b375166d10b4.woff") format("woff"), url("//db.onlinewebfonts.com/t/542bb456af90c620bc50b375166d10b4.ttf") format("truetype"), url("//db.onlinewebfonts.com/t/542bb456af90c620bc50b375166d10b4.png#Lemon/Milk") format("png"); }

            h1,h2,h3,h4,h5,h6 {
                font-family: 'LemonMilk';
            }
        </style>
        """  # noqa: E501
    )

    st.markdown(body=font_css, unsafe_allow_html=True,)

    s = ("""
        <style>
            div.stButton > button:first-child {
                background-color: #2A2526;
                color: #FAF4EB;
                font-size: 22px;
            }
        <style>
    """)

    st.markdown(s, unsafe_allow_html=True)

    st.image('images/Rep Score Portal Banner.png')

    if 'important' not in st.session_state:
        st.session_state.important = dict()

        st.session_state.important['username'] = username
        st.session_state.important['name'] = name
        st.session_state.important['run_id'] = 0

    if 'progress' not in st.session_state:
        clear_session_state_progress()

    if 'asset_information' not in st.session_state:
        clear_session_state_asset_information()

    with st.sidebar:
        st.markdown('')

        asset_overview_col_1, asset_overview_col_2 = st.columns([0.1, 300])
        explore_your_data_col_1, explore_your_data_col_2 = st.columns([0.1, 300])
        start_the_process_col_1, start_the_process_col_2 = st.columns([0.1, 300])

        with asset_overview_col_2:
            asset_overview_button = st.button('Asset Overview')
        with explore_your_data_col_2:
            explore_your_data_button = st.button('Explore Your Data')
        with start_the_process_col_2:
            start_the_process_button = st.button('Submit an Asset')

        if explore_your_data_button:
            st.session_state.sidebar_radio = 'Explore Your Data'
        elif start_the_process_button:
            st.session_state.sidebar_radio = 'Submit an Asset'
        elif asset_overview_button:
            st.session_state.sidebar_radio = 'Asset Overview'

        if st.session_state.get('sidebar_radio') == 'Explore Your Data':
            with explore_your_data_col_1:
                st.markdown('*')
        elif st.session_state.get('sidebar_radio') == 'Submit an Asset':
            with start_the_process_col_1:
                st.markdown('*')
        else:
            with asset_overview_col_1:
                st.markdown('*')

        st.markdown('<br>', unsafe_allow_html=True)

        if st.session_state.get('sidebar_radio') == 'Submit an Asset':
            # TODO: clean this up a bit
            if (
                'page_one_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p style="color:#fff;">1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief<p>
                    <p>3. DEI Checklist: Agency Creative Brief<p>
                    <p>4. DEI Checklist: Creative Reviews<p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)
                st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_one_complete' in st.session_state.progress
                and 'page_two_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p style="color:#fff;">2. DEI Checklist: Marketing Brief</p>
                    <p>3. DEI Checklist: Agency Creative Brief<p>
                    <p>4. DEI Checklist: Creative Reviews<p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)
                st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_two_complete' in st.session_state.progress
                and 'page_three_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p style="color:#fff;">3. DEI Checklist: Agency Creative Brief</p>
                    <p>4. DEI Checklist: Creative Reviews<p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)
                st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_three_complete' in st.session_state.progress
                and 'page_four_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p>3. DEI Checklist: Agency Creative Brief</p>
                    <p style="color:#fff;">4. DEI Checklist: Creative Reviews</p>
                    <p>5. Upload Asset<p>
                    <p>6. Summary<p>
                """)
                st.markdown(navigation_string, unsafe_allow_html=True)
            elif (
                'page_four_complete' in st.session_state.progress
                and 'page_five_complete' not in st.session_state.progress
            ):
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p>3. DEI Checklist: Agency Creative Brief</p>
                    <p>4. DEI Checklist: Creative Reviews</p>
                    <p style="color:#fff;">5. Upload Asset</p>
                    <p>6. Summary<p>
                """)
                st.markdown(navigation_string, unsafe_allow_html=True)
            else:
                navigation_string = ("""
                    <p>1. Start the Process</p>
                    <p>2. DEI Checklist: Marketing Brief</p>
                    <p>3. DEI Checklist: Agency Creative Brief</p>
                    <p>4. DEI Checklist: Creative Reviews</p>
                    <p>5. Upload Asset</p>
                    <p style="color:#fff;">6. Summary</p>
                """)
                st.markdown(navigation_string, unsafe_allow_html=True)
        else:
            navigation_string = ("""
                <p>1. Start the Process</p>
                <p>2. DEI Checklist: Marketing Brief<p>
                <p>3. DEI Checklist: Agency Creative Brief<p>
                <p>4. DEI Checklist: Creative Reviews<p>
                <p>5. Upload Asset<p>
                <p>6. Summary<p>
            """)
            st.markdown(navigation_string, unsafe_allow_html=True)

        if st.session_state.get('sidebar_radio') == 'Explore Your Data':
            st.markdown('<br>', unsafe_allow_html=True)

            st.session_state.sidebar_data_explorer_radio = st.radio(
                label='Select a visualization to view',
                options=('Score Heatmap', 'Rep Score Progress', 'Qualitative Notes'),
                index=0,
            )

        st.markdown('<br>', unsafe_allow_html=True)

        email_subject = 'Trouble with the Rep Score Portal'
        email_body = "Hi Rebecca,%0D%0A%0D%0AI'm having some trouble with...%0D%0A%0D%0AThanks!"

        contact_html = (f"""
            <a style="color: #003749;"
            href="mailto:rebecca@therepproject.org?subject={email_subject}&body={email_body}">
            Having issues?</a>
        """)

        st.markdown(contact_html, unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)

        col_1, col_2 = st.columns(2)

        with col_1:
            if st.session_state.get('sidebar_radio') == 'Submit an Asset':
                if st.button('Start over'):
                    clear_session_state_progress()
                    clear_session_state_asset_information()

                    st.session_state.refresh_app = True

                    main()
            else:
                if st.button('Refresh'):
                    st.session_state.refresh_app = True

                    if isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
                        del st.session_state.asset_tracker_df
                    if isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame):
                        del st.session_state.data_explorer_df

                    main()

        with col_2:
            authenticator.logout('Logout', 'main')

    progress_bar_css = ("""
        <style>
        .stProgress > div > div > div {
            background-color: gray;
        }
        .stProgress > div > div > div > div {
            background-color: green;
        }
        </style>
    """)

    st.markdown(progress_bar_css, unsafe_allow_html=True)

    text_area_color_css = ("""
        <style>
        .streamlit-expanderHeader {
            font-size: 16px;
            color: #EA3423;
            font-weight: bold;
        }
        </style>
    """)

    st.markdown(text_area_color_css, unsafe_allow_html=True)

    display_footer()

    main()

# TODO: write smart df caching system
