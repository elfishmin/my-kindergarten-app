import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 基本設定 (已填入您的 URL)
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="極速點名系統", page_icon="⚡", layout="wide")

# 完整名單資料 (根據您的 CSV 提取)
raw_data = {
    "美術": [("大一班 粉蠟筆", "王銘緯"), ("大一班 粉蠟筆", "許鈞凱"), ("大一班 粉蠟筆", "陳愷蒂"), ("大一班 藍天使", "吳秉宸"), ("大二班 紫葡萄", "張簡瑞晨"), ("大二班 綠格子", "王子蕎"), ("中二班 冰淇淋", "宋宥希")],
    "桌遊": [("大一班 粉蠟筆", "吳鎧崴"), ("大一班 粉蠟筆", "鐘苡禎"), ("大二班 紫葡萄", "黃芊熒"), ("大二班 紫葡萄", "蘇祐森"), ("大二班 綠格子", "陳語棠"), ("中二班 冰淇淋", "徐承睿")],
    "陶土": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "鄭尹棠"), ("中二班 冰淇淋", "徐承睿")],
    "足球": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "吳秉宸"), ("大一班 藍天使", "黃彥淇"), ("中二班 冰淇淋", "宋宥希")],
    "直排輪": [("大一班 粉蠟筆", "陳愷蒂"), ("大一班 粉蠟筆", "劉恩谷"), ("大一班 藍天使", "周星宇"), ("大二班 紫葡萄", "吳尚恩"), ("大二班 紫葡萄", "林予煖"), ("大二班 綠格子", "張哲銘"), ("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "宋宥希")],
    "積木A": [("大一班 藍天使", "黃宇頡"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱")],
    "積木B": [("大二班 綠格子", "陳冠呈"), ("大二班 綠格子", "陳姵吟"), ("中二班 冰淇淋", "徐承睿")],
    "舞蹈A": [("大二班 綠格子", "邱子芮"), ("中二班 冰淇淋", "吳姷樼"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱")],
    "美語A一": [("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "李悅宸"), ("中二班 冰淇淋", "陳劭齊")],
    "美語A三": [("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "李悅宸"), ("中二班 冰淇淋", "陳劭齊")],
    "感統A": [("中二班 冰淇淋", "徐承睿"), ("中二班 冰淇淋", "陳芸希")],
    "感統B": [("中二班 冰淇淋", "范芯瑀"), ("中二班 冰淇淋", "張簡睿泱")],
    "美語B四": [("大二班 綠格子", "蔡枍廷")]
}

today = datetime.now().strftime("%Y-%m-%d")

# --- 2. 狀態管理 (Session State) ---
# 確保變數名稱統一為 done_list
if 'done_list' not in st.session_state:
    st.session_state.done_list = []

# 同步函數
def force_sync():
    try:
        r = requests.get(f"{SCRIPT_URL}?date={today}", timeout=3)
        if r.status_code == 200:
            st.session_state.done_list = r.json()
            st.toast("已同步最新進度", icon="☁️")
    except:
        st.toast("同步超時，請檢查網路", icon="⚠️")

# --- 3. 側邊欄 ---
with st.sidebar:
    st.title("🎨 才藝班點名")
    st.button("🔄 同步雲端狀態", on_click=force_sync, use_container_width=True)
    st.write("")
    
    display_options = []
    class_map = {}
    
    for c in raw_data.keys():
        # 修正這裡的變數名稱為 done_list
        label = f"{c} ✅" if c in st.session_state.done_list else c
        display_options.append(label)
        class_map[label] = c
    
    selected_label = st.radio("課程清單", display_options, key="nav_radio", label_visibility="collapsed")
    current_class = class_map[selected_label]

# --- 4. 主畫面 ---
st.title(f"🍎 {current_class}")
if current_class in st.session_state.done_list:
    st.success(f"此班級今日已點名完成")

st.divider()

status_dict = {}
reason_dict = {}
students = raw_data[current_class]

for class_name, name in students:
    full_id = f"{class_name} {name}"
    c1, c2, c3 = st.columns([1.5, 3, 2])
    with c1: st.markdown(f"**{full_id}**")
    with c2:
        res = st.radio("狀態", ["到校", "請假", "未到"], horizontal=True, key=f"s_{full_id}", label_visibility="collapsed")
        status_dict[full_id] = (class_name, name, res)
    with c3:
        if res != "到校":
            reason_dict[full_id] = st.text_input("原因", key=f"r_{full_id}", label_visibility="collapsed", placeholder="原因")
        else: reason_dict[full_id] = ""

# --- 5. 送出邏輯 ---
if st.button("🚀 儲存紀錄", type="primary", use_container_width=True):
    # 樂觀更新勾勾
    if current_class not in st.session_state.done_list:
        st.session_state.done_list.append(current_class)
    
    payload = [{
        "date": today, "classroom": current_class, "lesson": cn, "name": sn, "status": s, "time": datetime.now().strftime("%H:%M:%S"), "note": reason_dict.get(f"{cn} {sn}", "")
    } for cn, sn, s in status_dict.values()]
    
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=5)
        st.toast(f"✅ {current_class} 已同步", icon='🎉')
        st.rerun() # 點完立即重繪以顯示左側勾勾
    except:
        st.error("網路異常，資料可能未送出")
