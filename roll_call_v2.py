import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定
# ==========================================
# 請確保 GitHub 上的檔名與此處完全一致
CSV_FILE = "2_總才藝班修課名冊.xlsx - Sheet1.csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="全校才藝班點名系統", page_icon="🏫", layout="wide")

# --- 自動讀取 CSV (處理 240 筆名單) ---
@st.cache_data
def load_all_students():
    try:
        # 讀取 CSV
        df = pd.read_csv(CSV_FILE)
        # 清理欄位前後空白
        df.columns = [c.strip() for c in df.columns]
        # 排除姓名或課程為空的無效行
        df = df.dropna(subset=['姓名', '課程名稱'])
        # 確保內容也是乾淨的字串
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"❌ 讀取名冊失敗，請檢查 GitHub 是否有上傳 '{CSV_FILE}'。")
        st.info(f"錯誤訊息: {e}")
        return pd.DataFrame()

df = load_all_students()

# 建立課程字典結構: { "星期一": { "足球": [(班級, 姓名), ...], "直排輪": [...] } }
all_data = {}
if not df.empty:
    # 按照 CSV 內的「上課星期」分組
    for day in df['上課星期'].unique():
        all_data[day] = {}
        day_df = df[df['上課星期'] == day]
        for course in day_df['課程名稱'].unique():
            course_df = day_df[day_df['課程名稱'] == course]
            student_list = list(zip(course_df['班級'], course_df['姓名']))
            all_data[day][course] = student_list

# 時間設定
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
current_day_name = weekday_map.get(today_dt.weekday(), "星期一")

# --- 2. 狀態管理 ---
if 'done_list' not in st.session_state:
    st.session_state.done_list = []
if 'current_class' not in st.session_state:
    # 預設顯示今天的課程，若今天沒課則抓第一筆有課的星期
    if current_day_name in all_data and all_data[current_day_name]:
        st.session_state.current_class = list(all_data[current_day_name].keys())[0]
    elif all_data:
        first_day = list(all_data.keys())[0]
        st.session_state.current_class = list(all_data[first_day].keys())[0]
    else:
        st.session_state.current_class = "無課程"

# --- 3. 側邊欄：顯示所有星期與課程 ---
with st.sidebar:
    st.title("🏫 全校才藝班名冊")
    st.write(f"📅 今天是：{today_str} ({current_day_name})")
    
    if st.button("🔄 刷新雲端狀態", use_container_width=True):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=5)
            st.session_state.done_list = r.json() if r.status_code ==
