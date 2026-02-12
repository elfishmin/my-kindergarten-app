import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 請確認您的 Google Apps Script 網址
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="才藝班雲端點名系統", page_icon="🎨", layout="wide")

# 2. 才藝班學生名單 (格式：班別 + 姓名)
students_data = {
    "美術": [
        "大一班 粉蠟筆 王銘緯", "大一班 粉蠟筆 許鈞凱", "大一班 粉蠟筆 陳愷蒂", 
        "大一班 藍天使 吳秉宸", "大二班 紫葡萄 張簡瑞晨", "大二班 綠格子 王子蕎",
        "中二班 冰淇淋 宋宥希"
    ],
    "直排輪": [
        "大一班 粉蠟筆 陳愷蒂", "大一班 粉蠟筆 劉恩谷", "大一班 藍天使 周星宇", 
        "大二班 紫葡萄 吳尚恩", "大二班 紫葡萄 林予煖", "大二班 綠格子 張哲銘",
        "中二班 冰淇淋 吳承浚", "中二班 冰淇淋 宋宥希"
    ],
    "足球": [
        "大一班 粉蠟筆 謝恩典", "大一班 藍天使 吳秉宸", "大一班 藍天使 黃彥淇",
        "中二班 冰淇淋 宋宥希"
    ],
    "桌遊": [
        "大一班 粉蠟筆 吳鎧崴", "大一班 粉蠟筆 鐘苡禎", "大二班 紫葡萄 黃芊熒", 
        "大二班 紫葡萄 蘇祐森", "大二班 綠格子 陳語棠", "中二班 冰淇淋 徐承睿"
    ],
    "陶土": [
        "大一班 粉蠟筆 謝恩典", "大一班 藍天使 鄭尹棠", "中二班 冰淇淋 徐承睿"
    ],
    "積木A": [
        "大一班 藍天使 黃宇頡", "中二班 冰淇淋 宋宥希", "中二班 冰淇淋 張簡睿泱"
    ],
    "積木B": [
        "大二班 綠格子 陳冠呈", "大二班 綠格子 陳姵吟", "中二班 冰淇淋 徐承睿"
    ],
    "舞蹈A": [
        "大二班 綠格子 邱子芮", "中二班 冰淇淋 吳姷樼", "中二班 冰淇淋 宋宥希", 
        "中二班 冰淇淋 張簡睿泱"
    ],
    "美語A一": [
        "中二班 冰淇淋 吳承浚", "中二班 冰淇淋 李悅宸", "中二班 冰淇淋 陳劭齊"
    ],
    "感統A": [
        "中二班 冰淇淋 徐承睿", "中二班 冰淇淋 陳芸希"
    ],
    "感統B": [
        "中二班 冰淇淋 范芯瑀", "中二班 冰淇淋 張簡睿泱"
    ]
}

# 側邊欄設定
st.sidebar.header("⚙️ 才藝班管理")
# 原本的「選擇班級」已改為「選擇才藝班」
classroom = st.sidebar.selectbox("選擇才藝班", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂備註", value="正式課")
today = datetime.now().strftime("%Y-%m-%d")

st.title(f"🎨 {classroom} 點名系統")
st.write(f"日期：{today}")

st.divider()

# --- 3. 點名介面 ---
status_dict = {}
reason_dict = {}
current_students = students_data[classroom]

options = ["到校", "請假", "未到"]

for student in current_students:
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
        # 顯示帶有班別的全名
        st.write(f"**{student}**")
        
    with col2:
        status = st.radio(
            f"S-{student}", options, 
            index=0, 
            horizontal=True, 
            key=f"s_{classroom}_{student}", 
            label_visibility="collapsed"
        )
        status_dict[student] = status
        
    with col3:
        if status in ["請假", "未到"]:
            reason = st.text_input(
                f"R-{student}", 
                placeholder="輸入原因...", 
                key=f"r_{classroom}_{student}",
                label_visibility="collapsed"
            )
            reason_dict[student] = reason
        else:
            reason_dict[student] = ""

st.divider()

# --- 4. 提交邏輯 ---
if st.button("🚀 確認提交點名紀錄", type="primary", use_container_width=True):
    with st.spinner('正在同步至雲端試算表...'):
        now_time = datetime.now().strftime("%H:%M:%S")
        
        payload_list = []
        for name, stat in status_dict.items():
            payload_list.append({
                "date": today,
                "classroom": classroom, # 這裡會存入「才藝班名稱」
                "lesson": lesson_name,
                "name": name,           # 這裡會存入「班別+姓名」
                "status": stat,
                "time": now_time,
                "note": reason_dict.get(name, "")
            })
        
        try:
            response = requests.post(SCRIPT_URL, data=json.dumps(payload_list))
            if response.status_code == 200:
                st.success(f"🎉 {classroom} 點名成功！")
                st.balloons()
            else:
                st.error("連線失敗，請檢查 Google Script 部署。")
        except Exception as e:
            st.error(f"發生錯誤: {e}")
