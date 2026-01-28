import streamlit as st

def paginate(df, page_size, page_num):
    start = (page_num - 1) * page_size
    return df.iloc[start:start + page_size]

def pagination_ui(df, key):
    page_size = st.selectbox(
        "Rows per page",
        [10, 25, 50],
        index=1,
        key=f"{key}_size"
    )
    total_pages = max(1, (len(df) - 1) // page_size + 1)

    page_num = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        key=f"{key}_page"
    )

    return paginate(df, page_size, page_num)
