import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 請在此處貼上您的 Google Apps Script 網址
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="雲端點名系統", page_icon="🍎", layout="wide")

# 2. 學生名單
students_data = {
    "大班": ["王小明", "李小華", "張小花", "劉德華"],
    "中班": ["陳大文", "林小智", "吳美美", "周杰倫"],
    "小班": ["郭雪芙", "蔡依林", "張惠妹", "陳奕迅"]
}

# 3. 側邊欄
st.sidebar.header("⚙️ 管理選單")
classroom = st.sidebar.selectbox("選擇班級", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂名稱", value="早自習")
today = datetime.now().strftime("%Y-%m-%d")

st.title(f"🍎 {classroom} 點名系統")

# --- 4. 快速操作 (連動邏輯核心) ---
if 'default_status' not in st.session_state:
    st.session_state.default_status = "到校"

st.write("#### 快速操作")
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("✅ 全班到齊", use_container_width=True):
        st.session_state.default_status = "到校"
        st.rerun() 
with col_btn2:
    if st.button("❌ 全班未到", use_container_width=True):
        st.session_state.default_status = "未到"
        st.rerun()

st.divider()

# 5. 點名介面
status_dict = {}
reason_dict = {}
current_students = students_data[classroom]

for student in current_students:
    # 調整欄位比例：名字(1.2) | 狀態按鈕(2.8) | 原因空格(2)
    col1, col2, col3 = st.columns([1.2, 2.8, 2])
    
    with col1:
        st.write(f"**{student}**")
        
    with col2:
        options = ["到校", "請假", "未到"]
        # 關鍵連動：使用 index 變數讓按鈕控制選項
        idx = options.index(st.session_state.default_status)
        status = st.radio(
            f"S-{student}", options, index=idx, horizontal=True, 
            key=f"s_{classroom}_{student}", label_visibility="collapsed"
        )
        status_dict[student] = status
        
    with col3:
        # 只有在「請假」或「未到」時，才在右側小格子顯示原因輸入
        if status in ["請假", "未到"]:
            reason = st.text_input(
                f"R-{student}", 
                placeholder="原因...", 
                key=f"r_{classroom}_{student}",
                label_visibility="collapsed"
            )
            reason_dict[student] = reason
        else:
            reason_dict[student] = ""
            st.write("") # 保持對齊

st.divider()

# 6. 提交
if st.button("🚀 確認提交", type="primary", use_container_width=True):
    with st.spinner('同步中...'):
        now_time = datetime.now().strftime("%H:%M:%S")
        for name, stat in status_dict.items():
            payload = {
                "date": today, 
                "classroom": classroom, 
                "lesson": lesson_name,
                "name": name, 
                "status": stat, 
                "time": now_time,
                "note": reason_dict[name]
            }
            requests.post(SCRIPT_URL, data=json.dumps(payload))
        st.success("🎉 資料已成功同步至 Google 表單！")
        st.balloons()
