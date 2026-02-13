import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定 (V33 終極加速版)
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="才藝班點名 V33", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

# --- 核心加速函數：合併請求與快取 ---
@st.cache_data(ttl=3600)  # 名單快取一小時
def get_initial_data(date_str):
    try:
        # 一次請求同時拿「名單」與「點名狀態」，速度快一倍
        response = requests.get(f"{SCRIPT_URL}?action=get_all_info&date={date_str}", timeout=8)
        full_data = response.json()
        
        raw_list = full_data['students']
        done_list = full_data['done']
        
        structured_data = {day: {} for day in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in raw_list:
            if len(row) < 3: continue
            class_name, student_name, subject = str(row[0]), str(row[1]), str(row[2])
            days = []
            if "舞蹈" in subject or "感統A" in subject: days = ["星期一"]
            elif any(k in subject for k in ["美術", "陶土", "美語"]): days = ["星期二", "星期五"]
            elif "桌遊" in subject or "足球" in subject: days = ["星期三"]
            elif "感統B" in subject or "直排輪" in subject: days = ["星期四"]
            
            for day in days:
                if subject not in structured_data[day]: structured_data[day][subject] = []
                structured_data[day][subject].append((class_name, student_name))
        return structured_data, done_list
    except:
        return {}, []

# 初始化或刷新
today_str = datetime.now().strftime("%Y-%m-%d")

# 如果快取中沒有，才去抓
if 'all_data' not in st.session_state:
    with st.spinner("🚀 正在加速啟動系統..."):
        all_data, done_list = get_initial_data(today_str)
        st.session_state.all_data = all_data
        st.session_state.done_list = done_list

# --- UI 介面 ---
# 側邊欄改為只在必要時刷新
with st.sidebar:
    st.title("🏫 點名系統 V33")
    if st.button("⚡ 極速刷新"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    
    # 直接從記憶體讀取，完全不卡
    all_data = st.session_state.all_data
    # ... (後續按鈕邏輯同 V32)
