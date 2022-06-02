import json

import altair as alt
import boto3
import gspread_pandas
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
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


def aggrid_interactive_table(df: pd.DataFrame) -> AgGrid:
    """
    Creates an ``st-aggrid`` interactive table based on the input DataFrame.

    Parameters
    ----------
    df: pd.DataFrame

    Returns
    -------
    selection: st_aggrid.AgGrid

    """
    options = GridOptionsBuilder.from_dataframe(
        dataframe=df, enableRowGroup=True, enableValue=True, enablePivot=True,
    )

    options.configure_side_bar()

    options.configure_selection('single')

    selection = AgGrid(
        dataframe=df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection


def upload_file_and_update_tracker(uploaded_file: st.uploaded_file_manager.UploadedFile) -> None:
    """TODO."""
    with open('aws_credentials.json', 'r') as fp:
        aws_credentials_dict = json.load(fp)

    print(f'uploads/{uploaded_file.name}')

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
        other=pd.Series({'Filename': uploaded_file.name, 'Status': 'Uploaded'}),
        ignore_index=True,
    )

    # TODO: figure out how to do this without replacement
    sheet.df_to_sheet(
        df=asset_tracker_df,
        index=False,
        sheet='Sheet1',
        replace=True,
    )

    # ``uploaded_file`` is of type ``io.BytesIO``, basically
    st.write(f'Uploaded filename: {uploaded_file.name} ({uploaded_file.type})')

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


def plot_color_map(df: pd.DataFrame) -> alt.vegalite.v4.api.Chart:
    """TODO."""
    df = df.rename(columns={
        'Product ': 'Product',
        'TOTAL (GENDER)': 'GENDER',
        'TOTAL (RACE)': 'RACE',
        'TOTAL (LGBTQ)': 'LGBTQ+',
        'TOTAL (Disability)': 'DISABILITY',
        'TOTAL (50+)': 'AGE',
        'TOTAL (Fat)': 'BODY SIZE',
    })

    cols_to_select_subset = [
        'Ad Name',
        'Brand',
        'Product',
        'GENDER',
        'RACE',
        'LGBTQ+',
        'DISABILITY',
        'AGE',
        'BODY SIZE',
    ]

    df_to_plot = (
        df[cols_to_select_subset]
        .set_index(['Ad Name', 'Brand', 'Product'])
        .stack()
        .reset_index()
        .rename(columns={0: 'Score', 'level_3': 'Variable'})
    )

    filter_by = st.selectbox(
        label='Filter visualization by...',
        options=['None', 'Ad Name', 'Brand', 'Product'],
    )

    field_selected = None

    if filter_by != 'None':
        field_selected = st.multiselect(
            label='Choose a field to compare against',
            options=sorted(df_to_plot[filter_by].unique()),
            default=sorted(df_to_plot[filter_by].unique()),
        )

    st.write('')

    if filter_by != 'None' and field_selected:
        df_to_plot = df_to_plot[df_to_plot[filter_by].isin(field_selected)]

    df_to_plot['color'] = [
        '#81c675' if float(x) >= 80
        else '#fbf28d' if 60 <= float(x) < 80
        else '#f2766e'
        for x in df_to_plot['Score']
    ]

    sort = [
        'GENDER',
        'RACE',
        'LGBTQ+',
        'DISABILITY',
        'AGE',
        'BODY SIZE',
    ]

    return (
        alt
        .Chart(df_to_plot)
        .mark_rect(size=100, stroke='black', strokeWidth=0.5)
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
            alt.Y(shorthand='Ad Name', axis=alt.Axis(tickSize=0, labelPadding=10, titlePadding=20)),
            color=alt.Color('color', scale=None),
            tooltip=['Ad Name', 'Brand', 'Product', 'Variable', 'Score'],
        ).properties(
            height=300,
        ).configure_axis(
            labelFontSize=15,
            labelFontWeight=alt.FontWeight('bold'),
            titleFontSize=15,
            titleFontWeight=alt.FontWeight('normal'),
        )
    )


