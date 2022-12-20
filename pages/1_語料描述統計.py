import streamlit as st
import pandas as pd

st.markdown("# 語料描述統計")

# Cache the raw data and profile report to speed up subseuqent requests 
@st.cache
def get_basic_stats():
  d = pd.read_pickle('data/basic_stats.pkl', compression="gzip")
  return d

df_basic_stats = get_basic_stats()

df_basic_stats