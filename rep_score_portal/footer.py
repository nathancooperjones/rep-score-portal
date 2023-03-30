# Modified from: https://discuss.streamlit.io/t/st-footer/6447/17
from typing import Union

from htbuilder import div, HtmlElement, img, p, styles
from htbuilder.units import percent, px
import streamlit as st


def layout(*args: Union[HtmlElement, str]) -> None:
    """Create the footer layout using ``htbuilder``."""
    style_div = styles(
        position='fixed',
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color='black',
        text_align='right',
        height='auto',
        opacity=1,
        z_index=100,
    )

    body = p(
        id='custom_streamlit_footer',
        style=styles(
            margin=px(0, 0, 0, 0),
            padding=px(0, 5, 12, 0),
            font_size='0.8rem',
            color='rgb(51,51,51)',
        ),
    )

    footer = div(style=style_div)(body)

    for arg in args:
        body(arg)

    st.markdown(str(footer), unsafe_allow_html=True)


def display_footer() -> None:
    """Display the footer."""
    layout(
        img(
            src='https://trp-other.s3.amazonaws.com/images/BBDO_and_Rep_Logos.png',
            style=styles(height=px(37)),
        )
    )