def plot_color_map_overall(df: pd.DataFrame) -> alt.vegalite.v4.api.Chart:
    """TODO."""
    df = df.rename(columns={
        'Product ': 'Product',
    })

    cols_to_select_subset = [
        'Ad Name',
        'Brand',
        'Product',
        'Ad Total Score',
    ]

    df_to_plot = (
        df[cols_to_select_subset]
        .set_index(['Ad Name', 'Brand', 'Product'])
        .stack()
        .reset_index()
        .rename(columns={0: 'Score', 'level_3': 'Ad Total Score'})
    )

    df_to_plot['color'] = [
        '#81c675' if float(x) >= 80
        else '#fbf28d' if 60 <= float(x) < 80
        else '#f2766e'
        for x in df_to_plot['Score']
    ]

    return (
        alt
        .Chart(df_to_plot)
        .mark_rect(size=100, stroke='black', strokeWidth=0.5)
        .encode(
            alt.X(
                shorthand='Ad Total Score',
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
        ).configure_axis(
            labelFontSize=15,
            labelFontWeight=alt.FontWeight('bold'),
            titleFontSize=15,
            titleFontWeight=alt.FontWeight('normal'),
        )
    )


if authentication_status is False:
    st.error('Username and/or password is incorrect!')
    st.stop()
elif authentication_status is None:
    st.warning('Please enter your username and password.')
    st.stop()
else:
    st.markdown('# Rep Score UI Prototype')

    with st.sidebar:
        sidebar_radio = st.radio(
            label='Choose a page to view',
            options=('Import Your Asset', 'Track Your Asset', 'Explore Your Data'),
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

    if sidebar_radio == 'Track Your Asset':
        st.markdown('## Asset Tracker')

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

        # inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        # gradient light blue to dark blue
        # uploaded, in progress, complete

        st.table(data=asset_tracker_df)

    elif sidebar_radio == 'Import Your Asset':
        st.markdown('## Asset Import')

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
                    'Infuse DE&I provocations into the Marketing Brief'
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
                    'Infuse DE&I provocations into the Agency Creative Brief'
                ),
                expanded=not should_we_expand_marketing,
            ):
                st.session_state.agency_creative_1 = st.checkbox(
                    'We have considered where we are sourcing data and inspiration for this project'
                )
                st.session_state.agency_creative_2 = st.checkbox(
                    'We are getting a full picture of the audience - we get a more diverse '
                    'perspective'
                )
                st.session_state.agency_creative_3 = st.checkbox(
                    'There are relevant stereotypes about the audience that we should dispel'
                )
                st.session_state.agency_creative_4 = st.checkbox(
                    'We are gaining input or inspiration from the audience'
                )
                st.session_state.agency_creative_5 = st.checkbox(
                    'Our creative references and thought starters are as diverse, equal and '
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
                    'We can reasonably make the work more inclusive, equitable and representative '
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
                    'gender, sexual orientation'
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

                        st.write("""
                            Your asset has been uploaded and we'll begin work on it soon. It should
                            not show up in the tracker table in the "Track Your Asset" page.

                            In the meantime, please view the qualitative discussion guide on driving
                            DEI in the production and into the performance review.

                            **Production**:
                            * What steps are we taking to be inclusive, representative and equitable
                              in director and production partner search?
                            * For every every triple bid, can we include one underrepresented maker
                              in the mix?
                            * Can we offer veterans on-set opportunities as PA’s for US productions?
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

    elif sidebar_radio == 'Explore Your Data':
        st.markdown('## Data Explorer')

        if not isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame):
            data_explorer_df = read_google_spreadsheet(
                spread='https://docs.google.com/spreadsheets/d/1AxYTVCUs0PRfPcmMZRP3jYPwtmrHps-C9ndyS3SJTxM/',  # noqa: E501
                sheet=0,
            )

            data_explorer_df = data_explorer_df[data_explorer_df['Cat No. '].str.len() > 0]

            cols_to_select = [
                'Ad Name',
                'Brand',
                'Product ',
                'TOTAL (GENDER)',
                'TOTAL (RACE)',
                'TOTAL (LGBTQ)',
                'TOTAL (Disability)',
                'TOTAL (50+)',
                'TOTAL (Fat)',
                'Presence Sum',
                'Prominence Total',
                'Stereotypes Total',
                'Ad Total Score',
            ]

            data_explorer_df = data_explorer_df[cols_to_select]

            st.session_state.data_explorer_df = data_explorer_df

        st.caption('Select a row below for more details')

        # selection = aggrid_interactive_table(df=st.session_state.data_explorer_df)

        # if selection and selection['selected_rows']:
        #     st.write('Row selected:')
        #     st.json(selection['selected_rows'])

        # TODOs:
        # add number to squares, maybe make it an option
        # make the filtering options for the visualization global to affect both
        # add line chart to plot score over time / drafts

        st.altair_chart(
            plot_color_map_overall(df=st.session_state.data_explorer_df),
            use_container_width=True,
        )

        st.write('-----')

        if st.checkbox('Break down by identity'):
            st.altair_chart(
                plot_color_map(df=st.session_state.data_explorer_df),
                use_container_width=True,
            )
