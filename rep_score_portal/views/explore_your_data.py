from typing import Iterable, Optional, Union

import altair as alt
import pandas as pd
import streamlit as st

from input_output import read_google_spreadsheet
from utils import (
    check_for_assigned_assets,
    edit_colors_of_selectbox,
    get_content_types,
    insert_line_break,
)


def page_seven() -> None:
    """Display the "Explore Your Data" page."""
    st.markdown('## Explore Your Data')

    if (
        not isinstance(st.session_state.get('data_explorer_df'), pd.DataFrame)
        or not isinstance(st.session_state.get('data_explorer_df_no_duplicates'), pd.DataFrame)
        or not isinstance(st.session_state.get('color_map_df'), pd.DataFrame)
    ):
        check_for_assigned_assets()

        if (
            isinstance(st.session_state.get('assigned_user_assets'), list)
            and len(st.session_state.assigned_user_assets) > 0
        ):
            with st.spinner(text='Fetching the latest rep score data...'):
                data_explorer_df = (
                    read_google_spreadsheet(
                        spread=st.secrets['spreadsheets']['primary_dataset_url'],
                        sheet=0,
                    )
                    .sheet_to_df(index=None)
                )

                if st.session_state['username'] not in st.secrets['login_groups']['admins']:
                    data_explorer_df = data_explorer_df[
                        data_explorer_df['Ad Name'].isin(st.session_state.assigned_user_assets)
                    ]

            data_explorer_df = data_explorer_df[data_explorer_df['Cat No. '].str.len() > 0]
        else:
            data_explorer_df = None

        if (
            not isinstance(data_explorer_df, pd.DataFrame)
            or len(data_explorer_df) == 0
        ):
            st.error("We couldn't find any assigned and completed assets you can view yet - sorry!")
            st.stop()

        data_explorer_df = data_explorer_df.rename(columns={
            'Product ': 'Product',
            'TOTAL (GENDER)': 'GENDER',
            'TOTAL (RACE)': 'RACE',
            'TOTAL (LGBTQ)': 'LGBTQ+ ',  # the space is intentional, sadly
            'TOTAL (Disability)': 'DISABILITY',
            'TOTAL (50+)': 'AGE',
            'TOTAL (Fat)': 'BODY SIZE',
        })

        data_explorer_df = data_explorer_df.replace('#N/A', '').replace('N/A', '')

        # hacky, I know, but easier to work with down the line when it comes to filtering input
        data_explorer_df['BASELINE'] = data_explorer_df['Baseline'].copy()

        data_explorer_df['Date Submitted'] = pd.to_datetime(data_explorer_df['Date Submitted'])

        data_explorer_df_no_duplicates = (
            data_explorer_df
            .sort_values(by=['Date Submitted'])
            .drop_duplicates(subset=['Ad Name', 'Brand', 'Product'], keep='last')
        )

        color_map_df_index = [
            'Ad Name',
            'Brand',
            'Product',
            'Content Type',
            'Baseline',
            'Date Submitted',
            'Qual Notes',
        ]

        color_map_df = (
            data_explorer_df_no_duplicates[[
                'Ad Name',
                'Brand',
                'Product',
                'Content Type',
                'Baseline',
                'BASELINE',
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
            .set_index(color_map_df_index)
            .stack()
            .reset_index()
            .rename(columns={0: 'Score', f'level_{len(color_map_df_index)}': 'Variable'})
        )

        color_map_df['Date Submitted'] = pd.to_datetime(color_map_df['Date Submitted']).dt.date

        color_map_df['color'] = _create_color_column(scores=color_map_df['Score'])

        st.session_state.data_explorer_df = data_explorer_df
        st.session_state.data_explorer_df_no_duplicates = data_explorer_df_no_duplicates
        st.session_state.color_map_df = color_map_df

    edit_colors_of_selectbox()

    tab_1, tab_2, tab_3 = st.tabs(['Score Heatmap', 'Qualitative Notes', 'Rep Score Progress'])

    with tab_1:
        plot_color_maps()
    with tab_2:
        display_qualitative_notes()
    with tab_3:
        plot_rep_score_progress()

    if not st.session_state.get('hacky_experimental_rerun_for_explore_data_first_page_load'):
        st.session_state.hacky_experimental_rerun_for_explore_data_first_page_load = True
        st.experimental_rerun()


def _create_color_column(scores: Iterable[Union[str, float]]) -> Iterable[str]:
    """Assign cell color values to scores."""
    return [
        '#8F9193' if str(x) == '' or 'no codable character' in str(x).lower()  # N/A value
        else '#FFFFFF' if not str(x).replace('.', '', 1).isdigit()  # BASELINE
        else '#7ED957' if float(x) >= 80
        else '#FFDE59' if 60 <= float(x) < 80
        else '#EA3423'
        for x in scores
    ]


def plot_color_maps() -> None:
    """Plot rep score color maps."""
    color_explanation = (
        'In the color maps below, we assign different colors to '
        '<mark style="background-color:#7ED957;"><strong>GOOD REPRESENTATION</strong> '
        '(80 points or higher) </mark>, '
        '<mark style="background-color:#FFDE59;"><strong>FAIR REPRESENTATION</strong> '
        '(60-79 points) </mark>, and '
        '<mark style="background-color:#EA3423;"><strong>POOR REPRESENTATION</strong> '
        '(under 60 points)</mark>.'
    )
    st.markdown(color_explanation, unsafe_allow_html=True)

    insert_line_break()

    st.markdown('Use the filter below to choose which ads you want to include in your portfolio.')

    filter_by = st.selectbox(
        label='Filter visualization by...',
        options=[
            'None',
            'Ad Name',
            'Brand',
            'Product',
            'Content Type',
            'Baseline',
            'Date Submitted',
        ],
        help='Only display assets with the specified attribute',
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

    include_baseline = st.checkbox(label='Include baseline in plot(s)', value=True)

    insert_line_break()

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
            'Please try again with a different set of filters.'
        )
        return

    if include_baseline:
        overall_df_to_plot = df_to_plot[df_to_plot['Variable'].isin(['Ad Total Score', 'BASELINE'])]
    else:
        overall_df_to_plot = df_to_plot[df_to_plot['Variable'].isin(['Ad Total Score'])]

    overall_portfolio_df_to_plot = _create_portfolio_df(df=overall_df_to_plot)

    st.markdown('##### Overall Scores, Ad Level')
    _construct_plot(
        df_to_plot=overall_df_to_plot,
        x_sort=['Ad Total Score', 'Baseline'],
        display_y_axis=True,
    )

    insert_line_break()

    st.markdown('##### Overall Scores, Portfolio Level')
    _construct_plot(
        df_to_plot=overall_portfolio_df_to_plot,
        x_sort=['Ad Total Score', 'Baseline'],
        display_y_axis=False,
        tooltip=['Variable', 'Score'],
        height=200,
    )

    if include_baseline:
        subset_df_to_plot = df_to_plot[df_to_plot['Variable'] != 'Ad Total Score']
    else:
        subset_df_to_plot = df_to_plot[
            (df_to_plot['Variable'] != 'Ad Total Score')
            & (df_to_plot['Variable'] != 'BASELINE')
        ]

    subset_df_to_plot = subset_df_to_plot.copy()

    # hacky solution to trim strings that overflow out of the ``Baseline`` column of color map cells
    subset_df_to_plot[' Score'] = subset_df_to_plot['Score'].copy()  # hacky, I know. sorry.
    subset_df_to_plot['Score'] = subset_df_to_plot['Score'].apply(
        func=lambda x: x if not isinstance(x, str) else x if len(x) < 10 else x[:8] + '...',
    )

    subset_portfolio_df_to_plot = _create_portfolio_df(df=subset_df_to_plot)

    x_sort = [
        'GENDER',
        'RACE',
        'LGBTQ+ ',
        'DISABILITY',
        'BODY SIZE',
        'AGE',
        'Baseline',
    ]

    with st.expander(label='Break down by identity', expanded=False):
        insert_line_break()

        st.markdown('##### Scores by Identity, Ad Level')
        _construct_plot(
            df_to_plot=subset_df_to_plot,
            x_sort=x_sort,
            display_y_axis=True,
            tooltip=['Ad Name', 'Brand', 'Product', 'Variable', ' Score'],
        )

        insert_line_break()

        st.markdown('##### Scores by Identity, Portfolio Level')
        _construct_plot(
            df_to_plot=subset_portfolio_df_to_plot,
            x_sort=x_sort,
            display_y_axis=False,
            tooltip=['Variable', 'Score'],
            height=200,
        )

    insert_line_break()

    st.caption(
        '\\* Note that when multiple versions of an asset have been submitted, only the '
        'most-recent version will be displayed above. To see multiple versions plotted over time, '
        'click "Rep Score Progress" on the left sidebar.'
    )


def _create_portfolio_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate ``df`` to create a portfolio view ready to plot in a color map.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame with columns ``Variable`` and ``Score``, where all variables have float scores
        except for value ``BASELINE``

    Returns
    -------
    portfolio_df: pd.DataFrame
        DataFrame aggregated by means with null values excluded. Columns include:

            * Ad Name

            * Variable

            * Score

            * color

    """
    portfolio_df = df[df['Variable'] != 'BASELINE']
    portfolio_df = portfolio_df[['Variable', 'Score']]
    portfolio_df['Score'] = pd.to_numeric(portfolio_df['Score'], errors='coerce')
    portfolio_df = portfolio_df.dropna()
    portfolio_df = portfolio_df.groupby('Variable').mean().apply(round, args=(1,)).reset_index()

    # # display combined baseline values
    # baseline_values = ', '.join(
    #     list(df.loc[df['Variable'] == 'BASELINE', 'Score'].value_counts().index)
    # )
    # portfolio_df = pd.concat(
    #     # objs=[portfolio_df, pd.DataFrame([{'Variable': 'BASELINE', 'Score': baseline_values}])],
    #     objs=[portfolio_df, pd.DataFrame([{'Variable': 'BASELINE', 'Score': '1'}])],
    # )

    portfolio_df['Ad Name'] = ''
    portfolio_df['color'] = _create_color_column(scores=portfolio_df['Score'])

    return portfolio_df


def _construct_plot(
    df_to_plot: pd.DataFrame,
    x_sort: Iterable[str] = None,
    display_y_axis: bool = True,
    tooltip: Iterable[str] = ['Ad Name', 'Brand', 'Product', 'Variable', 'Score'],
    height: Optional[int] = None,
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
    tooltip: list
        Tooltip to be displayed on cell hover
    height: int
        Optional height property to pass to the chart. If not provided, the height will be the
        default value set by ``altair.Chart``

    """
    df_to_plot = df_to_plot.copy()

    df_to_plot.loc[df_to_plot['Variable'] == 'BASELINE', 'Variable'] = 'Baseline'

    y_axis_kwargs = {
        'tickSize': 0,
        'labelPadding': 10,
        'titlePadding': 20,
        **({'title': None} if not display_y_axis else {})
    }

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
                axis=alt.Axis(**y_axis_kwargs)
            ),
        )
    )

    chart = (
        base
        .mark_rect(size=100, stroke='black', strokeWidth=0.5)
        .encode(
            color=alt.Color('color', scale=None),
            tooltip=tooltip,
        )
    )

    if height:
        chart = chart.properties(height=height)

    text = base.mark_text().encode(text='Score', tooltip=tooltip)

    full_plot = (
        (chart + text)
        .configure_axis(
            labelFontSize=15,
            labelFontWeight=alt.FontWeight('bold'),
            titleFontSize=12,
            titleFontWeight=alt.FontWeight('normal'),
        )
    )

    st.altair_chart(full_plot, use_container_width=True)


