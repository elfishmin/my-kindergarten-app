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

# 2. 完整才藝班學生名單 (根據上傳名冊整理)
students_data = {
    "直排輪(一) 星期一": ["陳薏伶", "陳禹羽", "陳禹豪", "李承安", "林品岑", "方彤", "邱晨恩", "曾苡淳"],
    "直排輪(二) 星期四": ["陳芯宇", "杜承希", "王翊捷", "徐晨恩", "黃聖勛", "林子寬"],
    "足球班 星期五": ["劉禹豪", "李承寬", "謝承安", "張峻維", "郭宥瑞", "曾芷語", "陳奕丞", "葉宸睿"],
    "Lasy積木(一) 星期一": ["黃品瑀", "柯品宇", "蔡羽倢", "林芮妡", "周品宇", "劉秉佑"],
    "Lasy積木(二) 星期三": ["李語芯", "簡呈宇", "張芮涵", "許芮妢", "陳楷勳", "張育睿"],
    "美術班(一) 星期二": ["羅苡恩", "李舒璇", "蔡欣芸", "鍾宜芯", "謝采霏"],
    "美術班(二) 星期四": ["林子帆", "張哲恩", "黃愉榛", "陳奕廷", "蘇品涵", "林禹潔"],
    "體能操 星期二": ["杜承希", "王翊捷", "陳楷勳", "曾芷語", "葉宸睿"],
    "MV舞蹈 星期三": ["張芯瑗", "黃愉榛", "蘇品涵", "劉芷均", "邱晨恩"],
    "心算班 星期三": ["曾苡淳", "謝采霏", "蘇品涵", "林禹潔", "林子寬"],
    "珠算班 星期三": ["曾苡淳", "謝采霏", "蘇品涵", "林禹潔", "林子寬"],
    "圍棋班 星期二": ["林芮妡", "柯品宇", "簡呈宇", "許芮妢", "陳奕丞"]
}

# 側邊欄設定
st.sidebar.header("⚙️ 才藝班管理")
classroom = st.sidebar.selectbox("選擇才藝課程", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂備註", value="正式課")
today = datetime.now().strftime("%Y-%m-%d")

st.title(f"🎨 {classroom} 點名系統")
st.write(f"今日日期：{today}")

st.divider()

# --- 3. 點名介面 ---
status_dict = {}
reason_dict = {}
current_students = students_data[classroom]

options = ["到校", "請假", "未到"]

for student in current_students:
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
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
                placeholder="備註原因...", 
                key=f"r_{classroom}_{student}",
                label_visibility="collapsed"
            )
            reason_dict[student] = reason
        else:
            reason_dict[student] = ""

st.divider()

# --- 4. 提交邏輯 (批次傳送) ---
if st.button("🚀 儲存本次點名紀錄", type="primary", use_container_width=True):
    with st.spinner('連線至雲端試算表...'):
        now_time = datetime.now().strftime("%H:%M:%S")
        
        payload_list = []
        for name, stat in status_dict.items():
            payload_list.append({
                "date": today,
                "classroom": classroom, 
                "lesson": lesson_name,
                "name": name,
                "status": stat,
                "time": now_time,
                "note": reason_dict.get(name, "")
            })
        
        try:
            response = requests.post(SCRIPT_URL, data=json.dumps(payload_list))
            if response.status_code == 200:
                st.success(f"🎉 {classroom} 紀錄儲存成功！")
                st.balloons()
            else:
                st.error("儲存失敗，請檢查網路連線。")
        except Exception as e:
            st.error(f"錯誤回報: {e}")
