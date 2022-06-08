import pandas as pd
import streamlit as st

from input_output import read_google_spreadsheet


def home_page():
    st.markdown('## Asset Overview')

    with st.spinner(text='Fetching the latest asset data...'):
        if not isinstance(st.session_state.get('asset_tracker_df'), pd.DataFrame):
            st.session_state.asset_tracker_df = read_google_spreadsheet(
                spread='https://docs.google.com/spreadsheets/d/1OR5Tj63Kzmq9AJX7XFGCzjQ7M9BEv15TkpkitXC1DgI/',  # noqa: E501
                sheet=0,
            )

    if st.session_state.asset_information.get('name'):
        st.markdown('### In Progress Assets')

        with st.expander(label=st.session_state.asset_information.get('name'), expanded=True):
            # TODO: handle nulls better here
            # st.write(f"**Asset Name**: {st.session_state.asset_information.get('name')}")
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
            # st.write(f"**Asset Name**: {row['Asset Name']}")
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
