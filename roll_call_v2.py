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
CSV_FILE = "2-1_總才藝班上課日期.xlsx - Sheet1.csv"

st.set_page_config(page_title="才藝班點名系統", page_icon="🏫", layout="wide")

# 加載全校名單 (240 列全自動讀取)
@st.cache_data
def load_full_roster():
    try:
        # 讀取 CSV，根據您的檔案格式跳過前兩行標頭
        df = pd.read_csv(CSV_FILE, skiprows=2)
        # 強制命名欄位，確保對應正確
        df.columns = ["班級", "姓名", "星期", "課程"]
        # 移除空白行並清理字串
        df = df.dropna(subset=["姓名", "課程"])
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"讀取名冊失敗，請確認檔案 {CSV_FILE} 是否存在。錯誤: {e}")
        return pd.DataFrame()

df_roster = load_full_roster()

# 建立自動分組
full_schedule = {}
if not df_roster.empty:
    for _, row in df_roster.iterrows():
        day = row["星期"]
        course = row["課程"]
        if day not in full_schedule:
            full_schedule[day] = {}
        if course not in full_schedule[day]:
            full_schedule[day][course] = []
        full_schedule[day][course].append((row["班級"], row["姓名"]))

# 時間設定
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五"}
current_weekday = weekday_map.get(today_dt.weekday(), "星期一")

# --- 2. 狀態管理 ---
if 'done_list' not in st.session_state:
    st.session_state.done_list = []
if 'current_class' not in st.session_state:
    # 預設自動顯示今天的課程，如果今天沒課，就顯示第一個星期的第一門課
    default_day = current_weekday if current_weekday in full_schedule else list(full_schedule.keys())[0]
    st.session_state.current_class = list(full_schedule[default_day].keys())[0]

# --- 3. 側邊欄：依星期分組顯示所有課程 ---
with st.sidebar:
    st.title("🗓️ 全校才藝班名冊")
    if st.button("🔄 刷新雲端狀態", use_container_width=True):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=5)
            st.session_state.done_list = r.json() if r.status_code == 200 else []
        except: st.toast("雲端同步中...")
    
    st.divider()
    # 排序：一、二、三、四、五
    sorted_days = ["星期一", "星期二", "星期三", "星期四", "星期五"]
    for day in sorted_days:
        if day in full_schedule:
            is_today = (day == current_weekday)
            st.markdown(f"### {'🟢' if is_today else '⚪'} {day}")
            for course in full_schedule[day].keys():
                icon = "✅" if course in st.session_state.done_list else "📝"
                if st.button(f"{icon} {course}", key=f"btn_{day}_{course}", use_container_width=True):
                    st.session_state.current_class = course

# --- 4. 主畫面 ---
target_course = st.session_state.current_class
# 從資料庫撈出該班級學生
students = []
for d in full_schedule:
    if target_course in full_schedule[d]:
        students = full_schedule[d][target_course]
        break

st.title(f"🍎 當前點名：{target_course}")
st.info(f"本班共有 {len(students)} 位學生")

# 快速按鈕
col_a, col_b = st.columns(2)
with col_a:
    if st.button("🙋‍♂️ 全員到校", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"
with col_b:
    if st.button("🧹 重置名單", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"

st.divider()

# 點名表單
status_results = {}
for class_name, name in students:
    student_id = f"{class_name}_{name}"
    c1, c2, c3 = st.columns([2, 3, 2])
    with c1: st.write(f"**{class_name} {name}**")
    with c2:
        res = st.radio("狀態", ["到校", "請假", "未到"], horizontal=True, key=f"s_{student_id}", label_visibility="collapsed")
        status_results[student_id] = (class_name, name, res)
    with c3:
        note = st.text_input("備註", key=f"n_{student_id}", label_visibility="collapsed", placeholder="原因") if res != "到校" else ""
        status_results[student_id] += (note,)

# --- 5. 儲存 ---
if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
    if target_course not in st.session_state.done_list:
        st.session_state.done_list.append(target_course)
    
    payload = [{
        "date": today_str, "classroom": target_course, "lesson": item[0], "name": item[1], 
        "status": item[2], "time": datetime.now().strftime("%H:%M:%S"), "note": item[3]
    } for item in status_results.values()]
    
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=0.1)
    except: pass
    
    st.toast(f"🎉 {target_course} 點名資料已發送！", icon="🎉")
    time.sleep(0.5)
    st.rerun()
