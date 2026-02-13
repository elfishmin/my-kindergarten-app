import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定 (V34 安全鎖版)
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="才藝班點名系統 V34", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        @media (max-width: 991px) {
            section[data-testid="stSidebar"] { width: 250px !important; position: relative !important; margin-left: 0 !important; }
            .main { margin-left: 10px !important; }
        }
        .stRadio [role=radiogroup] { gap: 15px; }
        /* 警告框樣式 */
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

# --- 核心同步函數 (與 V33 相同) ---
@st.cache_data(ttl=3600)
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

# --- 初始化狀態 ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'done_list' not in st.session_state: st.session_state.done_list = []
if 'current_class' not in st.session_state: st.session_state.current_class = ""
if 'current_day_sel' not in st.session_state: st.session_state.current_day_sel = current_day
if 'unlock_non_today' not in st.session_state: st.session_state.unlock_non_today = False

# --- 側邊欄 ---
with st.sidebar:
    st.title("🏫 才藝班點名")
    if st.button("🔄 刷新雲端名單"):
        st.cache_data.clear()
        st.rerun()
    if st.button("🔄 刷新點名狀態"):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=5)
            st.session_state.done_list = r.json() if r.status_code == 200 else []
            st.toast("點名狀態已更新！")
        except: st.toast("連線失敗")
    st.divider()
    
    for day, classes in all_data.items():
        st.markdown(f"### {'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day
                # 每次換班級時，如果選的是今天，自動解鎖；如果是別天，則鎖定
                st.session_state.unlock_non_today = (day == current_day)

# --- 主畫面 ---
active_class = st.session_state.current_class
selected_day = st.session_state.current_day_sel

if not active_class:
    st.info("請點擊側邊欄選擇課程。")
else:
    # --- 安全鎖判斷 ---
    is_today = (selected_day == current_day)
    
    # 如果不是當天，且尚未點擊確認解鎖按鈕
    if not is_today and not st.session_state.unlock_non_today:
        st.markdown(f"""
            <div class="warning-box">
                <h2>⚠️ 非當天點名警告</h2>
                <p>您選擇的是 <b>{selected_day}</b> 的課程，但今天是 <b>{current_day}</b>。</p>
                <p>如果您是要補登舊紀錄，請點擊下方按鈕解鎖。</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔓 確認進行 {selected_day} 的補登", type="secondary", use_container_width=True):
            st.session_state.unlock_non_today = True
            st.rerun()
    else:
        # --- 正常點名流程 (原本 V33 修正重複 Key 的代碼) ---
        students = []
        for d in all_data:
            if active_class in all_data[d]:
                students = all_data[d][active_class]
                break
        
        # 標題加入星期顯示，避免混淆
        st.title(f"🍎 {active_class} ({selected_day})")
        
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("🙋‍♂️ 全員到校", use_container_width=True):
                for i, (cn, sn) in enumerate(students): 
                    st.session_state[f"s_{active_class}_{cn}_{sn}_{i}"] = "到校"
        with c_b:
            if st.button("🧹 重置選擇", use_container_width=True):
                for i, (cn, sn) in enumerate(students):
                    st.session_state[f"s_{active_class}_{cn}_{sn}_{i}"] = "到校"
        
        st.divider()
        status_results = {}
        for i, (class_name, name) in enumerate(students):
            unique_key = f"{active_class}_{class_name}_{name}_{i}"
            col1, col2, col3 = st.columns([3, 6, 1])
            with col1: 
                st.markdown(f"<div style='display: flex; align-items: center;'><div style='width: 60px; color: gray; font-size: 12px;'>{class_name}</div><div style='font-size: 24px; font-weight: bold;'>{name}</div></div>", unsafe_allow_html=True)
            with col2:
                res = st.radio("S", ["到校", "請假", "未到"], horizontal=True, key=f"s_{unique_key}", label_visibility="collapsed")
                status_results[unique_key] = (class_name, name, res)
            with col3:
                note = st.text_input("N", key=f"n_{unique_key}", label_visibility="collapsed", placeholder="原因") if res != "到校" else ""
                status_results[unique_key] += (note,)

        st.divider()
        if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
            # 注意：這裡的日期還是維持 today_str，若是補點名，建議手動修改 Excel 或在界面增加日期選擇
            payload = [{"date": today_str, "classroom": active_class, "lesson": val[0], "name": val[1], "status": val[2], "time": datetime.now().strftime("%H:%M:%S"), "note": val[3]} for val in status_results.values()]
            with st.spinner('同步中...'):
                try:
                    resp = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=15)
                    if resp.status_code == 200:
                        st.success("儲存成功！")
                        if active_class not in st.session_state.done_list: st.session_state.done_list.append(active_class)
                        time.sleep(1)
                        st.rerun()
                except: st.error("連線超時")

