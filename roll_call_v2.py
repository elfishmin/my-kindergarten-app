import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 參數設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="極速點名系統", page_icon="⚡", layout="wide")

# 初始化本地緩存，減少網路讀取次數
if 'cloud_done' not in st.session_state:
    st.session_state.cloud_done = []
if 'last_sync' not in st.session_state:
    st.session_state.last_sync = datetime.min

# 2. 原始名單 (這裡保持你的名單結構)
raw_data = {
    "美術": [("大一班 粉蠟筆", "王銘緯"), ("大一班 粉蠟筆", "許鈞凱"), ("大一班 粉蠟筆", "陳愷蒂"), ("大一班 藍天使", "吳秉宸"), ("大二班 紫葡萄", "張簡瑞晨"), ("大二班 綠格子", "王子蕎"), ("中二班 冰淇淋", "宋宥希")],
    "直排輪": [("大一班 粉蠟筆", "陳愷蒂"), ("大一班 粉蠟筆", "劉恩谷"), ("大一班 藍天使", "周星宇"), ("大二班 紫葡萄", "吳尚恩"), ("大二班 紫葡萄", "林予煖"), ("大二班 綠格子", "張哲銘"), ("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "宋宥希")],
    "足球": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "吳秉宸"), ("大一班 藍天使", "黃彥淇"), ("中二班 冰淇淋", "宋宥希")],
    "桌遊": [("大一班 粉蠟筆", "吳鎧崴"), ("大一班 粉蠟筆", "鐘苡禎"), ("大二班 紫葡萄", "黃芊熒"), ("大二班 紫葡萄", "蘇祐森"), ("大二班 綠格子", "陳語棠"), ("中二班 冰淇淋", "徐承睿")],
    "陶土": [("大一班 粉蠟筆", "謝恩典"), ("大一班 藍天使", "鄭尹棠"), ("中二班 冰淇淋", "徐承睿")],
    "積木A": [("大一班 藍天使", "黃宇頡"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱")],
    "積木B": [("大二班 綠格子", "陳冠呈"), ("大二班 綠格子", "陳姵吟"), ("中二班 冰淇淋", "徐承睿")],
    "舞蹈A": [("大二班 綠格子", "邱子芮"), ("中二班 冰淇淋", "吳姷樼"), ("中二班 冰淇淋", "宋宥希"), ("中二班 冰淇淋", "張簡睿泱")],
    "美語A一": [("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "李悅宸"), ("中二班 冰淇淋", "陳劭齊")],
    "感統A": [("中二班 冰淇淋", "徐承睿"), ("中二班 冰淇淋", "陳芸希")],
    "感統B": [("中二班 冰淇淋", "范芯瑀"), ("中二班 冰淇淋", "張簡睿泱")]
}

today = datetime.now().strftime("%Y-%m-%d")

# --- 3. 同步函數 (手動觸發) ---
def sync_with_cloud():
    try:
        resp = requests.get(f"{SCRIPT_URL}?date={today}", timeout=3)
        if resp.status_code == 200:
            st.session_state.cloud_done = resp.json()
            st.session_state.last_sync = datetime.now()
    except:
        pass # 失敗時保持舊有狀態，不卡死介面

# 初次進入或每隔 5 分鐘自動背景同步一次
if (datetime.now() - st.session_state.last_sync).total_seconds() > 300:
    sync_with_cloud()

# --- 4. 側邊欄 ---
st.sidebar.button("🔄 同步狀態", on_click=sync_with_cloud, use_container_width=True)

# 建立顯示標籤
display_options = {}
for c in raw_data.keys():
    icon = "✅" if c in st.session_state.cloud_done else "⚪"
    display_options[f"{icon} {c}"] = c

selected_label = st.sidebar.radio("課程列表", list(display_options.keys()))
classroom = display_options[selected_label]

st.title(f"🍎 {classroom}")
st.divider()

# --- 5. 點名介面 (優化渲染) ---
status_dict = {}
reason_dict = {}
for class_name, name in raw_data[classroom]:
    full_name = f"{class_name} {name}"
    c1, c2, c3 = st.columns([1.5, 3, 2])
    with c1: st.write(f"**{full_name}**")
    with c2:
        res = st.radio(f"S-{full_name}", ["到校", "請假", "未到"], horizontal=True, key=f"s_{classroom}_{full_name}", label_visibility="collapsed")
        status_dict[full_name] = (class_name, name, res)
    with c3:
        if res != "到校":
            reason_dict[full_name] = st.text_input(f"R-{full_name}", placeholder="原因", key=f"r_{classroom}_{full_name}", label_visibility="collapsed")
        else:
            reason_dict[full_name] = ""

# --- 6. 樂觀提交 ---
if st.button(f"🚀 確認提交【{classroom}】", type="primary", use_container_width=True):
    # 樂觀更新：先在手機上顯示點名成功，背景再慢慢傳資料
    if classroom not in st.session_state.cloud_done:
        st.session_state.cloud_done.append(classroom)
    
    with st.spinner('同步中...'):
        payload = [{
            "date": today, "classroom": classroom, "lesson": c, "name": n, "status": s, "time": datetime.now().strftime("%H:%M:%S"), "note": reason_dict.get(f"{c} {n}", "")
        } for c, n, s in status_dict.values()]
        
        try:
            r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=5)
            if r.status_code == 200:
                st.success("儲存成功！")
                st.balloons()
            else: st.error("寫入超時，請檢查網路")
        except:
            st.error("網路異常，請稍後重試")
    st.rerun()
