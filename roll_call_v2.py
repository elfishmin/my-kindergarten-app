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

# 2. 匯入才藝班名單 (根據您提供的 CSV 結構)
# 這裡模擬從您的檔案提取出的數據結構
students_data = {
    "直排輪(一)": ["陳○伶", "陳○羽", "陳○豪", "李○安", "林○岑", "方○", "邱○恩", "曾○淳"],
    "直排輪(二)": ["陳○宇", "杜○希", "王○捷", "徐○恩", "黃○勛", "林○寬"],
    "足球班": ["劉○豪", "李○寬", "謝○安", "張○維", "郭○瑞", "曾○語", "陳○丞", "葉○睿"],
    "Lasy積木(一)": ["黃○瑀", "柯○宇", "蔡○倢", "林○妡", "周○宇", "劉○佑"],
    "Lasy積木(二)": ["李○芯", "簡○宇", "張○涵", "許○倢", "陳○勳", "張○睿"],
    "美術班(一)": ["羅○恩", "李○璇", "蔡○芸", "鍾○芯", "謝○霏"],
    "美術班(二)": ["林○帆", "張○恩", "黃○榛", "陳○廷", "蘇○涵", "林○潔"]
}

# 側邊欄設定
st.sidebar.header("⚙️ 才藝班管理")
# 選項會自動顯示為：直排輪(一)、足球班...等
classroom = st.sidebar.selectbox("選擇課程", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂名稱", value="才藝課")
today = datetime.now().strftime("%Y-%m-%d")

st.title(f"🎨 {classroom} 點名介面")
st.write(f"日期：{today}")

st.divider()

# --- 3. 點名清單介面 ---
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
                placeholder="輸入原因...", 
                key=f"r_{classroom}_{student}",
                label_visibility="collapsed"
            )
            reason_dict[student] = reason
        else:
            reason_dict[student] = ""

st.divider()

# --- 4. 提交邏輯 ---
if st.button("🚀 確認提交才藝班紀錄", type="primary", use_container_width=True):
    with st.spinner('正在同步資料至 Google 試算表...'):
        now_time = datetime.now().strftime("%H:%M:%S")
        
        payload_list = []
        for name, stat in status_dict.items():
            payload_list.append({
                "date": today,
                "classroom": classroom, # 這裡會存入課程名稱
                "lesson": lesson_name,
                "name": name,
                "status": stat,
                "time": now_time,
                "note": reason_dict.get(name, "")
            })
        
        try:
            response = requests.post(SCRIPT_URL, data=json.dumps(payload_list))
            if response.status_code == 200:
                st.success(f"🎉 {classroom} 點名紀錄已成功儲存！")
                st.balloons()
            else:
                st.error(f"連線失敗，請檢查 Script 部署。 (錯誤碼: {response.status_code})")
        except Exception as e:
            st.error(f"發生非預期錯誤: {e}")
