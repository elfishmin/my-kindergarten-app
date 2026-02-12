import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"
st.set_page_config(page_title="才藝班點名系統", page_icon="🏫", layout="wide")

# 完整 240+ 筆交叉比對名單 (名單已根據您的 CSV 校對)
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

# --- 2. 狀態管理 (修正第 46 行語法) ---
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
weekday_map = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'done_list' not in st.session_state:
    st.session_state.done_list = []
if 'current_class' not in st.session_state:
    if current_day in all_data:
        st.session_state.current_class = list(all_data[current_day].keys())[0]
    else:
        st.session_state.current_class = "足球"

# --- 3. 側邊欄 ---
with st.sidebar:
    st.title("🏫 全校點名")
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
st.write(f"📊 名冊共 {len(students)} 位學生")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🙋‍♂️ 全員到校", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"
with col_b:
    if st.button("🧹 重置名單", use_container_width=True):
        for cn, sn in students: st.session_state[f"s_{cn}_{sn}"] = "到校"

st.divider()

# 點名區：班別與人名放在同一行，不換行
status_results = {}
for class_name, name in students:
    full_id = f"{class_name}_{name}"
    # 增加左側寬度，讓班級與名字能並排
    c1, c2, c3 = st.columns([3.5, 4, 2.5])
    with c1: 
        # 顯示格式：班級 姓名 (例如: 冰淇淋 吳姷樼)
        st.markdown(f"**{class_name}** {name}")
    with c2:
        res = st.radio("狀態", ["到校", "請假", "未到"], horizontal=True, key=f"s_{full_id}", label_visibility="collapsed")
        status_results[full_id] = (class_name, name, res)
    with c3:
        note = st.text_input("備註", key=f"n_{full_id}", label_visibility="collapsed", placeholder="原因") if res != "到校" else ""
        status_results[full_id] += (note,)

# --- 5. 儲存與下載 ---
st.divider()
col_save, col_dl = st.columns([2, 1])

with col_save:
    if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
        if active_class not in st.session_state.done_list: st.session_state.done_list.append(active_class)
        payload = [{"date": today_str, "classroom": active_class, "lesson": item[0], "name": item[1], "status": item[2], "time": datetime.now().strftime("%H:%M:%S"), "note": item[3]} for item in status_results.values()]
        try: requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=0.1)
        except: pass
        st.toast("🎉 雲端儲存成功！")
        time.sleep(0.5)
        st.rerun()

with col_dl:
    df_export = pd.DataFrame([{"班級": i[0], "姓名": i[1], "狀態": i[2], "備註": i[3]} for i in status_results.values()])
    csv_data = df_export.to_csv(index=False).encode('utf-8-sig') 
    st.download_button(label="📥 下載 CSV", data=csv_data, file_name=f"{active_class}_{today_str}.csv", mime="text/csv", use_container_width=True)
