import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

st.set_page_config(page_title="才藝班點名系統 V34.1", page_icon="🏫", layout="wide")

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxTDHM3oNGMuRuKK_v8wVSM5-PWcGJfKRNMt6Sy4ClNqN280-r1oXZbRhePUD6RZ2LMVg/exec"

# --- 核心資料獲取 ---
@st.cache_data(ttl=60)
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=15)
        data = response.json()
        raw_students = data.get("students", [])
        raw_schedule = data.get("schedule", [])
        
        course_to_days = {}
        for row in raw_schedule:
            if len(row) < 2: continue
            day, course = str(row[0]).strip(), str(row[1]).replace(" ", "").strip()
            if course not in course_to_days: course_to_days[course] = []
            course_to_days[course].append(day)
            
        structured_data = {d: {} for d in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in raw_students:
            if len(row) < 3: continue
            c, s, sub = str(row[0]).strip(), str(row[1]).strip(), str(row[2]).replace(" ", "").strip()
            if sub in course_to_days:
                for day in course_to_days[sub]:
                    if day in structured_data:
                        if sub not in structured_data[day]: structured_data[day][sub] = []
                        structured_data[day][sub].append((c, s))
        return structured_data
    except: return {}

# --- 初始化時間與狀態 ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")

# 修正：精確對應星期，禮拜天(6)就該是禮拜天，不該跳到禮拜一
weekday_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
current_day = weekday_list[today_dt.weekday()]

if 'done_list' not in st.session_state: st.session_state.done_list = []
if 'current_class' not in st.session_state: st.session_state.current_class = ""
if 'current_day_sel' not in st.session_state: st.session_state.current_day_sel = ""
if 'unlock_confirm' not in st.session_state: st.session_state.unlock_confirm = False

# --- 側邊欄 ---
with st.sidebar:
    st.title("🏫 V34.1 穩定版")
    st.write(f"今天是：**{current_day}**") # 顯示正確日期供核對
    if st.button("🔄 刷新名單"): st.cache_data.clear(); st.rerun()
    
    st.divider()
    for day, classes in all_data.items():
        if not classes: continue
        # 修正：只有當「排程星期」完全等於「系統星期」時才亮🟢
        is_real_today = (day == current_day)
        st.subheader(f"{'🟢' if is_real_today else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day
                st.session_state.unlock_confirm = False # 切換班級時重新鎖定

# --- 主畫面 ---
if st.session_state.current_class:
    active_class = st.session_state.current_class
    selected_day = st.session_state.current_day_sel
    
    # 功能 1：非當天點名警告
    if selected_day != current_day and not st.session_state.unlock_confirm:
        st.warning(f"⚠️ 您正在查看 **{selected_day}** 的課程，但今天是 **{current_day}**。")
        if st.button(f"🔓 我確認要補登 {selected_day} 的紀錄"):
            st.session_state.unlock_confirm = True
            st.rerun()
    else:
        # 點名介面
        st.title(f"🍎 {active_class} ({selected_day})")
        students = all_data.get(selected_day, {}).get(active_class, [])
        
        # 快捷鍵
        if st.button("🙋‍♂️ 全員到校", use_container_width=True):
            for i, (cn, sn) in enumerate(students): st.session_state[f"r_{active_class}_{sn}"] = "到校"
        
        st.divider()
        results = {}
        for i, (cn, sn) in enumerate(students):
            key = f"r_{active_class}_{sn}"
            c1, c2, c3 = st.columns([2, 5, 2])
            with c1: st.write(f"**{cn}**\n### {sn}")
            with c2: res = st.radio("S", ["到校", "請假", "未到"], key=key, horizontal=True, label_visibility="collapsed")
            with c3: note = st.text_input("備註", key=f"n_{key}", label_visibility="collapsed") if res != "到校" else ""
            results[i] = {"class_name": cn, "name": sn, "status": res, "note": note}

        if st.button("🚀 儲存至雲端", type="primary", use_container_width=True):
            payload = [{"date": today_str, "classroom": v["class_name"], "lesson": active_class, "name": v["name"], "status": v["status"], "time": datetime.now().strftime("%H:%M:%S"), "note": v["note"]} for v in results.values()]
            try:
                resp = requests.post(SCRIPT_URL, data=json.dumps(payload))
                if resp.status_code == 200:
                    st.success("儲存成功！")
                    time.sleep(1); st.rerun()
            except: st.error("儲存失敗")
else:
    st.info("請選擇左側課程")
