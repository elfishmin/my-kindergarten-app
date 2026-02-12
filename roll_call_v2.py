import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 請填入最新的 SCRIPT_URL
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="才藝班同步點名系統", page_icon="🍎", layout="wide")

today = datetime.now().strftime("%Y-%m-%d")

# 2. 學生名冊資料
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

# --- 3. 雲端同步檢查 (關鍵功能) ---
@st.cache_data(ttl=10) # 每 10 秒自動重新獲取一次雲端狀態
def get_cloud_submitted_list(date):
    try:
        resp = requests.get(f"{SCRIPT_URL}?date={date}")
        return resp.json().get("submittedClasses", [])
    except:
        return []

# 取得今天哪些班級點過了
done_classes = get_cloud_submitted_list(today)

# --- 4. 側邊欄：生成帶有標註的選單 ---
st.sidebar.header("🎨 才藝班列表")

# 建立顯示用的名稱清單
display_options = []
for c in raw_data.keys():
    label = f"{c} (✅ 已點名)" if c in done_classes else f"{c} (⚪ 未點名)"
    display_options.append(label)

# 讓老師選擇（左側 radio）
selected_label = st.sidebar.radio("請選擇班級：", display_options, label_visibility="collapsed")

# 從顯示名稱還原回原始班級 key
classroom = selected_label.split(" (")[0]

st.title(f"🍎 {classroom} 點名系統")
st.write(f"今日日期：{today}")
st.divider()

# --- 5. 點名介面 ---
status_dict = {}
reason_dict = {}
student_info_list = raw_data[classroom]
options = ["到校", "請假", "未到"]

for class_name, name in student_info_list:
    full_display_name = f"{class_name} {name}"
    col1, col2, col3 = st.columns([1.5, 3, 2])
    with col1:
        st.write(f"**{full_display_name}**")
    with col2:
        status = st.radio(f"S-{full_display_name}", options, horizontal=True, key=f"s_{classroom}_{full_display_name}", label_visibility="collapsed")
        status_dict[full_display_name] = (class_name, name, status)
    with col3:
        if status in ["請假", "未到"]:
            reason = st.text_input(f"R-{full_display_name}", placeholder="原因...", key=f"r_{classroom}_{full_display_name}", label_visibility="collapsed")
            reason_dict[full_display_name] = reason
        else:
            reason_dict[full_display_name] = ""

st.divider()

# --- 6. 提交邏輯 ---
if st.button(f"🚀 提交/更新【{classroom}】點名紀錄", type="primary", use_container_width=True):
    with st.spinner('正在更新雲端資料...'):
        now_time = datetime.now().strftime("%H:%M:%S")
        payload_list = [{
            "date": today, "classroom": classroom, "lesson": c, "name": n, "status": s, "time": now_time, "note": reason_dict.get(f"{c} {n}", "")
        } for c, n, s in status_dict.values()]
        
        try:
            requests.post(SCRIPT_URL, data=json.dumps(payload_list))
            st.success("紀錄更新成功！")
            st.cache_data.clear() # 提交後強制清除快取，立即更新左側狀態標籤
            st.rerun()
        except:
            st.error("同步失敗")

# 如果該班級已點過，在主畫面提示
if classroom in done_classes:
    st.info(f"💡 提醒：{classroom} 今日已有老師提交過紀錄，再次提交將會覆蓋舊資料。")
