import streamlit as st
from datetime import datetime
import requests
import json

# ==========================================
# 1. 核心設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="才藝班點名系統", page_icon="🏫", layout="wide")

# 完整學生名單 (對應 2025 課表)
all_data = {
    "星期一 (Mon)": {
        "足球": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "吳秉宸"), ("大一班 藍天使", "黃彥淇"), ("中二班 冰淇淋", "宋宥希")],
        "直排輪": [("大一班 粉蠟筆", "陳愷蒂"), ("大一班 粉蠟筆", "劉恩谷"), ("大一班 藍天使", "周星宇"), ("大二班 紫葡萄", "吳尚恩"), ("大二班 紫葡萄", "林予煖"), ("大二班 綠格子", "張哲銘"), ("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "宋宥希")],
        "積木B": [("大二班 綠格子", "陳冠呈"), ("大二班 綠格子", "陳姵吟"), ("中二班 冰淇淋", "徐承睿")],
        "桌遊": [("大一班 粉蠟筆", "吳鎧崴"), ("大一班 粉蠟筆", "鐘苡禎"), ("大二班 紫葡萄", "黃芊熒"), ("大二班 紫葡萄", "蘇祐森"), ("大二班 綠格子", "陳語棠"), ("中二班 冰淇淋", "徐承睿")],
        "陶土": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "鄭尹棠"), ("中二班 冰淇淋", "徐承睿")],
        "美語A一": [("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "李悅宸"), ("中二班 冰淇淋", "陳劭齊")],
        "美語A三": [("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "李悅宸"), ("中二班 冰淇淋", "陳劭齊")],
        "美語B二": [("中一班 蘋果派", "蔡枍廷")], # 根據原始名冊補充
        "美語B四": [("大二班 綠格子", "蔡枍廷")]
    },
    "星期二 (Tue)": {
        "美術": [("大一班 粉蠟筆", "王銘緯"), ("大一班 粉蠟筆", "許鈞凱"), ("大一班 粉蠟筆", "陳愷蒂"), ("大一班 藍天使", "吳秉宸"), ("大二班 紫葡萄", "張簡瑞晨"), ("大二班 綠格子", "王子蕎"), ("中二班 冰淇淋", "宋宥希")]
    },
    "其他課程": {
        "積木A": [("大一班 藍天使", "黃宇頡"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱")],
        "舞蹈A": [("大二班 綠格子", "邱子芮"), ("中二班 冰淇淋", "吳姷樼"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱")],
        "感統A": [("中二班 冰淇淋", "徐承睿"), ("中二班 冰淇淋", "陳芸希")],
        "感統B": [("中二班 冰淇淋", "范芯瑀"), ("中二班 冰淇淋", "張簡睿泱")]
    }
}

# 取得今天日期與星期
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_idx = today_dt.weekday() # 0=Mon, 1=Tue...

# --- 2. 狀態管理 ---
if 'done_list' not in st.session_state:
    st.session_state.done_list = []
if 'current_class' not in st.session_state:
    # 預設顯示：週一顯示足球，週二顯示美術
    st.session_state.current_class = "美術" if weekday_idx == 1 else "足球"

# 同步函數
def sync_data():
    try:
        r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=10)
        st.session_state.done_list = r.json() if r.status_code == 200 else []
    except: pass

# --- 3. 側邊欄：分組顯示 ---
with st.sidebar:
    st.title("🗓️ 才藝班課表")
    if st.button("🔄 刷新雲端狀態", use_container_width=True):
        sync_data()
    
    st.divider()
    
    for day_name, classes in all_data.items():
        # 標記今日
        is_today = (day_name == "星期一 (Mon)" and weekday_idx == 0) or \
                   (day_name == "星期二 (Tue)" and weekday_idx == 1)
        header = f"📍 {day_name}" + (" (今日)" if is_today else "")
        st.subheader(header)
        
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "⚪"
            if st.button(f"{icon} {c}", key=f"btn_{c}", use_container_width=True):
                st.session_state.current_class = c
    st.write("")

# --- 4. 主畫面：小朋友名單 ---
current_class = st.session_state.current_class
# 找到該班級所屬的星期分組
target_day = next((day for day, cls in all_data.items() if current_class in cls), "其他課程")
students = all_data[target_day][current_class]

st.title(f"🍎 {current_class} 點名表")
if current_class in st.session_state.done_list:
    st.success("今日已完成點名")

# 功能鈕
col_a, col_b = st.columns(2)
with col_a:
    if st.button("🙋‍♂️ 全員到校", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn} {sn}"] = "到校"
with col_b:
    if st.button("🔄 重設名單", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn} {sn}"] = "到校" # 或清空

st.divider()

# 渲染學生名單
status_results = {}
for class_name, name in students:
    full_id = f"{class_name} {name}"
    c1, c2, c3 = st.columns([2, 3, 2])
    with c1: st.write(f"**{full_id}**")
    with c2:
        res = st.radio("狀態", ["到校", "請假", "未到"], horizontal=True, 
                       key=f"s_{full_id}", label_visibility="collapsed")
        status_results[full_id] = (class_name, name, res)
    with c3:
        note = st.text_input("備註", key=f"n_{full_id}", label_visibility="collapsed", placeholder="原因") if res != "到校" else ""
        status_results[full_id] += (note,)

# --- 5. 儲存 ---
if st.button("🚀 儲存並同步 Excel", type="primary", use_container_width=True):
    payload = [{
        "date": today_str, "classroom": current_class, "lesson": item[0], "name": item[1], 
        "status": item[2], "time": datetime.now().strftime("%H:%M:%S"), "note": item[3]
    } for item in status_results.values()]
    
    try:
        with st.status("正在連線 Google Excel...", expanded=False):
            r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=15)
            if r.status_code == 200:
                if current_class not in st.session_state.done_list:
                    st.session_state.done_list.append(current_class)
                st.toast("儲存成功！")
                st.rerun()
    except:
        st.error("傳送超時，請檢查網路")
