import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# 頁面基本設定
st.set_page_config(page_title="才藝班點名系統 V35", page_icon="🏫", layout="wide")

# 您原本的 GAS 網址
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxTDHM3oNGMuRuKK_v8wVSM5-PWcGJfKRNMt6Sy4ClNqN280-r1oXZbRhePUD6RZ2LMVg/exec"

@st.cache_data(ttl=60)
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=15)
        data = response.json()
        raw_students = data.get("students", [])
        raw_schedule = data.get("schedule", [])
        
        # 1. 建立排程索引：{ '舞蹈A': ['星期一'] }
        # 使用 .replace(" ", "") 徹底刪除名稱中間與前後的所有空格
        course_to_days = {}
        for row in raw_schedule:
            if len(row) < 2: continue
            day = str(row[0]).replace(" ", "")
            course = str(row[1]).replace(" ", "")
            if course not in course_to_days:
                course_to_days[course] = []
            course_to_days[course].append(day)
            
        # 2. 建立資料結構
        structured_data = {d: {} for d in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        
        for row in raw_students:
            if len(row) < 3: continue
            class_name = str(row[0]).strip()
            student_name = str(row[1]).strip()
            subject = str(row[2]).replace(" ", "") # 名單內的課程也徹底去空格
            
            # 3. 嚴格比對名稱 (A 就是 A，B 就是 B)
            if subject in course_to_days:
                target_days = course_to_days[subject]
                for day in target_days:
                    if day in structured_data:
                        if subject not in structured_data[day]:
                            structured_data[day][subject] = []
                        structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return {}

# --- 側邊欄與主畫面 UI ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'current_class' not in st.session_state: st.session_state.current_class = ""
if 'current_day_sel' not in st.session_state: st.session_state.current_day_sel = current_day

with st.sidebar:
    st.title("🏫 V35 才藝點名")
    if st.button("🔄 刷新雲端名單"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    for day, classes in all_data.items():
        if not classes: continue
        st.subheader(f"{day}")
        for c in classes.keys():
            # 顯示已點名狀態 (這裡可串接您的 done_list 邏輯)
            if st.button(f"📝 {c}", key=f"{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day

# 主畫面
if st.session_state.current_class:
    active_class = st.session_state.current_class
    sel_day = st.session_state.current_day_sel
    st.title(f"🍎 {active_class} ({sel_day})")
    
    students = all_data.get(sel_day, {}).get(active_class, [])
    if students:
        for i, (cn, sn) in enumerate(students):
            col1, col2 = st.columns([1, 2])
            with col1: st.write(f"**{cn}**")
            with col2: st.radio("狀態", ["到校", "請假", "未到"], key=f"r_{active_class}_{sn}_{i}", horizontal=True)
    else:
        st.warning("找不到學生，請檢查 transformat 表內的課程名稱是否正確。")
