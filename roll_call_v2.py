import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# 必須放在最前面
st.set_page_config(page_title="才藝班點名系統 V35", page_icon="🏫", layout="wide")

# 修改為您的 GAS 網址
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxTDHM3oNGMuRuKK_v8wVSM5-PWcGJfKRNMt6Sy4ClNqN280-r1oXZbRhePUD6RZ2LMVg/exec"

# --- 核心資料讀取：增加 strip() 容錯處理 ---
@st.cache_data(ttl=600)
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=15)
        data = response.json()
        
        raw_students = data.get("students", [])
        raw_schedule = data.get("schedule", [])
        
        # 1. 處理排程：建立 { 課程名稱: [星期] } 的對照表
        course_to_days = {}
        for row in raw_schedule:
            if len(row) < 2: continue
            day = str(row[0]).strip()     # 去除空格
            course = str(row[1]).strip()  # 去除空格
            if course not in course_to_days:
                course_to_days[course] = []
            course_to_days[course].append(day)
            
        # 2. 處理學生並歸類到對應星期
        structured_data = {d: {} for d in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in raw_students:
            if len(row) < 3: continue
            class_name, student_name, subject = str(row[0]).strip(), str(row[1]).strip(), str(row[2]).strip()
            
            # 尋找該課程在哪幾天有課
            target_days = course_to_days.get(subject, [])
            for day in target_days:
                if day in structured_data:
                    if subject not in structured_data[day]:
                        structured_data[day][subject] = []
                    structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return {}

# --- 初始化與 UI 介面 ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'current_class' not in st.session_state: st.session_state.current_class = ""
if 'current_day_sel' not in st.session_state: st.session_state.current_day_sel = current_day

# --- 側邊欄 ---
with st.sidebar:
    st.title("🏫 才藝點名 V35")
    if st.button("🔄 刷新名單"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    
    for day, classes in all_data.items():
        if not classes: continue
        st.subheader(f"{'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            if st.button(f"📝 {c}", key=f"{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day

# --- 主畫面 ---
active_class = st.session_state.current_class
selected_day = st.session_state.current_day_sel

if active_class:
    st.title(f"🍎 {active_class} ({selected_day})")
    students = all_data[selected_day][active_class]
    
    # 這裡進行 radio 點名 UI 繪製...
    # (儲存邏輯與 V34 相同)
else:
    st.info("請從左側選擇課程開始點名")
