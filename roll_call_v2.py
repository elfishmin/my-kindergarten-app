import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

st.set_page_config(page_title="才藝班點名系統 V34", page_icon="🏫", layout="wide")

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxTDHM3oNGMuRuKK_v8wVSM5-PWcGJfKRNMt6Sy4ClNqN280-r1oXZbRhePUD6RZ2LMVg/exec"

@st.cache_data(ttl=60)
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=15)
        data = response.json()
        raw_students, raw_schedule = data.get("students", []), data.get("schedule", [])
        
        course_to_days = {}
        for row in raw_schedule:
            if len(row) < 2: continue
            day, course = str(row[0]).strip(), str(row[1]).replace(" ", "").strip()
            if course not in course_to_days: course_to_days[course] = []
            course_to_days[course].append(day)
            
        structured_data = {d: {} for d in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in raw_students:
            if len(row) < 3: continue
            # 這裡把 班別(c_name), 姓名(s_name), 課程(sub) 都抓完整
            c_name, s_name, sub = str(row[0]).strip(), str(row[1]).strip(), str(row[2]).replace(" ", "").strip()
            if sub in course_to_days:
                for day in course_to_days[sub]:
                    if day in structured_data:
                        if sub not in structured_data[day]: structured_data[day][sub] = []
                        structured_data[day][sub].append((c_name, s_name))
        return structured_data
    except: return {}

all_data = fetch_cloud_data()
today_str = datetime.now().strftime("%Y-%m-%d")
current_day = {0:"星期一",1:"星期二",2:"星期三",3:"星期四",4:"星期五"}.get(datetime.now().weekday(), "星期一")

if 'done_list' not in st.session_state: st.session_state.done_list = []
if 'current_class' not in st.session_state: st.session_state.current_class = ""

with st.sidebar:
    st.title("🏫 V34 穩定版")
    if st.button("🔄 刷新名單"): st.cache_data.clear(); st.rerun()
    if st.button("🔄 刷新今日點名狀態"):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}")
            st.session_state.done_list = r.json()
            st.toast("狀態已更新")
        except: pass
    st.divider()
    for day, classes in all_data.items():
        if not classes: continue
        st.subheader(f"{'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day

if st.session_state.current_class:
    active_class = st.session_state.current_class
    st.title(f"🍎 {active_class}")
    students = all_data.get(st.session_state.current_day_sel, {}).get(active_class, [])
    
    # 快捷鍵按鈕
    if st.button("🙋‍♂️ 全員到校", use_container_width=True):
        for i, (cn, sn) in enumerate(students): st.session_state[f"r_{active_class}_{sn}"] = "到校"
    
    st.divider()
    results = {}
    for i, (cn, sn) in enumerate(students):
        key = f"r_{active_class}_{sn}"
        c1, c2, c3 = st.columns([2, 5, 2])
        with c1: st.write(f"**{cn}**\n### {sn}") # 這裡會顯示班別
        with c2: res = st.radio("S", ["到校", "請假", "未到"], key=key, horizontal=True, label_visibility="collapsed")
        with c3: note = st.text_input("備註", key=f"n_{key}", placeholder="原因", label_visibility="collapsed") if res != "到校" else ""
        results[i] = {"class_name": cn, "name": sn, "status": res, "note": note}

    if st.button("🚀 儲存至雲端 (更新不累加)", type="primary", use_container_width=True):
        # 這裡的 payload 增加了 classroom_real (班別) 和 lesson_real (課堂)
        payload = [{"date": today_str, "classroom": v["class_name"], "lesson": active_class, "name": v["name"], "status": v["status"], "time": datetime.now().strftime("%H:%M:%S"), "note": v["note"]} for v in results.values()]
        try:
            resp = requests.post(SCRIPT_URL, data=json.dumps(payload))
            if resp.status_code == 200:
                st.success("儲存完成！重複資料已自動覆蓋。")
                if active_class not in st.session_state.done_list: st.session_state.done_list.append(active_class)
                time.sleep(1); st.rerun()
        except: st.error("儲存失敗")
