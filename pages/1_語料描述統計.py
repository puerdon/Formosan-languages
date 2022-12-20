import streamlit as st
import pandas as pd
from nltk import sent_tokenize

st.markdown("# 語料描述統計")

# Cache the raw data and profile report to speed up subseuqent requests 
@st.cache
def get_basic_stats():
  # df = pd.read_pickle('Formosan-Mandarin_sent_pairs_139023entries.pkl')
  df = pd.read_pickle('data/basic_stats.pkl', compression="gzip")
  return df

df_basic_stats = get_basic_stats()

df_basic_stats