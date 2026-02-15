import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# 必須放在最前面
st.set_page_config(page_title="才藝班點名系統 V35", page_icon="🏫", layout="wide")

# 核心設定
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxTDHM3oNGMuRuKK_v8wVSM5-PWcGJfKRNMt6Sy4ClNqN280-r1oXZbRhePUD6RZ2LMVg/exec"

st.markdown("""
    <style>
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

# --- 核心資料獲取：精準去空格 (A/B 不可忽略) ---
@st.cache_data(ttl=60)
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=15)
        data = response.json()
        raw_students = data.get("students", [])
        raw_schedule = data.get("schedule", [])
        
        # 處理排程：刪除名稱內所有空格
        course_to_days = {}
        for row in raw_schedule:
            if len(row) < 2: continue
            day = str(row[0]).replace(" ", "").strip()
            course = str(row[1]).replace(" ", "").strip()
            if course not in course_to_days:
                course_to_days[course] = []
            course_to_days[course].append(day)
            
        structured_data = {d: {} for d in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in raw_students:
            if len(row) < 3: continue
            class_name = str(row[0]).strip()
            student_name = str(row[1]).strip()
            subject = str(row[2]).replace(" ", "").strip()
            
            if subject in course_to_days:
                for day in course_to_days[subject]:
                    if day in structured_data:
                        if subject not in structured_data[day]:
                            structured_data[day][subject] = []
                        structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return {}

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
    st.title("🏫 才藝點名 V35")
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
        if not classes: continue
        is_real_today = (day == current_day)
        st.subheader(f"{'🟢' if is_real_today else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day
                st.session_state.unlock_non_today = (day == current_day)

# --- 主畫面邏輯：解鎖後顯示點名表 ---
active_class = st.session_state.current_class
selected_day = st.session_state.current_day_sel

if active_class:
    is_today = (selected_day == current_day)
    
    # 顯示警告鎖：如果不是今天且尚未點擊解鎖
    if not is_today and not st.session_state.unlock_non_today:
        st.markdown(f"""
            <div class="warning-box">
                <h2>⚠️ 非當天點名警告</h2>
                <p>您選擇的是 <b>{selected_day}</b> 的課程，但今天是 <b>{current_day}</b>。</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔓 確認補登 {selected_day} 紀錄", use_container_width=True):
            st.session_state.unlock_non_today = True
            st.rerun()
    else:
        # --- 點名介面開始 (解鎖後或當天課程都會進到這裡) ---
        st.title(f"🍎 {active_class} ({selected_day})")
        students = all_data.get(selected_day, {}).get(active_class, [])
        
        # 快捷鍵
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🙋‍♂️ 全員到校", use_container_width=True):
                for i, (cn, sn) in enumerate(students):
                    st.session_state[f"r_{active_class}_{sn}_{i}"] = "到校"
        with c2:
            if st.button("🧹 重置選擇", use_container_width=True):
                for i, (cn, sn) in enumerate(students):
                    st.session_state[f"r_{active_class}_{sn}_{i}"] = "到校"

        st.divider()
        
        status_results = {}
        for i, (cn, sn) in enumerate(students):
            key = f"r_{active_class}_{sn}_{i}"
            col1, col2, col3 = st.columns([2, 5, 2])
            with col1: st.markdown(f"**{cn}**\n### {sn}")
            with col2:
                # 這裡就是您說不見的選項！現在移到 else 區塊確保一定顯示
                res = st.radio("S", ["到校", "請假", "未到"], key=key, horizontal=True, label_visibility="collapsed")
            with col3:
                note = st.text_input("備註", key=f"n_{key}", label_visibility="collapsed", placeholder="原因") if res != "到校" else ""
            status_results[i] = {"class": cn, "name": sn, "status": res, "note": note}

        st.divider()
        if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
            payload = [{"date": today_str, "classroom": active_class, "lesson": v["class"], "name": v["name"], "status": v["status"], "time": datetime.now().strftime("%H:%M:%S"), "note": v["note"]} for v in status_results.values()]
            with st.spinner('同步中...'):
                try:
                    resp = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=15)
                    if resp.status_code == 200:
                        st.success("儲存成功！")
                        if active_class not in st.session_state.done_list:
                            st.session_state.done_list.append(active_class)
                        time.sleep(1)
                        st.rerun()
                except: st.error("連線超時")
else:
    st.info("💡 請從左側選單選擇課程。")

