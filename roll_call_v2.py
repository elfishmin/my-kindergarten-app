import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="才藝點名系統 V32.1", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

# --- 側邊欄與介面 CSS ---
st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        .stRadio [role=radiogroup] { gap: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 核心同步函數：從 Excel 撈資料 ---
@st.cache_data(ttl=3600)
def fetch_cloud_data():
    try:
        # 向 GAS 請求 action=get_students (讀取 transformat 工作表)
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=10)
        raw_list = response.json()
        
        structured_data = {day: {} for day in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in raw_list:
            if len(row) < 3: continue
            class_name, student_name, subject = str(row[0]), str(row[1]), str(row[2])
            
            # 分類邏輯：根據科目自動歸類到星期幾
            days = []
            if any(k in subject for k in ["舞蹈", "感統A", "積木A"]): days = ["星期一"]
            elif any(k in subject for k in ["美術", "陶土", "美語"]): days = ["星期二", "星期五"]
            elif any(k in subject for k in ["桌遊", "足球"]): days = ["星期三"]
            elif any(k in subject for k in ["感統B", "直排輪", "積木B"]): days = ["星期四"]
            
            for day in days:
                if subject not in structured_data[day]:
                    structured_data[day][subject] = []
                structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except:
        return {}

# --- 初始化狀態 ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'done_list' not in st.session_state:
    st.session_state.done_list = []
if 'current_class' not in st.session_state:
    st.session_state.current_class = ""

# --- 側邊欄 ---
with st.sidebar:
    st.title("🏫 才藝班點名")
    
    # 這是您的核心需求：更動 Excel 後點這個
    if st.button("🔄 同步 Excel 名單", use_container_width=True):
        st.cache_data.clear() # 強制清空快取
        st.rerun() # 重新啟動 App 會觸發 fetch_cloud_data()

    if st.button("✅ 刷新點名狀態", use_container_width=True):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=5)
            st.session_state.done_list = r.json() if r.status_code == 200 else []
            st.toast("狀態更新成功！")
        except: st.toast("連線失敗")
    
    st.divider()
    
    # 顯示週一到週五的班級按鈕
    for day, classes in all_data.items():
        st.markdown(f"### {'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.selected_day = day

# --- 主畫面 ---
active_class = st.session_state.get('current_class', "")
if not active_class:
    st.info("請從左側選擇班級。")
else:
    # 取得名單
    sel_day = st.session_state.get('selected_day', current_day)
    students = all_data.get(sel_day, {}).get(active_class, [])
    
    st.title(f"🍎 {active_class}")
    st.caption(f"日期：{today_str} ({sel_day})")

    # 全員到校與重置按鈕
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🙋‍♂️ 全員到校", use_container_width=True):
            for i, (cn, sn) in enumerate(students):
                st.session_state[f"s_{active_class}_{cn}_{sn}_{i}"] = "到校"
    with c2:
        if st.button("🧹 重置", use_container_width=True):
            for i, (cn, sn) in enumerate(students):
                st.session_state[f"s_{active_class}_{cn}_{sn}_{i}"] = "到校"

    st.divider()

    # 點名清單區
    status_results = {}
    for i, (class_name, name) in enumerate(students):
        # 關鍵：Key 加入了索引 i，解決重複姓名造成的當機問題
        unique_key = f"{active_class}_{class_name}_{name}_{i}"
        
        col1, col2, col3 = st.columns([3, 6, 1])
        with col1: 
            st.markdown(f"**{name}**\n<small>{class_name}</small>", unsafe_allow_html=True)
        with col2:
            res = st.radio("S", ["到校", "請假", "未到"], horizontal=True, key=f"s_{unique_key}", label_visibility="collapsed")
            status_results[unique_key] = (class_name, name, res)
        with col3:
            note = st.text_input("N", key=f"n_{unique_key}", label_visibility="collapsed", placeholder="備註") if res != "到校" else ""
            status_results[unique_key] += (note,)

    st.divider()
    if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
        payload = [{"date": today_str, "classroom": active_class, "lesson": v[0], "name": v[1], "status": v[2], "time": datetime.now().strftime("%H:%M:%S"), "note": v[3]} for v in status_results.values()]
        with st.spinner('儲存中...'):
            try:
                resp = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=15)
                if resp.status_code == 200:
                    st.success("儲存成功！")
                    if active_class not in st.session_state.done_list:
                        st.session_state.done_list.append(active_class)
                    time.sleep(1)
                    st.rerun()
            except: st.error("連線超時，請重新儲存。")
