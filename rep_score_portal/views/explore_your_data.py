from typing import Iterable

import altair as alt
import pandas as pd
import streamlit as st

from input_output import read_google_spreadsheet


def page_seven() -> None:
    """Display the "Explore Your Data" page."""
    st.markdown('## Explore Your Data')

    if (
        not isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame)
        or not isinstance(st.session_state.get('data_explorer_df_no_duplicates'), pd.DataFrame)
        or not isinstance(st.session_state.get('color_map_df'), pd.DataFrame)
    ):
        with st.spinner(text='Fetching the latest rep score data...'):
            data_explorer_df = (
                read_google_spreadsheet(
                    spread='https://docs.google.com/spreadsheets/d/1AxYTVCUs0PRfPcmMZRP3jYPwtmrHps-C9ndyS3SJTxM/',  # noqa: E501
                    sheet=0,
                )
                .sheet_to_df(index=None)
            )

        data_explorer_df = data_explorer_df[data_explorer_df['Cat No. '].str.len() > 0]

        if len(data_explorer_df) == 0:
            st.write("We couldn't find any existing assets to view yet - sorry!")
            return

        data_explorer_df = data_explorer_df.rename(columns={
            'Product ': 'Product',
            'TOTAL (GENDER)': 'GENDER',
            'TOTAL (RACE)': 'RACE',
            'TOTAL (LGBTQ)': 'LGBTQ+ ',  # the space is intentional, sadly
            'TOTAL (Disability)': 'DISABILITY',
            'TOTAL (50+)': 'AGE',
            'TOTAL (Fat)': 'BODY SIZE',
        })

        data_explorer_df_no_duplicates = (
            data_explorer_df
            .sort_values(by=['Date Submitted'])
            .drop_duplicates(subset=['Ad Name', 'Brand', 'Product'], keep='last')
        )

        color_map_df = (
            data_explorer_df_no_duplicates[[
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
            ]]
            .set_index(
                ['Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted', 'Qual Notes']
            )
            .stack()
            .reset_index()
            .rename(columns={0: 'Score', 'level_6': 'Variable'})
        )

        color_map_df['Date Submitted'] = pd.to_datetime(color_map_df['Date Submitted']).dt.date

        color_map_df['color'] = [
            '#7ED957' if float(x) >= 80
            else '#FFDE59' if 60 <= float(x) < 80
            else '#EA3423'
            for x in color_map_df['Score']
        ]

        st.session_state.data_explorer_df = data_explorer_df
        st.session_state.data_explorer_df_no_duplicates = data_explorer_df_no_duplicates
        st.session_state.color_map_df = color_map_df

    if st.session_state.sidebar_data_explorer_radio == 'Score Heatmap':
        plot_color_maps()
    elif st.session_state.sidebar_data_explorer_radio == 'Rep Score Progress':
        plot_rep_score_progress()
    elif st.session_state.sidebar_data_explorer_radio == 'Qualitative Notes':
        display_qualitative_notes()


def plot_color_maps() -> None:
    """Plot rep score color maps."""
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
                    value=st.session_state.color_map_df['Date Submitted'].min(),
                )

            with col_2:
                max_date = st.date_input(label='Latest submitted date to consider')
        else:
            field_selected = st.multiselect(
                label='Choose a field to compare against',
                options=sorted(st.session_state.color_map_df[filter_by].unique()),
                default=sorted(st.session_state.color_map_df[filter_by].unique()),
            )

    st.markdown('<br>', unsafe_allow_html=True)

    if (
        filter_by != 'None'
        and (field_selected is not None or min_date is not None or max_date is not None)
    ):
        if filter_by == 'Date Submitted':
            df_to_plot = st.session_state.color_map_df[
                (st.session_state.color_map_df['Date Submitted'] >= min_date)
                & (st.session_state.color_map_df['Date Submitted'] <= max_date)
            ]
        else:
            df_to_plot = st.session_state.color_map_df[
                st.session_state.color_map_df[filter_by].isin(field_selected)
            ]
    else:
        df_to_plot = st.session_state.color_map_df.copy()

    if len(df_to_plot) == 0:
        st.error(
            "Hmm... we couldn't find any existing assets with those filters applied. "
            'Please try again with a different set of filters applied.'
        )
        st.stop()

    overall_df_to_plot = df_to_plot[df_to_plot['Variable'] == 'Ad Total Score']

    _construct_plot(
        df_to_plot=overall_df_to_plot,
        x_sort=None,
        include_variable_in_tooltip=False,
    )

    st.caption(
        '\\* Note that when multiple versions of an asset have been submitted, only the '
        'most-recent version will be displayed above. To see multiple versions plotted over time, '
        'click "Rep Score Progress" on the left sidebar.'
    )

    st.write('-----')

    if st.checkbox('Break down by identity'):
        subset_df_to_plot = df_to_plot[df_to_plot['Variable'] != 'Ad Total Score']

        x_sort = [
            'GENDER',
            'RACE',
            'LGBTQ+ ',
            'DISABILITY',
            'BODY SIZE',
            'AGE',
        ]

        _construct_plot(
            df_to_plot=subset_df_to_plot,
            x_sort=x_sort,
            include_variable_in_tooltip=True,
        )


