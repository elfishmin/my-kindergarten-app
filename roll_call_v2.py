import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定 (V31 最終版)
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="才藝班點名系統 V31", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        @media (max-width: 991px) {
            section[data-testid="stSidebar"] { width: 250px !important; position: relative !important; margin-left: 0 !important; }
            .main { margin-left: 10px !important; }
        }
        .stRadio [role=radiogroup] { gap: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- V31 高效快取函數 ---
@st.cache_data(ttl=3600)  # 快取一小時
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=10)
        raw_list = response.json()
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
        return structured_data
    except: return {}

# --- 狀態與名單初始化 ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'done_list' not in st.session_state: st.session_state.done_list = []
if 'current_class' not in st.session_state:
    classes_today = list(all_data.get(current_day, {}).keys())
    st.session_state.current_class = classes_today[0] if classes_today else ""

# --- 側邊欄 ---
with st.sidebar:
    st.title("🏫 才藝點名系統")
    if st.button("🔄 刷新雲端名單"):
        st.cache_data.clear()
        st.rerun()
    if st.button("🔄 同步雲端狀態"):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=5)
            st.session_state.done_list = r.json() if r.status_code == 200 else []
            st.toast("同步成功！")
        except: st.toast("連線中...")
    st.divider()
    for day, classes in all_data.items():
        st.markdown(f"### {'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{day}_{c}", use_container_width=True):
                st.session_state.current_class = c

# --- 主畫面 ---
active_class = st.session_state.current_class
if not active_class:
    st.info("今天目前沒有安排才藝課程。")
else:
    students = []
    for d in all_data:
        if active_class in all_data[d]:
            students = all_data[d][active_class]
            break
    st.title(f"🍎 {active_class}")
    c_a, c_b = st.columns(2)
    with c_a:
        if st.button("🙋‍♂️ 全員到校", use_container_width=True):
            for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"
    with c_b:
        if st.button("🧹 重置", use_container_width=True):
            for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"
    st.divider()
    status_results = {}
    for class_name, name in students:
        full_id = f"{class_name}_{name}"
        col1, col2, col3 = st.columns([3, 6, 1])
        with col1: 
            st.markdown(f"<div style='display: flex; align-items: center;'><div style='width: 60px; color: gray; font-size: 12px;'>{class_name}</div><div style='font-size: 24px; font-weight: bold; color: #1E1E1E;'>{name}</div></div>", unsafe_allow_html=True)
        with col2:
            res = st.radio("S", ["到校", "請假", "未到"], horizontal=True, key=f"s_{full_id}", label_visibility="collapsed")
            status_results[full_id] = (class_name, name, res)
        with col3:
            note = st.text_input("N", key=f"n_{full_id}", label_visibility="collapsed", placeholder="原因") if res != "到校" else ""
            status_results[full_id] += (note,)
    st.divider()
    if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
        payload = [{"date": today_str, "classroom": active_class, "lesson": i[0], "name": i[1], "status": i[2], "time": datetime.now().strftime("%H:%M:%S"), "note": i[3]} for i in status_results.values()]
        with st.spinner('同步報表中...'):
            try:
                resp = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=15)
                if resp.status_code == 200:
                    st.toast("🎉 儲存成功！")
                    if active_class not in st.session_state.done_list: st.session_state.done_list.append(active_class)
                    time.sleep(1); st.rerun()
            except: st.error("連線超時，請檢查網路。")
