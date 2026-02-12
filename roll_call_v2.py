import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 請在此處貼上您的 Google Apps Script 網址
# ==========================================
SCRIPT_URL = "這裡貼上您的網址"

st.set_page_config(page_title="雲端點名系統", page_icon="🍎", layout="centered")

# 2. 學生名單資料庫
students_data = {
    "大班": ["王小明", "李小華", "張小花", "劉德華"],
    "中班": ["陳大文", "林小智", "吳美美", "周杰倫"],
    "小班": ["郭雪芙", "蔡依林", "張惠妹", "陳奕迅"]
}

# 3. 側邊欄：管理選單
st.sidebar.header("⚙️ 管理選單")
classroom = st.sidebar.selectbox("選擇班級", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂名稱", value="早自習")
today = datetime.now().strftime("%Y-%m-%d")

st.title(f"🍎 {classroom} 點名系統")
st.write(f"日期：{today} | 課堂：{lesson_name}")

# --- 4. 增加「一鍵全選」功能 ---
st.subheader("快速操作")
col_all1, col_all2 = st.columns(2)

# 初始化 Session State (用來控制按鈕狀態)
if 'all_status' not in st.session_state:
    st.session_state.all_status = "到校"

with col_all1:
    if st.button("✅ 全班到齊", use_container_width=True):
        st.session_state.all_status = "到校"
        st.rerun() # 重新整理頁面以更新狀態

with col_all2:
    if st.button("❌ 全班未到", use_container_width=True):
        st.session_state.all_status = "未到"
        st.rerun()

st.divider()

# 5. 點名介面
status_dict = {}
st.write("#### 學生名單回報")

# 根據選擇的班級顯示名單
current_students = students_data[classroom]

for student in current_students:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"**{student}**")
    with col2:
        # 這裡的 index 會根據快速操作按鈕改變
        default_idx = ["到校", "請假", "未到"].index(st.session_state.all_status)
        
        status = st.radio(
            f"狀態-{student}", 
            options=["到校", "請假", "未到"], 
            index=default_idx,
            horizontal=True, 
            key=f"{classroom}_{student}", # 增加班級前綴，避免切換班級時報錯
            label_visibility="collapsed"
        )
        status_dict[student] = status

st.divider()

# 6. 提交至雲端
if st.button("🚀 確認提交並上傳雲端", type="primary", use_container_width=True):
    with st.spinner('連線中，請稍候...'):
        success_count = 0
        now_time = datetime.now().strftime("%H:%M:%S")
        
        for name, stat in status_dict.items():
            payload = {
                "date": today,
                "classroom": classroom,
                "lesson": lesson_name,
                "name": name,
                "status": stat,
                "time": now_time
            }
            try:
                response = requests.post(SCRIPT_URL, data=json.dumps(payload))
                if response.status_code == 200:
                    success_count += 1
            except:
                pass

        if success_count == len(status_dict):
            st.success(f"🎉 {classroom} 共 {success_count} 筆紀錄已存入雲端 Excel！")
            st.balloons()
        else:
            st.error("⚠️ 部分資料上傳失敗，請檢查網路或網址設定。")
