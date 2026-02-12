import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 基本設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="才藝班點名-極速版", page_icon="⚡", layout="wide")

# 完整名單 (略，請保留您原本程式碼中的 raw_data 內容)
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

# --- 2. 狀態管理與強制同步 ---
# 檢查是否有 done_list，若無則初始化並同步一次
if 'done_list' not in st.session_state:
    st.session_state.done_list = []
    # 第一次啟動時，主動去問一次雲端
    try:
        r = requests.get(f"{SCRIPT_URL}?date={today}", timeout=3)
        if r.status_code == 200:
            st.session_state.done_list = r.json()
    except:
        pass

def manual_sync():
    """ 手動強制刷新邏輯 """
    try:
        r = requests.get(f"{SCRIPT_URL}?date={today}", timeout=5)
        if r.status_code == 200:
            st.session_state.done_list = r.json()
            st.toast("同步成功！已取得最新進度", icon="☁️")
        else:
            st.toast("雲端回報錯誤", icon="❌")
    except Exception as e:
        st.toast(f"網路連線超時", icon="⚠️")

# --- 3. 側邊欄：帶勾顯示 ---
with st.sidebar:
    st.title("🎨 才藝班點名")
    st.button("🔄 同步雲端進度", on_click=manual_sync, use_container_width=True)
    st.divider()
    
    # 建立選項與對應表
    display_options = []
    mapping = {}
    for c in raw_data.keys():
        # 從 st.session_state.done_list 判斷是否打勾
        icon = "✅" if c in st.session_state.done_list else "⚪"
        label = f"{icon} {c}"
        display_options.append(label)
        mapping[label] = c
    
    selected_label = st.radio("課程清單", display_options, key="nav_radio", label_visibility="collapsed")
    current_class = mapping[selected_label]

# --- 4. 主畫面 ---
st.title(f"🍎 {current_class}")

if current_class in st.session_state.done_list:
    st.success("🎉 此班級今日已完成點名 (修正後儲存將覆蓋舊紀錄)")

st.divider()

# 點名介面渲染
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

# --- 5. 儲存邏輯 ---
if st.button("🚀 儲存並提交紀錄", type="primary", use_container_width=True):
    # 1. 樂觀標記：讓側邊欄立刻變勾勾
    if current_class not in st.session_state.done_list:
        st.session_state.done_list.append(current_class)
    
    # 2. 準備資料
    now_time = datetime.now().strftime("%H:%M:%S")
    payload = [{
        "date": today, "classroom": current_class, "lesson": cn, "name": sn, "status": s, "time": now_time, "note": reason_dict.get(f"{cn} {sn}", "")
    } for cn, sn, s in status_dict.values()]
    
    # 3. 傳送
    try:
        with st.spinner("傳送中..."):
            r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=8)
            if r.status_code == 200:
                st.toast(f"✅ {current_class} 儲存成功", icon='🎉')
                st.rerun() # 點完立即重繪以確保 ✅ 狀態被鎖定
            else:
                st.error("寫入失敗，請確認網路或 URL 是否正確")
    except:
        st.error("網路超時，但資料可能已排程送出，請刷新確認")
