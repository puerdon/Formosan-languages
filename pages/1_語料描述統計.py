import streamlit as st
import pandas as pd

st.markdown("""# 資料概要
- Egerod (1969): a conversation with English translation
- Egerod (1974): a conversation with English translation
- Rau (1992): 6 stories with English translation
- Rau et al. (1995): 5 stories with Mandarin translation
- Huang (1993): a conversation with English translation
- Huang & Wu (2016): 2 stories with Mandarin translation
- 泰雅爾族傳說故事精選輯 (Y&Y 1991): 20 stories with Mandarin translation
- 泰雅族大嵙崁群的部落故事: 17 stories with Mandarin translation
- 復興鄉泰雅族故事(一): 20 stories with Mandarin translation
- 復興鄉泰雅族故事(二): 20 stories with Mandarin translation
- 和平鄉泰雅族故事: 26 stories with Mandarin translation (TBD)""")

st.markdown("# 語料描述統計")

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)


# Cache the raw data and profile report to speed up subseuqent requests
@st.cache_data
def get_basic_stats():
    d = pd.read_pickle(
        'data/stats_of_each_text_20230321.pkl', compression="gzip")
    return d


@st.cache_data
def get_each_text_stats():
    d = pd.read_pickle(
        'data/stats_of_each_text_with_subtext_20221228-3.pkl', compression="gzip")
    return d


df_basic_stats = get_basic_stats()

each_text_with_stories = get_each_text_stats()

st.markdown("## 各篇文本詞句數統計")

st.table(df_basic_stats)

st.markdown("## 含單篇子文本的詞句數統計")

st.table(each_text_with_stories)
