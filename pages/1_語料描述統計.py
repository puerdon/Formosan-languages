import streamlit as st
import pandas as pd

st.markdown("# 語料描述統計")

# Cache the raw data and profile report to speed up subseuqent requests 
@st.cache
def get_basic_stats():
  d = pd.read_pickle('data/stats_of_each_text.pkl', compression="gzip")
  return d

@st.cache
def get_each_text_stats():
  d = pd.read_pickle('data/stats_of_text_with_stories.pkl', compression="gzip")
  return d

df_basic_stats = get_basic_stats()

each_text_with_stories = get_each_text_stats()

st.markdown("## 各篇文本詞句數統計")

df_basic_stats

st.markdown("## 含單篇子文本的詞句數統計")

each_text_with_stories