def _construct_plot(
    df_to_plot: pd.DataFrame,
    x_sort: Iterable[str] = None,
    include_variable_in_tooltip: bool = False,
) -> None:
    """
    Construct the color map plot.

    Parameters
    ----------
    df_to_plot: pd.DataFrame
        Pandas DataFrame to plot with columns ``Variable``, ``Ad Name``, ``Brand``, ``Product``, and
        ``Score``
    x_sort: list
        Desired sort of the x-axis, if any
    include_variable_in_tooltip: bool
        Whether or not to include the variable ``Variable`` in the plot tooltip

    """
    base = (
        alt
        .Chart(df_to_plot)
        .encode(
            x=alt.X(
                shorthand='Variable',
                sort=x_sort,
                axis=alt.Axis(
                    orient='top',
                    labelAngle=-45,
                    tickSize=0,
                    labelPadding=10,
                    title=None,
                )
            ),
            y=alt.Y(
                shorthand='Ad Name',
                axis=alt.Axis(tickSize=0, labelPadding=10, titlePadding=20)
            ),
        )
    )

    tooltip = ['Ad Name', 'Brand', 'Product', 'Score']

    if include_variable_in_tooltip:
        tooltip.insert(-1, 'Variable')

    chart = (
        base
        .mark_rect(size=100, stroke='black', strokeWidth=0.5)
        .encode(
            color=alt.Color('color', scale=None),
            tooltip=tooltip,
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


def plot_rep_score_progress() -> None:
    """Plot rep score progress over content type or date submitted."""
    x_axis = st.selectbox(
        label='Select field to view by',
        options=['Content Type', 'Date Submitted'],
    )

    if x_axis == 'Date Submitted':
        x_axis = 'Date Submitted Month Year'

    st.markdown('<br>', unsafe_allow_html=True)

    progress_df = st.session_state.data_explorer_df[
        st.session_state.data_explorer_df[['Ad Name', 'Brand', 'Product']]
        .duplicated(keep=False)
    ]

    progress_df = progress_df[[
        'Content Type',
        'Ad Total Score',
        'Ad Name',
        'Brand',
        'Product',
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
            tooltip=['Ad Name', 'Brand', 'Product', 'Date Submitted', 'Ad Total Score'],
        ).properties(
            height=500,
        ).configure_point(
            size=100,
        )
    )

    st.altair_chart(progress_chart, use_container_width=True)


def display_qualitative_notes() -> None:
    """Display qualitative notes per unique asset."""
    notes_df = st.session_state.data_explorer_df_no_duplicates.copy()

    notes_df = notes_df.drop_duplicates(
        subset=['Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted', 'Qual Notes']
    )

    for _, row in notes_df.iterrows():
        with st.expander(f'"{row["Ad Name"]}" Notes', expanded=False):
            notes = 'No notes! 🎉'

            if row['Qual Notes']:
                notes = row['Qual Notes']

            st.write(notes)

    st.caption(
        '\\* Note that when multiple versions of an asset have been submitted, only the '
        'most-recent version will be displayed above.'
    )
