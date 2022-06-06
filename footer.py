# Modified from: https://discuss.streamlit.io/t/st-footer/6447/17
from htbuilder import div, HtmlElement, img, p, styles
from htbuilder.units import percent, px
import streamlit as st


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def layout(*args):
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
        id='myFooter',
        style=styles(
            margin=px(0, 0, 0, 0),
            padding=px(0, 5, 12, 0),
            font_size='0.8rem',
            color='rgb(51,51,51)',
        ),
    )

    foot = div(style=style_div)(body)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def display_footer():
    myargs = [
        image(
            src_as_string='https://nathancooperjones.com/wp-content/uploads/2022/06/BBDO_and_Rep_Logos-e1654094195618.png',  # noqa: E501
            # width=px(25),
            height=px(20),
        ),
    ]
    layout(*myargs)
