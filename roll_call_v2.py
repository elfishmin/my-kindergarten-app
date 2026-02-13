import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定 (強制永久顯示側邊欄)
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(
    page_title="才藝班點名系統", 
    page_icon="🏫", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# 注入 CSS：強制 Sidebar 在小螢幕也不收合
st.markdown("""
    <style>
        /* 1. 隱藏左上角的收合/展開箭頭按鈕 */
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* 2. 強制側邊欄在手機版也保持顯示 (不移動到上方) */
        @media (max-width: 991px) {
            section[data-testid="stSidebar"] {
                width: 250px !important;
                position: relative !important;
                margin-left: 0 !important;
            }
            .main {
                margin-left: 20px !important;
            }
        }

        /* 3. 調整單選框間距 */
        .stRadio [role=radiogroup] {
            gap: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 以下維持原有名單與邏輯 ---
# ... (all_data 內容) ...

# 完整 240+ 筆名單 (保持不變)
all_data = {
    "星期一": {
        "舞蹈A": [("冰淇淋", "吳姷樼"), ("冰淇淋", "宋宥希"), ("冰淇淋", "張簡睿泱"), ("彩虹魚", "周子芹"), ("雪碧", "陳禹妃"), ("雪碧", "劉苡璇"), ("雪碧", "龔畇溱"), ("綠格子", "邱子芮")],
        "感統A": [("可樂1班", "林文峖"), ("可樂1班", "胡恩瑞"), ("可樂1班", "許甯喬"), ("可樂1班", "蔡宇謙"), ("可樂2班", "王品崴"), ("可樂2班", "蔡崴羽"), ("冰淇淋", "徐承睿"), ("冰淇淋", "陳芸希"), ("雪碧", "游帛洵")]
    },
    "星期二": {
        "美術": [("冰淇淋", "宋宥希"), ("冰淇淋", "林思橙"), ("粉蠟筆", "王銘緯"), ("粉蠟筆", "許鈞凱"), ("粉蠟筆", "陳愷蒂"), ("粉蠟筆", "謝恩典"), ("粉蠟筆", "許竑榤"), ("彩虹魚", "吳愷杰"), ("彩虹魚", "黃語葳"), ("雪碧", "王星鈞"), ("雪碧", "林佳穎"), ("雪碧", "陳禹妃"), ("雪碧", "黃梓碩"), ("雪碧", "廖允菲"), ("藍天使", "吳秉宸"), ("綠格子", "王子蕎"), ("紫葡萄", "張簡瑞晨")],
        "陶土": [("冰淇淋", "徐承睿"), ("彩虹魚", "李恩瑨"), ("彩虹魚", "周子芹"), ("雪碧", "林佳穎"), ("雪碧", "游帛洵"), ("雪碧", "龔畇溱"), ("粉蠟筆", "謝恩典"), ("藍天使", "鄭尹棠")],
        "美語小班": [("可樂1班", "林文峖"), ("可樂1班", "胡恩瑞"), ("可樂2班", "王品崴"), ("可樂2班", "黃若芸")]
    },
    "星期三": {
        "桌遊": [("冰淇淋", "徐承睿"), ("冰淇淋", "陳芸希"), ("彩虹魚", "李恩瑨"), ("彩虹魚", "陳盺"), ("雪碧", "王星鈞"), ("雪碧", "許宥甯"), ("粉蠟筆", "吳鎧崴"), ("粉蠟筆", "鐘苡禎"), ("綠格子", "陳語棠"), ("紫葡萄", "吳尚恩"), ("紫葡萄", "黃芊熒"), ("紫葡萄", "蘇祐森")],
        "足球": [("冰淇淋", "宋宥希"), ("彩虹魚", "周冠賢"), ("彩虹魚", "戴子睿"), ("粉蠟筆", "謝恩典"), ("藍天使", "吳秉宸"), ("藍天使", "黃彥淇"), ("綠格子", "周睿澤"), ("綠格子", "陳冠呈"), ("紫葡萄", "何丞鎧"), ("紫葡萄", "蘇祐森")]
    },
    "星期四": {
        "感統B": [("可樂1班", "宋昱希"), ("可樂1班", "黃柏睿"), ("可樂2班", "黃若芸"), ("可樂2班", "黃婕恩"), ("冰淇淋", "范芯瑀"), ("冰淇淋", "張簡睿泱"), ("彩虹魚", "戴子睿"), ("雪碧", "陳芋菲"), ("雪碧", "曾語安")],
        "直排輪": [("冰淇淋", "吳承浚"), ("冰淇淋", "吳姷樼"), ("冰淇淋", "宋宥希"), ("冰淇淋", "范芯瑀"), ("彩虹魚", "徐郁蓁"), ("粉蠟筆", "陳愷蒂"), ("粉蠟筆", "劉恩谷"), ("粉蠟筆", "鐘苡禎"), ("藍天使", "周星宇"), ("綠格子", "張哲銘"), ("紫葡萄", "吳尚恩"), ("紫葡萄", "林予煖")]
    },
    "星期五": {
        "積木A": [("冰淇淋", "宋宥希"), ("冰淇淋", "范芯瑀"), ("冰淇淋", "張簡睿泱"), ("冰淇淋", "陳芸希"), ("雪碧", "吳哲睿"), ("雪碧", "游帛洵"), ("雪碧", "黃梓碩"), ("藍天使", "黃宇頡"), ("蘋果派", "蔡枍廷"), ("甜甜圈", "林芊妤")],
        "積木B": [("冰淇淋", "林思橙"), ("冰淇淋", "徐承睿"), ("綠格子", "陳冠呈"), ("綠格子", "陳姵吟")],
        "美語小班": [("可樂1班", "林文峖"), ("可樂1班", "胡恩瑞"), ("可樂2班", "王品崴"), ("可樂2班", "黃若芸")]
    }
}

# --- 2. 狀態管理 ---
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'done_list' not in st.session_state: st.session_state.done_list = []
if 'current_class' not in st.session_state:
    st.session_state.current_class = list(all_data.get(current_day, {"舞蹈A":[]}).keys())[0]

# --- 3. 側邊欄 (永遠顯示) ---
with st.sidebar:
    st.title("🏫 才藝點名")
    if st.button("🔄 刷新雲端勾勾", use_container_width=True):
        try:
            r = requests.get(f"{SCRIPT_URL}?date={today_str}", timeout=5)
            st.session_state.done_list = r.json() if r.status_code == 200 else []
            st.toast("同步成功！")
        except: st.toast("連線雲端中...")
    
    st.divider()
    for day, classes in all_data.items():
        st.markdown(f"### {'🟢' if day == current_day else '⚪'} {day}")
        for c in classes.keys():
            icon = "✅" if c in st.session_state.done_list else "📝"
            if st.button(f"{icon} {c}", key=f"btn_{day}_{c}", use_container_width=True):
                st.session_state.current_class = c

# --- 4. 主畫面 ---
active_class = st.session_state.current_class
students = []
for d in all_data:
    if active_class in all_data[d]:
        students = all_data[d][active_class]
        break

st.title(f"🍎 {active_class}")

c_a, c_b = st.columns(2)
with c_a:
    if st.button("🙋‍♂️ 全員到校", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"
with c_b:
    if st.button("🧹 重置", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"

st.divider()

# 點名區 (排版：名字大字體、選項緊貼)
status_results = {}
for class_name, name in students:
    full_id = f"{class_name}_{name}"
    col1, col2, col3 = st.columns([3, 6, 1])
    with col1: 
        st.markdown(f"""
            <div style='display: flex; align-items: center; margin-right: -100px;'>
                <div style='width: 60px; color: gray; font-size: 12px; flex-shrink: 0;'>{class_name}</div>
                <div style='font-size: 24px; font-weight: bold; margin-left: 5px; color: #1E1E1E; white-space: nowrap;'>{name}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        res = st.radio("狀態", ["到校", "請假", "未到"], horizontal=True, key=f"s_{full_id}", label_visibility="collapsed")
        status_results[full_id] = (class_name, name, res)
    with col3:
        note = st.text_input("原因", key=f"n_{full_id}", label_visibility="collapsed", placeholder="備註") if res != "到校" else ""
        status_results[full_id] += (note,)

# --- 5. 儲存與下載 ---
st.divider()
col_save, col_dl = st.columns([2, 1])

with col_save:
    if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
        payload = [
            {
                "date": today_str, 
                "classroom": active_class, 
                "lesson": item[0], 
                "name": item[1], 
                "status": item[2], 
                "time": datetime.now().strftime("%H:%M:%S"), 
                "note": item[3]
            } for item in status_results.values()
        ]
        try:
            # 增加至 2 秒以配合 GAS 的覆蓋檢查邏輯
            requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=2)
            if active_class not in st.session_state.done_list:
                st.session_state.done_list.append(active_class)
            st.toast("🎉 雲端儲存/更新成功！")
        except:
            st.toast("傳送中...請稍後確認試算表")
        time.sleep(0.5)
        st.rerun()

with col_dl:
    df_export = pd.DataFrame([{"班級": i[0], "姓名": i[1], "狀態": i[2], "備註": i[3]} for i in status_results.values()])
    csv_data = df_export.to_csv(index=False).encode('utf-8-sig') 
    st.download_button(label="📥 CSV", data=csv_data, file_name=f"{active_class}_{today_str}.csv", mime="text/csv", use_container_width=True)

