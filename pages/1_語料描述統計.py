import streamlit as st
import pandas as pd

st.markdown("# 語料描述統計")

# Cache the raw data and profile report to speed up subseuqent requests 
@st.cache
def get_data():
  # df = pd.read_pickle('Formosan-Mandarin_sent_pairs_139023entries.pkl')
  df = pd.read_pickle('data/Formosan-Mandarin_sent_pairs_20221219.pkl', compression="gzip")
  df = df.astype(str, errors='ignore')
  df = df.applymap(lambda x: x[1:] if x.startswith(".") else x)
  df = df.applymap(lambda x: x.strip())
  filt = df.Ch.apply(len) < 5
  df = df[~filt]
  return df

df = get_data()

df['word_count'] = df['Ab'].str.split(' ').str.len()
df['sent_count'] = df['Ab'].astype('str').apply(lambda s: len(sent_tokenize(s)))
summarized_df = df.groupby(['From']).sum()

summarized_df