def display_qualitative_notes() -> None:
    """Display qualitative notes per unique asset."""
    notes_df = st.session_state.data_explorer_df_no_duplicates.copy()

    notes_df = notes_df.drop_duplicates(
        subset=['Ad Name', 'Brand', 'Product', 'Content Type', 'Date Submitted', 'Qual Notes'],
        keep='last',
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


def plot_rep_score_progress() -> None:
    """Plot rep score progress over content type or date submitted."""
    progress_df = st.session_state.data_explorer_df[
        st.session_state.data_explorer_df[['Ad Name', 'Brand', 'Product']]
        .duplicated(keep=False)
    ]

    # remove scores of "No Codable Characters" from consideration
    progress_df = progress_df[
        ~progress_df['Ad Total Score'].str.lower().str.contains('no codable character')
    ]

    if len(progress_df) == 0:
        st.error('No assets with more than one version scored have been uploaded and assigned!')
        return

    x_axis = st.selectbox(
        label='Select field to compare against',
        options=['Content Type', 'Date Submitted', 'Portfolio'],
        help='This sets the x-axis of the plot below',
    )

    insert_line_break()

    progress_df = progress_df[[
        'Content Type',
        'Ad Total Score',
        'Ad Name',
        'Brand',
        'Product',
        'Date Submitted',
    ]]

    progress_df['Ad Total Score'] = progress_df['Ad Total Score'].astype(float)
    progress_df['Date Submitted (Month)'] = (
        progress_df['Date Submitted']
        .dt
        .date
        .apply(lambda x: x.strftime('%b %Y'))
    )
    progress_df = progress_df.sort_values(by='Date Submitted').reset_index(drop=True)

    date_submitted_month_sorted_order = progress_df['Date Submitted (Month)'].unique().tolist()

    progress_chart_x_kwargs = {
        'color': 'Ad Name',
        'strokeDash': 'Ad Name',
        'tooltip': ['Ad Name', 'Brand', 'Product', 'Date Submitted', 'Ad Total Score'],
    }

    if x_axis == 'Portfolio':
        progress_df = (
            progress_df
            .groupby('Date Submitted (Month)')
            .mean(numeric_only=True)
            .reset_index()
        )
        progress_chart_x_kwargs = {
            'tooltip': ['Ad Total Score'],
        }

    if x_axis == 'Date Submitted' or x_axis == 'Portfolio':
        x_axis = 'Date Submitted (Month)'

    progress_chart = (
        alt
        .Chart(progress_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                shorthand=x_axis,
                sort=get_content_types() + date_submitted_month_sorted_order,  # hacky, but whatever
                axis=alt.Axis(
                    labelAngle=-45,
                    labelPadding=5,
                )
            ),
            y='Ad Total Score',
            **progress_chart_x_kwargs,
        ).properties(
            height=500,
        ).configure_point(
            size=100,
        )
    )

    st.altair_chart(progress_chart, use_container_width=True)
