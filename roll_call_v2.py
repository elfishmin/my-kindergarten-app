import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 請在此處填上您「重新部署後」的 Google Apps Script 網址
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="雲端點名系統", page_icon="🍎", layout="wide")

# 2. 學生名單資料庫
students_data = {
    "大班": ["王小明", "李小華", "張小花", "劉德華"],
    "中班": ["陳大文", "林小智", "吳美美", "周杰倫"],
    "小班": ["郭雪芙", "蔡依林", "張惠妹", "陳奕迅"]
}

# 側邊欄設定
st.sidebar.header("⚙️ 管理選單")
classroom = st.sidebar.selectbox("選擇班級", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂名稱", value="早自習")
today = datetime.now().strftime("%Y-%m-%d")

st.title(f"🍎 {classroom} 點名系統")

# 已移除快速操作按鈕 (全班到齊/全班未到)
st.write("請勾選下方學生出勤狀況：")

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
        # 移除 index 連動，預設皆為 "到校" (options 的第 0 個)
        status = st.radio(
            f"S-{student}", options, 
            index=0, 
            horizontal=True, 
            key=f"s_{classroom}_{student}", 
            label_visibility="collapsed"
        )
        status_dict[student] = status
        
    with col3:
        # 只有「請假」或「未到」才顯示原因框
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

# --- 4. 提交邏輯 (批次傳送) ---
if st.button("🚀 確認提交", type="primary", use_container_width=True):
    with st.spinner('正在同步全班資料至 Google 試算表...'):
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
                st.success(f"🎉 {classroom} 點名紀錄已成功儲存！")
                st.balloons()
            else:
                st.error(f"連線失敗，請檢查 Script 部署權限。 (錯誤碼: {response.status_code})")
        except Exception as e:
            st.error(f"發生非預期錯誤: {e}")

