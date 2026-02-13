import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定 (V33 加速版)
# ==========================================
# 請務必更換成您 GAS 部署後的新網址
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="才藝點名 V33", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

# --- 側邊欄隱藏按鈕 CSS ---
st.markdown("""<style>[data-testid="collapsedControl"] { display: none !important; } .stRadio [role=radiogroup] { gap: 15px; }</style>""", unsafe_allow_html=True)

# --- 核心同步函數 ---
def fetch_data():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        resp = requests.get(f"{SCRIPT_URL}?action=get_all_info&date={today}", timeout=10).json()
        
        # 建立週一至週五結構
        new_data = {d: {} for d in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in resp['students']:
            c_name, s_name, subject = str(row[0]), str(row[1]), str(row[2])
            
            # 自動判定星期的邏輯 (依據您的科目安排)
            days = []
            if any(k in subject for k in ["舞蹈", "感統A"]): days = ["星期一"]
            elif any(k in subject for k in ["美術", "陶土", "美語"]): days = ["星期二", "星期五"]
            elif any(k in subject for k in ["桌遊", "足球"]): days = ["星期三"]
            elif any(k in subject for k in ["感統B", "直排輪"]): days = ["星期四"]
            
            for d in days:
                if subject not in new_data[d]: new_data[d][subject] = []
                new_data[d][subject].append((c_name, s_name))
        
        st.session_state.all_data = new_data
        st.session_state.done_list = resp['done']
    except Exception as e:
        st.error(f"連線失敗: {e}")

# 初始化
if 'all_data' not in st.session_state:
    with st.spinner("🚀 系統啟動中..."):
        fetch_data()

# --- 介面佈局 ---
with st.sidebar:
    st.title("🏫 才藝班點名")
    if st.button("⚡ 重新同步名單與狀態", use_container_width=True):
        st.cache_data.clear()
        fetch_data()
        st.rerun()
    st.divider()
    
    all_data = st.session_state.get('all_data', {})
    done_list = st.session_state.get('done_list', [])
    weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
    current_day = weekday_map.get(datetime.now().weekday(), "星期一")

    for day, classes in all_data.items():
        st.markdown(f"### {'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{day}_{c}", use_container_width=True):
                st.session_state.current_class = c

# --- 主點名畫面 ---
active_class = st.session_state.get('current_class', "")
if active_class:
    students = []
    for d in all_data:
        if active_class in all_data[d]:
            students = all_data[d][active_class]
            break
    
    st.title(f"🍎 {active_class}")
    # (點名單 radio 按鈕邏輯同前版本...)
    # ... 此處請接續 V32 的點名 UI 邏輯 ...
    
    # 儲存按鈕
    if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
        # 儲存邏輯 (payload 發送至 SCRIPT_URL)
        pass
