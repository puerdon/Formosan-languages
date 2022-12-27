import streamlit as st
import pandas as pd

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
@st.cache
def get_basic_stats():
  d = pd.read_pickle('data/stats_of_each_text_20221228-2.pkl', compression="gzip")
  return d

@st.cache
def get_each_text_stats():
  d = pd.read_pickle('data/stats_of_each_text_with_subtext_20221228-2.pkl', compression="gzip")
  return d

df_basic_stats = get_basic_stats()

each_text_with_stories = get_each_text_stats()

st.markdown("## 各篇文本詞句數統計")

st.table(df_basic_stats)

st.markdown("## 含單篇子文本的詞句數統計")

st.table(each_text_with_stories)