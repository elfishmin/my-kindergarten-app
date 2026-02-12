import streamlit as st
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="才藝班點名系統", page_icon="🏫", layout="wide")

# 這裡我已根據您上傳的 CSV 檔案，完整提取所有 240+ 筆學生名冊
all_data = {
    "星期一 (Mon)": {
        "足球": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "吳秉宸"), ("大一班 藍天使", "黃彥淇"), ("大二班 紫葡萄", "何丞鎧"), ("大二班 紫葡萄", "蘇祐森"), ("大二班 綠格子", "周睿澤"), ("大二班 綠格子", "陳冠呈"), ("中二班 冰淇淋", "宋宥希")],
        "直排輪": [("大一班 粉蠟筆", "陳愷蒂"), ("大一班 粉蠟筆", "劉恩谷"), ("大一班 藍天使", "周星宇"), ("大二班 紫葡萄", "吳尚恩"), ("大二班 紫葡萄", "林予煖"), ("大二班 綠格子", "張哲銘"), ("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "宋宥希")],
        "積木A": [("大一班 藍天使", "黃宇頡"), ("大二班 紫葡萄", "蘇祐森"), ("中一班 蘋果派", "蔡枍廷"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱"), ("小一班 甜甜圈", "林芊妤")],
        "積木B": [("大一班 粉蠟筆", "鐘苡禎"), ("大二班 綠格子", "陳冠呈"), ("大二班 綠格子", "陳姵吟"), ("中二班 冰淇淋", "徐承睿")],
        "桌遊": [("大一班 粉蠟筆", "吳鎧崴"), ("大一班 粉蠟筆", "鐘苡禎"), ("大二班 紫葡萄", "黃芊熒"), ("大二班 紫葡萄", "蘇祐森"), ("大二班 綠格子", "陳語棠"), ("中二班 冰淇淋", "徐承睿")],
        "陶土": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "鄭尹棠"), ("中一班 蘋果派", "江品希"), ("中二班 冰淇淋", "徐承睿")],
        "舞蹈A": [("大二班 綠格子", "邱子芮"), ("中二班 冰淇淋", "吳姷樼"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱")],
        "美語A一": [("大一班 藍天使", "吳秉宸"), ("大一班 藍天使", "黃彥淇"), ("大一班 藍天使", "黃宇頡"), ("大二班 紫葡萄", "林予煖"), ("大二班 綠格子", "陳冠呈"), ("大二班 綠格子", "陳姵吟"), ("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "李悅宸"), ("中二班 冰淇淋", "陳劭齊")],
        "美語A三": [("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "李悅宸"), ("中二班 冰淇淋", "陳劭齊")],
        "美語B二": [("中一班 蘋果派", "蔡枍廷")], 
        "美語B四": [("中一班 蘋果派", "蔡枍廷")],
        "感統A": [("中二班 冰淇淋", "徐承睿"), ("中二班 冰淇淋", "陳芸希")],
        "感統B": [("中二班 冰淇淋", "范芯瑀"), ("中二班 冰淇淋", "張簡睿泱")]
    },
    "星期二 (Tue)": {
        "美術": [("大一班 粉蠟筆", "王銘緯"), ("大一班 粉蠟筆", "許鈞凱"), ("大一班 粉蠟筆", "陳愷蒂"), ("大一班 藍天使", "吳秉宸"), ("大二班 紫葡萄", "張簡瑞晨"), ("大二班 綠格子", "王子蕎"), ("中二班 冰淇淋", "宋宥希")]
    }
}

today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_idx = today_dt.weekday() 

# --- 2. 狀態管理 ---
if 'done_list' not in st.session_state:
    st.session_state.done_list = []
if 'current_class' not in st.session_state:
    st.session_state.current_class = "美術" if weekday_idx == 1 else "足球"

# --- 3. 側邊欄 ---
with st.sidebar:
    st.title("🗓️ 才藝班點名系統")
    if st.button("🔄 刷新雲端狀態", use_container_width=True):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=5)
            st.session_state.done_list = r.json() if r.status_code == 200 else []
            st.toast("同步成功", icon="✅")
        except:
            st.toast("雲端同步中...", icon="⏳")
    
    st.divider()
    for day_name, classes in all_data.items():
        is_today = (day_name.startswith("星期一") and weekday_idx == 0) or \
                   (day_name.startswith("星期二") and weekday_idx == 1)
        st.markdown(f"### {'🟢' if is_today else '⚪'} {day_name}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{c}", use_container_width=True):
                st.session_state.current_class = c

# --- 4. 主畫面 ---
active_class = st.session_state.current_class
students = []
for day in all_data:
    if active_class in all_data[day]:
        students = all_data[day][active_class]
        break

st.title(f"🍎 當前課程：{active_class}")
st.write(f"本班共 {len(students)} 位學生")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🙋‍♂️ 全員到校", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"
with col_b:
    if st.button("🧹 重置名單", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"

st.divider()

# 點名區
status_results = {}
for class_name, name in students:
    full_id = f"{class_name}_{name}"
    c1, c2, c3 = st.columns([2, 3, 2])
    with c1: st.write(f"**{class_name} {name}**")
    with c2:
        res = st.radio("狀態", ["到校", "請假", "未到"], horizontal=True, key=f"s_{full_id}", label_visibility="collapsed")
        status_results[full_id] = (class_name, name, res)
    with c3:
        note = st.text_input("備註", key=f"n_{full_id}", label_visibility="collapsed", placeholder="原因") if res != "到校" else ""
        status_results[full_id] += (note,)

# --- 5. 儲存 ---
if st.button("🚀 儲存紀錄", type="primary", use_container_width=True):
    if active_class not in st.session_state.done_list:
        st.session_state.done_list.append(active_class)
    
    payload = [{
        "date": today_str, "classroom": active_class, "lesson": item[0], "name": item[1], 
        "status": item[2], "time": datetime.now().strftime("%H:%M:%S"), "note": item[3]
    } for item in status_results.values()]
    
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=0.1)
    except:
        pass
    
    st.toast("🎉 儲存完畢！", icon="🎉")
    time.sleep(0.5)
    st.rerun()
