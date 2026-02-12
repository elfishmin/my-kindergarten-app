import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 基本設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="極速點名", page_icon="⚡", layout="wide")

# 這裡放入你提供的完整 raw_data 名單... (保持不變)
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
if 'done_list' not in st.session_state:
    st.session_state.done_list = []

# 強制刷新函數 (只有按按鈕才觸發)
def force_sync():
    try:
        r = requests.get(f"{SCRIPT_URL}?date={today}", timeout=3)
        st.session_state.done_list = r.json()
    except: pass

# --- 3. 側邊欄 ---
with st.sidebar:
    st.title(" 才藝班")
    if st.button("🔄 同步進度", use_container_width=True):
        force_sync()
    
    # 建立純文字選項清單，減少圖示計算
    choice = st.radio("課程清單", list(raw_data.keys()), key="nav")
    
    # 顯示已完成標籤
    st.markdown("---")
    st.caption("今日已完成：")
    for d in st.session_state.done_list:
        st.write(f"✅ {d}")

# --- 4. 主畫面 (極簡化渲染) ---
classroom = st.session_state.nav
st.title(f"🍎 {classroom}")

# 點名介面
status_dict = {}
reason_dict = {}
students = raw_data[classroom]

# 使用 container 包裹提升渲染穩定性
with st.container():
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
    # 立即反映在本地，不等待 API
    if classroom not in st.session_state.done_list:
        st.session_state.done_list.append(classroom)
    
    payload = [{
        "date": today, "classroom": classroom, "lesson": cn, "name": sn, "status": s, "time": datetime.now().strftime("%H:%M:%S"), "note": reason_dict.get(f"{cn} {sn}", "")
    } for cn, sn, s in status_dict.values()]
    
    try:
        # 使用快速請求，不卡死主執行緒
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=5)
        st.toast("✅ 資料已傳送至雲端", icon='🎉')
    except:
        st.error("傳送失敗，請檢查網路")
