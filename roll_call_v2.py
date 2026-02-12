import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 請填入最新的 SCRIPT_URL
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="全校才藝班點名系統", page_icon="🏫", layout="wide")

# 初始化狀態
if 'cloud_done' not in st.session_state:
    st.session_state.cloud_done = []
if 'last_sync' not in st.session_state:
    st.session_state.last_sync = datetime.min

# 2. 從名冊 CSV 提取的完整名單
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

# 3. 同步功能
def sync_cloud():
    try:
        resp = requests.get(f"{SCRIPT_URL}?date={today}", timeout=3)
        if resp.status_code == 200:
            st.session_state.cloud_done = resp.json()
            st.session_state.last_sync = datetime.now()
    except: pass

if (datetime.now() - st.session_state.last_sync).total_seconds() > 300:
    sync_cloud()

# 4. 側邊欄導覽
st.sidebar.title("🎨 才藝班列表")
if st.sidebar.button("🔄 刷新雲端狀態", use_container_width=True):
    sync_cloud()

# 生成帶圖示的列表
options_map = {f"{'✅' if c in st.session_state.cloud_done else '⚪'} {c}": c for c in raw_data.keys()}
selected_label = st.sidebar.radio("選擇班級", list(options_map.keys()), label_visibility="collapsed")
classroom = options_map[selected_label]

# 5. 主點名畫面
st.title(f"🏫 {classroom} 點名系統")
if classroom in st.session_state.cloud_done:
    st.info("💡 此班級今日已完成點名，您可以進行修改並重新送出，系統會自動更新舊資料。")

st.divider()

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
            reason_dict[full_id] = st.text_input(f"原因", key=f"r_{classroom}_{full_id}", label_visibility="collapsed", placeholder="輸入原因")
        else: reason_dict[full_id] = ""

st.divider()

# 6. 送出邏輯
btn_label = "🔄 修正並更新紀錄" if classroom in st.session_state.cloud_done else "🚀 確認提交紀錄"
if st.button(btn_label, type="primary", use_container_width=True):
    if classroom not in st.session_state.cloud_done:
        st.session_state.cloud_done.append(classroom)
    
    with st.spinner('同步至雲端 Excel 中...'):
        now_time = datetime.now().strftime("%H:%M:%S")
        payload = [{
            "date": today, "classroom": classroom, "lesson": cn, "name": sn, "status": s, "time": now_time, "note": reason_dict.get(f"{cn} {sn}", "")
        } for cn, sn, s in status_dict.values()]
        
        try:
            r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=8)
            if r.status_code == 200:
                st.success("✅ 資料已成功寫入 Excel 原位址！")
                st.balloons()
            else: st.error("連線超時，請檢查網路")
        except: st.error("網路異常")
