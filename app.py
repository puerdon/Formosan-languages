import pandas as pd
import base64
import streamlit as st
import streamlit.components.v1 as components
import re
# from pandas_profiling import ProfileReport
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
# Read sheet from Google
from streamlit_gsheets import GSheetsConnection

import xlsxwriter
from io import BytesIO

LANG_ENG_TABLE = {
"阿美":"Amis",
"泰雅":"Atayal",
"排灣":"Paiwan",
"布農":"Bunun",
"卑南":"Puyuma",
"魯凱":"Rukai",
"鄒":"Tsou",
"卡那卡那富":"Kanakanavu",
"拉阿魯哇":"Saaroa",
"賽夏":"Saisiyat",
"雅美":"Yami",
"邵":"Thao",
"噶瑪蘭":"Kavalan",
"太魯閣":"Truku",
"撒奇萊雅":"Sakizaya",
"賽德克":"Seediq"
}

# Initialization
# if 'last_update_time' not in st.session_state:
#     st.session_state['last_update_time'] = 0

def main():
    
    st.set_page_config(layout="wide")
    st.title("台灣南島語文本數位資料庫")
    st.subheader("Formosan Digital Database")
    
    # st.write(st.session_state['last_update_time'])
    
    st.markdown(
        """
⚠️ 此查詢系統僅供教學與研究之用，內容版權歸原始資料提供者所有"""
    )

    with st.expander("查詢方法"):
        st.markdown('''
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
        ''')

    # check last updated time:
    last_update_timestamp = get_last_updated_timestamp()
    df = load_data(last_update_timestamp)

    # df = pd.concat([df, user_df], ignore_index=True)
    # pd.set_option('max_colwidth', 600)

    # remap column names
    zh_columns = {
        'Lang_En': 'Language',
        'Lang_Ch': '語言_方言',
        'Ab': '族語',
        'Ch': '華語',
        'From': '來源'
    }
    df.rename(columns=zh_columns, inplace=True)

    # set up filtering options
    langs = st.sidebar.selectbox(
        "請選擇語言",
        options=['泰雅', '布農', '阿美', '撒奇萊雅', '噶瑪蘭', '魯凱', '排灣', '卑南',
                 '賽德克', '太魯閣', '鄒', '拉阿魯哇', '卡那卡那富',
                 '邵', '賽夏', '達悟'],
    )

    sources = st.sidebar.multiselect(
        "請選擇資料來源",
        options=df[df['Language'] == LANG_ENG_TABLE[langs]]['來源'].unique(),
        default=df[df['Language'] == LANG_ENG_TABLE[langs]]['來源'].unique())
    
    texts = st.sidebar.radio(
        "請選擇關鍵詞查詢文字類別",
        options=['族語', '華語'],)

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
    filt_df = df[(s_filt) & (l_filt) & (t_filt)]

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

    # CSS to inject contained in a string
    hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """

    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    # add pagination to df
    gb = GridOptionsBuilder.from_dataframe(filt_df)
    gb.configure_pagination(
        paginationAutoPageSize=False, paginationPageSize=20)

    large_font = {"font-size": "1.5em"}

    # if len(text_box) != 0:
    # gb.configure_column(texts, cellRenderer=dynamic_js_code(text_box))

    # gb.configure_column("aa", valueGetter=c, cellRenderer=dynamic_js_code(text_box))
    gb.configure_columns(filt_df.columns, cellStyle=large_font)
    gridOptions = gb.build()
    # AgGrid(filt_df, gridOptions=gridOptions, allow_unsafe_jscode=True, height=650)
    AgGrid(filt_df, gridOptions=gridOptions, allow_unsafe_jscode=True)
    # st.dataframe(filt_df, use_container_width=True)
    st.markdown(
        """
### 查詢結果下載
"""
    )
    # download link for .csv file
    # st.markdown(get_table_download_link(filt_df), unsafe_allow_html=True)

    output_xlsx = BytesIO()
    output_csv = BytesIO()

    with pd.ExcelWriter(output_xlsx) as writer:
        filt_df.to_excel(writer)

    filt_df.to_csv(output_csv)

    st.download_button(
        label=".xlsx檔",
        data=output_xlsx.getvalue(),
        file_name="result.xlsx",
        mime="application/vnd.ms-excel"
    )

    st.download_button(
        label=".csv檔",
        data=output_csv.getvalue(),
        file_name="result.csv",
        mime="text/csv"
    )

    # st.markdown("""### 資料統計""")
    # display a data profile report
    # report = get_report()
    # components.html(report, width=800, height=800, scrolling=True)

# Cache the raw data and profile report to speed up subseuqent requests


# @st.cache_data
# def get_data():
    
#     # df = pd.read_pickle('Formosan-Mandarin_sent_pairs_139023entries.pkl')
#     # df = pd.read_pickle(
#     #     'data/Formosan-Mandarin_sent_pairs_20230321.pkl', compression="gzip")
#     # df = df.astype(str, errors='ignore')
#     # df = df.applymap(lambda x: x[1:] if x.startswith(".") else x)
#     # df = df.applymap(lambda x: x.strip())
#     # filt = df.Ch.apply(len) < 5
#     # df = df[~filt]
#     df = get_df_from_google()
#     return df


def load_data(update_timestamp):
    # update_timestamp = get_last_updated_timestamp()
    return cached_data_load(update_timestamp)

@st.cache_data
def cached_data_load(timestamp):
    # Connecting to google sheet
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(worksheet="main corpus", ttl=0)
    df = df.astype(str, errors='ignore')
    df = df.applymap(lambda x: x[1:] if x.startswith(".") else x)
    df = df.applymap(lambda x: x.strip())
    filt = df.Ch.apply(len) < 5
    df = df[~filt]

    user_df = conn.read(worksheet="user corpus", ttl=0)
    user_df = user_df.astype(str, errors='ignore')
    user_df = user_df.applymap(lambda x: x[1:] if x.startswith(".") else x)
    user_df = user_df.applymap(lambda x: x.strip())
    filt = user_df.Ch.apply(len) < 5
    user_df = user_df[~filt]

    result_df = df._append(user_df, ignore_index=True)
    return result_df


def get_last_updated_timestamp():
    # Connecting to google sheet
    conn = st.connection("gsheets", type=GSheetsConnection)
    last_ = conn.read(worksheet="last updated", ttl=0)
    last_update_timestamp = int(last_.time[0])
    return last_update_timestamp

# def get_df_from_google():
#     # Connecting to google sheet
#     conn = st.connection("gsheets", type=GSheetsConnection)

#     df = conn.read(worksheet="main corpus", ttl=0)
#     df = df.astype(str, errors='ignore')
#     df = df.applymap(lambda x: x[1:] if x.startswith(".") else x)
#     df = df.applymap(lambda x: x.strip())
#     filt = df.Ch.apply(len) < 5
#     df = df[~filt]

#     user_df = conn.read(worksheet="user corpus", ttl=0)
#     user_df = user_df.astype(str, errors='ignore')
#     user_df = user_df.applymap(lambda x: x[1:] if x.startswith(".") else x)
#     user_df = user_df.applymap(lambda x: x.strip())
#     filt = user_df.Ch.apply(len) < 5
#     user_df = user_df[~filt]

#     result_df = df._append(user_df, ignore_index=True)
#     return result_df

# @st.cache_data
# def get_report():
#     df = get_data()
#     report = ProfileReport(df, title='Report', minimal=True).to_html()
#     return report


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(csv.encode()).decode()
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
