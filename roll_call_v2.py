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

# 3. 初始化 Session State (確保快速操作按鈕運作正常)
if 'default_status' not in st.session_state:
    st.session_state.default_status = "到校"

# 側邊欄設定
st.sidebar.header("⚙️ 管理選單")
classroom = st.sidebar.selectbox("選擇班級", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂名稱", value="早自習")
today = datetime.now().strftime("%Y-%m-%d")

st.title(f"🍎 {classroom} 點名系統")

# --- 4. 快速操作區域 ---
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

# --- 5. 點名清單介面 ---
status_dict = {}
reason_dict = {}
current_students = students_data[classroom]

options = ["到校", "請假", "未到"]
# 根據 default_status 決定 radio 的起始位置
current_idx = options.index(st.session_state.default_status)

for student in current_students:
    col1, col2, col3 = st.columns([1, 3, 2])
    
    with col1:
        st.write(f"**{student}**")
        
    with col2:
        # 使用 key 確保狀態獨立，使用 index 連動快速按鈕
        status = st.radio(
            f"S-{student}", options, 
            index=current_idx, 
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

# --- 6. 提交邏輯 (優化後的批次傳送) ---
if st.button("🚀 確認提交", type="primary", use_container_width=True):
    with st.spinner('正在同步全班資料至 Google 試算表...'):
        now_time = datetime.now().strftime("%H:%M:%S")
        
        # 建立整班的資料包
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
            # 一次性發送整包 JSON 列表
            response = requests.post(SCRIPT_URL, data=json.dumps(payload_list))
            if response.status_code == 200:
                st.success(f"🎉 {classroom} 點名紀錄已成功儲存！")
                st.balloons()
            else:
                st.error(f"連線失敗，請檢查 Script 部署權限。 (錯誤碼: {response.status_code})")
        except Exception as e:
            st.error(f"發生非預期錯誤: {e}")
