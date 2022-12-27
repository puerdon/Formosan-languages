import pandas as pd
import base64
import streamlit as st
import streamlit.components.v1 as components
import re
from pandas_profiling import ProfileReport
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

import xlsxwriter
from io import BytesIO

def main():
  st.set_page_config(layout="wide")
  st.title("台灣南島語文本數位資料庫")
  st.subheader("Formosan Digital Database")
  st.markdown(
    """
![visitors](https://visitor-badge.glitch.me/badge?page_id=howard-haowen.Formosan-languages)

### 資料概要
- Egerod (1969): a conversation with English translation (TBD)
- Egerod (1974): a conversation with English translation
- Rau (1992): 6 stories with English translation
- Rau et al. (1995): 5 stories with Mandarin translation
- Huang (1993): a conversation with English translation
- Huang (1994): a story with English translation
- Huang & Wu (2016): 2 stories with Mandarin translation
- 泰雅爾族傳說故事精選輯 (Y&Y 1991): 20 stories with Mandarin translation
- 泰雅族大嵙崁群的部落故事: 17 stories with Mandarin translation
- 復興鄉泰雅族故事(一): 20 stories with Mandarin translation
- 復興鄉泰雅族故事(二): 20 stories with Mandarin translation
- 和平鄉泰雅族故事: 26 stories with Mandarin translation (TBD)


(⚠️ 此查詢系統僅供教學與研究之用，內容版權歸原始資料提供者所有)

### 查詢方法
- 🔭 過濾：使用左側欄功能選單可過濾資料來源(可多選)與語言，也可使用華語或族語進行關鍵詞查詢。
  - 🔍 關鍵詞查詢支援[正則表達式](https://zh.wikipedia.org/zh-tw/正则表达式)。
  - 🥳 族語範例: 
    + 搜尋以 mn 開頭的句子：輸入`^mn`。
    + 由於半形的`.`和`?`在正則表達式有特殊功能，因此若要搜尋出現在文本中的半形句點和問號。請在前方加上反斜線(backslash):`\.`和`\?`。搜尋逗號、冒號、驚嘆號毋須加上反斜線。
    + 搜尋作為單詞的 aki ，而非包含有aki的詞彙，請將單詞包在兩個`\b`之間：`\baki\b`（`\b`意為 word boundary）。
    + 搜尋所有以 mn 開頭的單詞：輸入`\bmn`。
    + 搜尋所有的 ga (泰雅主題標記)：輸入`\bga[ ,!\.\?]`。(這串搜尋的意義是:ga前面為word boundary，而ga的後面可以出現空格、逗號、驚嘆號、句號或問號其中之一。)
    + 搜尋單詞 ini 或 `ini'`：輸入`\bini'?\b`
  - 🤩 華語範例: 
    + 找出以「可能」作為開頭的句子：輸入`^可能`。
    + 找出「了」出現在句尾的句子：輸入`了$`。
- 📚 排序：點選標題列。例如點選`族語`欄位標題列內的任何地方，資料集便會根據族語重新排序。

"""
)
  # fetch the raw data
  df = get_data()
  # pd.set_option('max_colwidth', 600)
  
  # remap column names
  zh_columns = {'Lang_En': 'Language','Lang_Ch': '語言_方言', 'Ab': '族語', 'Ch': '華語', 'From': '來源'}
  df.rename(columns=zh_columns, inplace=True)
  
  # set up filtering options
  source_set = df['來源'].unique()
  sources = st.sidebar.multiselect(
        "請選擇資料來源",
        options=source_set,
        default=list(source_set))
  langs = st.sidebar.selectbox(
        "請選擇語言",
        #options=['泰雅','布農','阿美','撒奇萊雅','噶瑪蘭','魯凱','排灣','卑南',
        #         '賽德克','太魯閣','鄒','拉阿魯哇','卡那卡那富',
        #         '邵','賽夏','達悟'],)
        options=['泰雅'],)
  texts = st.sidebar.radio(
        "請選擇關鍵詞查詢文字類別",
        options=['族語','華語'],)
    
  # filter by sources
  s_filt = df['來源'].isin(sources)
  
  # select a language 
  if langs == "噶瑪蘭":
    l_filt = df['Language'] == "Kavalan"
  elif langs == "阿美":
    l_filt = df['Language'] == "Amis"
  elif langs == "撒奇萊雅":
    l_filt = df['Language'] == "Sakizaya"
  elif langs == "魯凱":
    l_filt = df['Language'] == "Rukai"
  elif langs == "排灣":
    l_filt = df['Language'] == "Paiwan"
  elif langs == "卑南":
    l_filt = df['Language'] == "Puyuma"
  elif langs == "賽德克":
    l_filt = df['Language'] == "Seediq"
  elif langs == "邵":
    l_filt = df['Language'] == "Thao"
  elif langs == "拉阿魯哇":
    l_filt = df['Language'] == "Saaroa"
  elif langs == "達悟":
    l_filt = df['Language'] == "Yami"
  elif langs == "泰雅":
    l_filt = df['Language'] == "Atayal"
  elif langs == "太魯閣":
    l_filt = df['Language'] == "Truku"
  elif langs == "鄒":
    l_filt = df['Language'] == "Tsou"
  elif langs == "卡那卡那富":
    l_filt = df['Language'] == "Kanakanavu"
  elif langs == "賽夏":
    l_filt = df['Language'] == "Saisiyat"
  elif langs == "布農":
    l_filt = df['Language'] == "Bunun"
  
  # create a text box for keyword search
  text_box = st.sidebar.text_input('在下方輸入華語或族語，按下ENTER後便會自動更新查詢結果')

  # search for keywords in Mandarin or Formosan 
  t_filt = df[texts].str.contains(text_box, flags=re.IGNORECASE)
  
  # filter the data based on all criteria
  filt_df = df[(s_filt)&(l_filt)&(t_filt)]

  st.markdown(
    """
### 查詢結果
"""
)
  # display the filtered data
  # st.dataframe(filt_df, width=1600, height=600)
  # st.table(filt_df)

  c = JsCode(
  """
  function(params) {
    return params.data.族語;
  }
  """)

  # add pagination to df
  gb = GridOptionsBuilder.from_dataframe(filt_df)
  gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)

  large_font = { "font-size": "1.5em" }

  if len(text_box) != 0:
    gb.configure_column(texts, cellRenderer=dynamic_js_code(text_box))


  # gb.configure_column("aa", valueGetter=c, cellRenderer=dynamic_js_code(text_box))
  gb.configure_columns(filt_df.columns, cellStyle=large_font)
  gridOptions = gb.build()
  AgGrid(filt_df, gridOptions=gridOptions, allow_unsafe_jscode=True, height=650)

  st.markdown(
    """
### 查詢結果下載
"""
)
  # download link for .csv file
  st.markdown(get_table_download_link(filt_df), unsafe_allow_html=True)

  output = BytesIO()
  with pd.ExcelWriter(output) as writer:
    filt_df.to_excel(writer)

  st.download_button(
        label="下載查詢結果 (.xlsx檔)",
        data=output.getvalue(),
        file_name="result.xlsx",
        mime="application/vnd.ms-excel"
  )




  # st.markdown("""### 資料統計""")
  # display a data profile report
  # report = get_report()
  # components.html(report, width=800, height=800, scrolling=True)  
  
# Cache the raw data and profile report to speed up subseuqent requests 
@st.cache
def get_data():
  # df = pd.read_pickle('Formosan-Mandarin_sent_pairs_139023entries.pkl')
  df = pd.read_pickle('data/Formosan-Mandarin_sent_pairs_20221227-2.pkl', compression="gzip")
  df = df.astype(str, errors='ignore')
  df = df.applymap(lambda x: x[1:] if x.startswith(".") else x)
  df = df.applymap(lambda x: x.strip())
  filt = df.Ch.apply(len) < 5
  df = df[~filt]
  return df

@st.cache
def get_report():
  df = get_data()
  report = ProfileReport(df, title='Report', minimal=True).to_html()
  return report

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a download="result.csv" href="data:file/csv;base64,{b64}">點此下載查詢結果 (CSV檔)</a>'
    return href

def dynamic_js_code(text):
  x = """
  function(params) {{
    var re = /{0}/gi;
    console.log(params.value);
    var news = params.value.replace(re, '<span style="background-color: #f7cac9;">$&</span>');
    return news;
  }}
  """.format(text)

  return JsCode(x)

if __name__ == '__main__':
  main()
