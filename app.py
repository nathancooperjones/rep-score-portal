from datetime import datetime
import json

import altair as alt
import boto3
import gspread_pandas
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth


hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

authenticator = stauth.Authenticate(names=['Test User'],
                                    usernames=['user'],
                                    passwords=stauth.Hasher(['test']).generate(),
                                    cookie_name='trp_rep_score_cookie',
                                    key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9-wiaWF0IjoxNTE2MjM5DI',
                                    cookie_expiry_days=7)

with st.sidebar:
    st.image('https://therepproject.org/wp-content/uploads/2020/05/Asset-1@3x.png')

name, authentication_status, username = authenticator.login('Login', 'main')


def upload_file_and_update_tracker(uploaded_file: st.uploaded_file_manager.UploadedFile) -> None:
    """TODO."""
    with open('aws_credentials.json', 'r') as fp:
        aws_credentials_dict = json.load(fp)

    (
        boto3
        .client(
            's3',
            aws_access_key_id=aws_credentials_dict['aws_access_key_id'],
            aws_secret_access_key=aws_credentials_dict['aws_secret_access_key'],
        )
        .upload_fileobj(uploaded_file, 'trp-rep-score-assets', f'uploads/{uploaded_file.name}')
    )

    # set up Google API client
    sheet = gspread_pandas.spread.Spread(
        spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/edit',  # noqa: E501
        sheet=0,
        config=(
            gspread_pandas.conf.get_config(conf_dir='.', file_name='credentials.json')
        ),
    )

    asset_tracker_df = sheet.sheet_to_df(index=None)

    # uploaded, sent, recieved, notes
    asset_tracker_df = asset_tracker_df.append(
        other=pd.Series({
            'Filename': uploaded_file.name,
            'Date Submitted': datetime.today().strftime('%m/%d/%Y'),
            'Status': 'Uploaded',
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

    st.write(f"""
        Your asset `{uploaded_file.name}` has been uploaded and we'll begin work on it soon. It
        should now show up in the "Track Your Asset" page.

        In the meantime, please view the qualitative discussion guide on driving
        DEI into both the production and performance review below.

        **Production**:
        * What steps are we taking to be inclusive, representative and equitable
            in director and production partner search?
        * For every every triple bid, can we include one underrepresented maker
            in the mix?
        * Can we offer veterans on-set opportunities as PA's for US productions?
        * Can we commit to DOUBLE THE LINE, and agree to double 1 role to give
            an opportunity to an underrepresented maker?
        * How can we authentically embrace diverse casting and locations
            representative of our DE&I objectives?

        **Performance Review**:
        * How is our work being received by different DE&I communities?
        * How can we optimize our campaigns against these learnings?
        * How can we use the Geena Davis Institute learnings to improve DE&I
            portfolio-wide?
    """)

    # ``uploaded_file`` is of type ``io.BytesIO``, basically
    # bytes_data = uploaded_file.read()


def read_google_spreadsheet(spread: str, sheet: int = 0) -> pd.DataFrame:
    """TODO."""
    # set up Google API client
    sheet = gspread_pandas.spread.Spread(
        spread=spread,
        sheet=sheet,
        config=gspread_pandas.conf.get_config(conf_dir='.', file_name='credentials.json'),
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
        .set_index(['Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted', 'Qual Notes'])
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
        '#81c675' if float(x) >= 80
        else '#fbf28d' if 60 <= float(x) < 80
        else '#f2766e'
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
            alt.Y(shorthand='Ad Name', axis=alt.Axis(tickSize=0, labelPadding=10, titlePadding=20)),
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

        st.write('-----')

    if st.checkbox('Show rep score progress'):
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

    if st.checkbox('Show qualitative notes'):
        notes_df = df_to_plot.copy()

        notes_df = notes_df.drop_duplicates(
            subset=['Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted', 'Qual Notes']
        )

        for _, row in notes_df.iterrows():
            with st.expander(f'"{row["Ad Name"]}" Notes', expanded=False):
                notes = 'No notes! 🎉'

                if row['Qual Notes']:
                    notes = row['Qual Notes']

                st.write(notes)


if authentication_status is False:
    st.error('Username and/or password is incorrect!')
    st.stop()
elif authentication_status is None:
    st.warning('Please enter your username and password.')
    st.stop()
else:
    st.markdown('# Rep Score Prototype')

    with st.sidebar:
        sidebar_radio = st.radio(
            label='Select a page to view',
            options=('Start the Process', 'Track Your Asset', 'Explore Your Data'),
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

        authenticator.logout('Logout', 'main')

    if sidebar_radio == 'Start the Process':
        st.markdown('## Start the Process')

        st.write(
            'Use this portal to upload your content (advertisement, storyboard, working cut, '
            'final cut, etc.).'
        )

        uploaded_file = st.file_uploader(
            label='Select a file to upload',
            type=None,
            accept_multiple_files=False,
        )

        if uploaded_file:
            st.write(
                'Before submitting, ensure that you have completed the Creative Compass '
                'Pre-Production DEI checklist.'
            )

            prefix = '✅ '

            should_we_expand_marketing = bool(
                not st.session_state.get('marketing_1')
                or not st.session_state.get('marketing_2')
                or not st.session_state.get('marketing_3')
                or not st.session_state.get('marketing_4')
            )

            with st.expander(
                (
                    f'{prefix if not should_we_expand_marketing else ""}'
                    'Marketing Brief'
                ),
                expanded=True,
            ):
                st.session_state.marketing_1 = st.checkbox(
                    'DE&I can be reflected in our High Value Communities or audience definitions'
                )
                st.session_state.marketing_2 = st.checkbox(
                    'All additional growth audience(s) are considered, or prioritized'
                )
                st.session_state.marketing_3 = st.checkbox(
                    'We have the opportunity to personalize our work to different DE&I communities'
                )
                st.session_state.marketing_4 = st.checkbox(
                    'This project (or business opportunity) intersects with social issues'
                )

            should_we_expand_marketing = bool(
                not st.session_state.get('marketing_1')
                or not st.session_state.get('marketing_2')
                or not st.session_state.get('marketing_3')
                or not st.session_state.get('marketing_4')
            )

            should_we_expand_agency = bool(
                not st.session_state.get('agency_creative_1')
                or not st.session_state.get('agency_creative_2')
                or not st.session_state.get('agency_creative_3')
                or not st.session_state.get('agency_creative_4')
                or not st.session_state.get('agency_creative_5')
            )

            with st.expander(
                (
                    f'{prefix if not should_we_expand_agency else ""}'
                    'Agency Creative Brief'
                ),
                expanded=not should_we_expand_marketing,
            ):
                st.session_state.agency_creative_1 = st.checkbox(
                    'We have considered where we are sourcing data and inspiration for this project'
                )
                st.session_state.agency_creative_2 = st.checkbox(
                    'We are getting a full picture of the audience, getting a more diverse '
                    'perspective'
                )
                st.session_state.agency_creative_3 = st.checkbox(
                    'We dispel any relevant stereotypes about the audience'
                )
                st.session_state.agency_creative_4 = st.checkbox(
                    'We are gaining input or inspiration from the audience'
                )
                st.session_state.agency_creative_5 = st.checkbox(
                    'Our creative references and thought starters are as diverse, equal, and '
                    'inclusive as the work we hope to make'
                )

            should_we_expand_agency = bool(
                not st.session_state.get('agency_creative_1')
                or not st.session_state.get('agency_creative_2')
                or not st.session_state.get('agency_creative_3')
                or not st.session_state.get('agency_creative_4')
                or not st.session_state.get('agency_creative_5')
            )

            should_we_expand_creative = bool(
                not st.session_state.get('creative_review_1')
                or not st.session_state.get('creative_review_2')
                or not st.session_state.get('creative_review_3')
                or not st.session_state.get('creative_review_4')
                # or not st.session_state.get('creative_review_5')
            )

            with st.expander(
                (
                    f'{prefix if not should_we_expand_creative else ""}'
                    'Commit to DE&I Discussion in the Creative Reviews'
                ),
                expanded=not should_we_expand_marketing and not should_we_expand_agency,
            ):
                st.session_state.creative_review_1 = st.checkbox(
                    'We can reasonably make the work more inclusive, equitable, and representative '
                    'at this stage'
                )
                st.session_state.creative_review_2 = st.checkbox(
                    'The work is not reinforcing negative stereotypes'
                )
                st.session_state.creative_review_3 = st.checkbox(
                    'There are no cultural references we are misappropriating'
                )
                st.session_state.creative_review_4 = st.checkbox(
                    'We are inclusive with regard to age, body type, disability, ethnicity, '
                    'gender, and sexual orientation'
                )
                st.session_state.creative_review_5 = st.checkbox(
                    'We, and our clients, made choices that lead to more inclusive and equitable '
                    'work'
                )

            if (
                st.session_state.marketing_1
                and st.session_state.marketing_2
                and st.session_state.marketing_3
                and st.session_state.marketing_4
                and st.session_state.agency_creative_1
                and st.session_state.agency_creative_2
                and st.session_state.agency_creative_3
                and st.session_state.agency_creative_4
                and st.session_state.agency_creative_5
                and st.session_state.creative_review_1
                and st.session_state.creative_review_2
                and st.session_state.creative_review_3
                and st.session_state.creative_review_4
                and st.session_state.creative_review_5
            ):
                if st.button('Upload!'):
                    with st.spinner(text='Uploading file...'):
                        upload_file_and_update_tracker(uploaded_file=uploaded_file)

    elif sidebar_radio == 'Track Your Asset':
        st.markdown('## Track Your Asset')

        asset_tracker_df = read_google_spreadsheet(
            spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/edit',  # noqa: E501
            sheet=0,
        )

        # CSS to inject contained in a string
        hide_table_row_index = ("""
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
        """)

        # inject CSS with Markdown to hide the table index
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        def color_survived(x: str) -> str:
            if x == 'Uploaded':
                color = 'black'
                background_color = '#9EC2FF'
            elif x == 'In progress':
                color = 'white'
                background_color = '#4259C3'
            elif x == 'Complete':
                color = 'white'
                background_color = '#03018C'

            return f'color: {color}; background-color: {background_color}'

        st.table(data=asset_tracker_df.style.applymap(color_survived, subset=['Status']))

    elif sidebar_radio == 'Explore Your Data':
        st.markdown('## Explore Your Data')

        if not isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame):
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

        # TODOs:
        # clear session state data on reload and upload
        # write smart df caching system
        # add date submitted to asset tracking table

        plot_color_maps(df=st.session_state.data_explorer_df_no_duplicates)
