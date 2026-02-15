import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# 設定頁面
st.set_page_config(page_title="才藝班點名系統 V34.2", page_icon="🏫", layout="wide")

# 核心設定
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

# --- 初始化狀態 ---
all_data = fetch_cloud_data()
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")

# 修正亮燈邏輯：定義標準星期清單
weekday_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
current_day = weekday_list[today_dt.weekday()]

# 初始化 session_state
if 'done_list' not in st.session_state: st.session_state.done_list = []
if 'current_class' not in st.session_state: st.session_state.current_class = ""
if 'current_day_sel' not in st.session_state: st.session_state.current_day_sel = ""
if 'unlock_confirm' not in st.session_state: st.session_state.unlock_confirm = False

# --- 側邊欄：功能與選單 ---
with st.sidebar:
    st.title("🏫 才藝點名系統")
    st.info(f"📅 今天是：{current_day}")
    
    # 功能：刷新點名狀態 (抓取當天已點名班級)
    if st.button("🔄 刷新今日點名狀態", use_container_width=True):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=10)
            if r.status_code == 200:
                st.session_state.done_list = r.json()
                st.toast("狀態已更新！")
            else: st.error("連線失敗")
        except: st.error("網路連線超時")

    if st.button("♻️ 刷新名單 (同步雲端)", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    
    # 側邊欄列表與亮燈
    for day, classes in all_data.items():
        if not classes: continue
        is_real_today = (day == current_day)
        st.subheader(f"{'🟢' if is_real_today else '⚪'} {day}")
        for c in classes.keys():
            # ✅ 檢查是否在已完成清單中
            is_done = c in st.session_state.done_list
            icon = "✅" if is_done else "📝"
            if st.button(f"{icon} {c}", key=f"{day}_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.current_day_sel = day
                st.session_state.unlock_confirm = False # 重置補登解鎖狀態

# --- 主畫面 ---
if st.session_state.current_class:
    active_class = st.session_state.current_class
    selected_day = st.session_state.current_day_sel
    
    # 功能：非當天點名警告
    is_today = (selected_day == current_day)
    if not is_today and not st.session_state.unlock_confirm:
        st.warning(f"### ⚠️ 非當天點名警告\n您選擇的是 **{selected_day}** 的課程，但今天是 **{current_day}**。")
        if st.button(f"🔓 我確認要補登 {selected_day} 的點名紀錄", use_container_width=True):
            st.session_state.unlock_confirm = True
            st.rerun()
    else:
        # 顯示點名介面
        st.title(f"🍎 {active_class} ({selected_day})")
        students = all_data.get(selected_day, {}).get(active_class, [])
        
        # 快捷鍵
        if st.button("🙋‍♂️ 全員到校", use_container_width=True):
            for i, (cn, sn) in enumerate(students):
                st.session_state[f"r_{active_class}_{sn}"] = "到校"
        
        st.divider()
        
        # 學生列表
        results = {}
        for i, (cn, sn) in enumerate(students):
            key = f"r_{active_class}_{sn}"
            c1, c2, c3 = st.columns([2, 5, 2])
            with c1: 
                st.markdown(f"**{cn}**\n### {sn}")
            with c2:
                res = st.radio("S", ["到校", "請假", "未到"], key=key, horizontal=True, label_visibility="collapsed")
            with c3:
                note = st.text_input("備註", key=f"n_{key}", placeholder="原因", label_visibility="collapsed") if res != "到校" else ""
            results[i] = {"class_name": cn, "name": sn, "status": res, "note": note}

        # 儲存按鈕
        if st.button("🚀 儲存至雲端 (自動更新)", type="primary", use_container_width=True):
            payload = [{"date": today_str, "classroom": v["class_name"], "lesson": active_class, "name": v["name"], "status": v["status"], "time": datetime.now().strftime("%H:%M:%S"), "note": v["note"]} for v in results.values()]
            with st.spinner("資料同步中..."):
                try:
                    resp = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=15)
                    if resp.status_code == 200:
                        st.success("儲存完成！")
                        # 儲存後立即更新勾選狀態
                        if active_class not in st.session_state.done_list:
                            st.session_state.done_list.append(active_class)
                        time.sleep(1)
                        st.rerun()
                except:
                    st.error("連線錯誤，請檢查網路。")
else:
    st.info("💡 請從左側選單選擇一個課程來開始點名。")
