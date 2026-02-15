import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定 (V35 排程動態化版)
# ==========================================
# 注意：st.set_page_config 必須是除了 import 之外的第一行程式碼
st.set_page_config(page_title="才藝班點名系統 V35", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

# 填入您的 Google Apps Script 網址 (請確保已按前一封建議更新 GAS 代碼)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxTDHM3oNGMuRuKK_v8wVSM5-PWcGJfKRNMt6Sy4ClNqN280-r1oXZbRhePUD6RZ2LMVg/exec"

st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        .stRadio [role=radiogroup] { gap: 15px; }
        .warning-box {
            padding: 20px;
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- V35 核心同步函數：讀取 schedule 分頁 ---
@st.cache_data(ttl=3600)
def fetch_cloud_data():
    try:
        # 向 GAS 請求包含學生與 schedule 排程的資料
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=10)
        json_data = response.json()
        
        raw_students = json_data.get("students", [])
        raw_schedule = json_data.get("schedule", [])  # 從 Google 試算表 schedule 分頁抓取
        
        # 建立課程對應星期的對照表: { '課程名': ['星期一', '星期二'] }
        course_to_days = {}
        for row in raw_schedule:
            if len(row) < 2: continue
            day_val = str(row[0]).strip()     # A 欄：星期
            course_val = str(row[1]).strip()  # B 欄：課程名稱
            if course_val not in course_to_days:
                course_to_days[course_val] = []
            course_to_days[course_val].append(day_val)
            
        # 依照星期結構組織資料
        structured_data = {day: {} for day in ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]}
        
        for row in raw_students:
            if len(row) < 3: continue
            class_name, student_name, subject = str(row[0]), str(row[1]), str(row[2])
            
            # 從 schedule 分頁對應關係找出該課程屬於哪幾天
            target_days = course_to_days.get(subject, [])
            
            for day in target_days:
                if day in structured_data:
                    if subject not in structured_data[day]:
                        structured_data[day][subject] = []
                    structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except Exception as e:
        st.error(f"☁️ 雲端同步失敗，請檢查 GAS 網址或 schedule 分頁：{e}")
        return {}

# --- 初始化狀態與側邊欄邏輯 ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'done_list' not in st.session_state: st.session_state.done_list = []
if 'current_class' not in st.session_state: st.session_state.current_class = ""
if 'current_day_sel' not in st.session_state: st.session_state.current_day_sel = current_day
if 'unlock_non_today' not in st.session_state: st.session_state.unlock_non_today = False

# --- 側邊欄 UI ---
with st.sidebar:
    st.title("🏫 V35 才藝點名")
    if st.button("🔄 刷新雲端名單"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    
    # 根據 schedule 分頁產生的選單
    for day, classes in all_data.items():
        if not classes: continue # 沒課的星期不顯示
        st.markdown(f"### {'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day
                st.session_state.unlock_non_today = (day == current_day)

# --- 主畫面點名邏輯 ---
active_class = st.session_state.current_class
selected_day = st.session_state.current_day_sel

if not active_class:
    st.info("💡 請從左側選單選擇今日課程進行點名。")
else:
    # 安全鎖與點名介面 (此處延用 V34 穩定邏輯)
    is_today = (selected_day == current_day)
    if not is_today and not st.session_state.unlock_non_today:
        st.markdown(f'<div class="warning-box"><h2>⚠️ 非當天點名</h2><p>這是 {selected_day} 的課，今天是 {current_day}。</p></div>', unsafe_allow_html=True)
        if st.button(f"🔓 確認補登 {selected_day} 紀錄", use_container_width=True):
            st.session_state.unlock_non_today = True
            st.rerun()
    else:
        st.title(f"🍎 {active_class} ({selected_day})")
        students = all_data.get(selected_day, {}).get(active_class, [])
        
        # 點名表單與儲存 (Payload 與 GAS 對接)
        # ... (此處代碼同前版本儲存邏輯)
        st.write(f"本班級共 {len(students)} 位學生")
        # 這裡放置 radio 點名按鈕...
