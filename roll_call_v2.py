import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 參數設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="幼稚園才藝點名", page_icon="⚡", layout="wide")

# 狀態初始化
if 'cloud_done' not in st.session_state:
    st.session_state.cloud_done = []
if 'last_sync' not in st.session_state:
    st.session_state.last_sync = datetime.min

# 2. 原始名單 (此處省略部分重複名單以節省空間，請沿用你原本的 raw_data)
raw_data = {
    "美術": [("大一班 粉蠟筆", "王銘緯"), ("大一班 粉蠟筆", "許鈞凱"), ("大一班 粉蠟筆", "陳愷蒂"), ("大一班 藍天使", "吳秉宸"), ("大二班 紫葡萄", "張簡瑞晨"), ("大二班 綠格子", "王子蕎"), ("中二班 冰淇淋", "宋宥希")],
    "直排輪": [("大一班 粉蠟筆", "陳愷蒂"), ("大一班 粉蠟筆", "劉恩谷"), ("大一班 藍天使", "周星宇"), ("大二班 紫葡萄", "吳尚恩"), ("大二班 紫葡萄", "林予煖"), ("大二班 綠格子", "張哲銘"), ("中二班 冰淇淋", "吳承浚"), ("中二班 冰淇淋", "宋宥希")],
    # ... 其餘班級請保持不變 ...
}

today = datetime.now().strftime("%Y-%m-%d")

# --- 3. 同步函數 (僅讀取進度，不讀取詳細點名內容以求快) ---
def sync_progress():
    try:
        resp = requests.get(f"{SCRIPT_URL}?date={today}", timeout=3)
        if resp.status_code == 200:
            st.session_state.cloud_done = resp.json()
            st.session_state.last_sync = datetime.now()
    except: pass

# --- 4. 側邊欄設計 ---
st.sidebar.title(" 才藝班列表")
if st.sidebar.button("🔄 同步雲端進度", use_container_width=True):
    sync_progress()

# 生成帶圖標的選項
display_map = {f"{'✅' if c in st.session_state.cloud_done else '⚪'} {c}": c for c in raw_data.keys()}
selected_label = st.sidebar.radio("選擇課程", list(display_map.keys()), label_visibility="collapsed")
classroom = display_map[selected_label]

st.title(f"🍎 {classroom} 點名介面")
if classroom in st.session_state.cloud_done:
    st.warning(f"💡 提醒：{classroom} 今日已點過名。若點錯了，修改後直接送出，系統會自動覆蓋舊紀錄。")
st.divider()

# --- 5. 點名介面渲染 ---
status_dict = {}
reason_dict = {}
for class_name, name in raw_data[classroom]:
    full_id = f"{class_name} {name}"
    c1, c2, c3 = st.columns([1.5, 3, 2])
    with c1: st.write(f"**{full_id}**")
    with c2:
        res = st.radio(f"S-{full_id}", ["到校", "請假", "未到"], horizontal=True, key=f"s_{classroom}_{full_id}", label_visibility="collapsed")
        status_dict[full_id] = (class_name, name, res)
    with c3:
        if res != "到校":
            reason_dict[full_id] = st.text_input(f"R-{full_id}", placeholder="原因", key=f"r_{classroom}_{full_id}", label_visibility="collapsed")
        else:
            reason_dict[full_id] = ""

# --- 6. 送出/修正邏輯 ---
btn_text = "🚀 確認提交紀錄" if classroom not in st.session_state.cloud_done else "🔄 確認修正並覆蓋紀錄"
if st.button(btn_text, type="primary", use_container_width=True):
    # 樂觀更新標記
    if classroom not in st.session_state.cloud_done:
        st.session_state.cloud_done.append(classroom)
        
    with st.spinner('正在同步至 Excel...'):
        payload = [{
            "date": today, "classroom": classroom, "lesson": c, "name": n, "status": s, "time": datetime.now().strftime("%H:%M:%S"), "note": reason_dict.get(f"{c} {n}", "")
        } for c, n, s in status_dict.values()]
        
        try:
            r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=8)
            if r.status_code == 200:
                st.success("✅ Excel 資料已更新！")
                st.balloons()
            else: st.error("連線超時")
        except: st.error("網路異常")

