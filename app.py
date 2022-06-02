# import altair as alt
import gspread_pandas
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import streamlit as st


def aggrid_interactive_table(df: pd.DataFrame):
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


def upload_file_and_update_tracker(uploaded_file: st.uploaded_file_manager.UploadedFile):
    # set up Google API client
    sheet = gspread_pandas.spread.Spread(
        spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/edit',  # noqa: E501
        sheet=0,
        config=(
            gspread_pandas.conf.get_config(conf_dir='.', file_name='credentials.json')
        ),
    )

    asset_tracker_df = sheet.sheet_to_df(index=None)

    asset_tracker_df = asset_tracker_df.append(
        other=pd.Series({'Filename': uploaded_file.name, 'Status': 'Uploaded'}),
        ignore_index=True,
    )

    sheet.df_to_sheet(
        df=asset_tracker_df,
        index=False,
        sheet='Sheet1',
        replace=True,
    )

    # ``uploaded_file`` is of type ``io.BytesIO``, basically
    st.write(f'Uploaded filename: {uploaded_file.name} ({uploaded_file.type})')

    # bytes_data = uploaded_file.read()


# st.markdown("""
#     <style>
#       .font {
#         font-size: 50px;
#         font-family: 'Cooper Black';
#         color: #FF9633;
#       }
#     </style>
# """, unsafe_allow_html=True)
#
# st.markdown('<p class="font">Test!</p>', unsafe_allow_html=True)

# hide_streamlit_style = """
#     <style>
#         #MainMenu {visibility: hidden;}
#         footer {visibility: hidden;}
#     </style>
# """
#
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)


st.markdown('# Rep Score UI Prototype')

with st.sidebar:
    st.image('https://therepproject.org/wp-content/uploads/2020/05/Asset-1@3x.png')

    sidebar_radio = st.radio(
        label='Choose a page to view',
        options=('Asset Import', 'Asset Tracker', 'Data Explorer'),
    )

# tracker - make that default
# uploaded, sent, recieved, notes
# contact form - "Having issues?" -> send email to Becca

if sidebar_radio == 'Asset Import':
    st.markdown('## Asset Import')

    uploaded_file = st.file_uploader(
        label='Select a file to upload',
        type=None,
        accept_multiple_files=False,
    )

    if uploaded_file:
        st.write('Please check the following before uploading:')

        option_1 = st.checkbox('initial velocity (u)')
        option_2 = st.checkbox('final velocity (v)')
        option_3 = st.checkbox('acceleration (a)')
        option_4 = st.checkbox('time (t)')

        if (
            option_1
            and option_2
            and option_3
            and option_4
        ):
            if st.button('Upload!'):
                with st.spinner(text='Uploading file...'):
                    upload_file_and_update_tracker(uploaded_file=uploaded_file)

elif sidebar_radio == 'Asset Tracker':
    st.markdown('## Asset Tracker')

    # set up Google API client
    sheet = gspread_pandas.spread.Spread(
        spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/edit',  # noqa: E501
        sheet=0,
        config=gspread_pandas.conf.get_config(conf_dir='.', file_name='credentials.json'),
    )

    asset_tracker_df = sheet.sheet_to_df(index=None)

    selection = aggrid_interactive_table(df=asset_tracker_df)

elif sidebar_radio == 'Data Explorer':
    st.markdown('## Data Explorer')

    if not isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame):
        # set up Google API client
        sheet = gspread_pandas.spread.Spread(
            spread='https://docs.google.com/spreadsheets/d/10jMmQpYYNbNhPYteRXDd76y8KuhWal1tqfVFJ2pqrSY/edit',  # noqa: E501
            sheet=0,
            config=gspread_pandas.conf.get_config(conf_dir='.', file_name='credentials.json'),
        )

        data_explorer_df = sheet.sheet_to_df(index=None)

        data_explorer_df = data_explorer_df[data_explorer_df['Cat No. '].str.len() > 0]

        st.session_state.data_explorer_df = data_explorer_df

    selection = aggrid_interactive_table(df=st.session_state.asset_tracker_df)

    if selection and selection['selected_rows']:
        st.write('Row selected:')
        st.json(selection['selected_rows'])


# elif sidebar_radio == 'Data Visualization':
#     st.markdown('## Data Visualization')

#     # TODO: replace this with real data
#     data_explorer_df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

#     st.markdown('### Scatterplot')

#     chart = (
#         alt.Chart(
#             data_explorer_df,
#             title='Iris Dataset Sepal Size Comparison',
#         )
#         .mark_circle()
#         .encode(
#             x=alt.X('sepal_length', title='Sepal Length'),
#             y=alt.Y('sepal_width', title='Sepal Width'),
#             color=alt.Color(
#                 'species',
#                 legend=alt.Legend(title="Species"),
#                 scale=alt.Scale(scheme='category10'),
#             ),
#             tooltip=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
#         )
#     )

#     st.altair_chart(chart, use_container_width=True)

#     st.markdown('### Bar Graph')

#     row_1, _ = st.columns((2.5, 5))

#     with row_1:
#         field_selected = st.selectbox(
#             label='Choose a field to compare against',
#             options=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
#         )

#     st.text('')

#     chart = (
#         alt.Chart(
#             data_explorer_df,
#             title='Iris Dataset Species Size Comparison',
#         )
#         .mark_bar()
#         .encode(
#             x=alt.X('species', title='Species'),
#             y=alt.Y(field_selected, title=field_selected),
#             color=alt.Color(
#                 'species',
#                 legend=alt.Legend(title="Species"),
#                 scale=alt.Scale(scheme='category10'),
#             ),
#             tooltip=[field_selected],
#         )
#     )

#     st.altair_chart(chart, use_container_width=True)

#     st.markdown('### Interactive Data Exploration')

#     selection = aggrid_interactive_table(data_explorer_df=data_explorer_df)

#     if selection and selection['selected_rows']:
#         st.write('Row selected:')
#         st.json(selection['selected_rows'])
