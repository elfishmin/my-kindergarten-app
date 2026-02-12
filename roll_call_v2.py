import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 請在此處重新貼上您的 Google Apps Script 網址
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="雲端點名系統", page_icon="🍎")

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

# --- 4. 增加「一鍵全選」按鈕區 ---
# 使用 session_state 來儲存目前的預設狀態
if 'default_status' not in st.session_state:
    st.session_state.default_status = "到校"

# --- 4. 增加「一鍵全選」按鈕區 ---
# 使用 session_state 來儲存目前的預設狀態
if 'default_status' not in st.session_state:
    st.session_state.default_status = "到校"

st.write("#### 快速操作")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("✅ 全班到齊", use_container_width=True):
        st.session_state.default_status = "到校"
        st.rerun()  # <--- 關鍵：點擊後立刻重新整理網頁，下面的選項才會同步更新

with col_btn2:
    if st.button("❌ 全班未到", use_container_width=True):
        st.session_state.default_status = "未到"
        st.rerun()  # <--- 關鍵：點擊後立刻重新整理網頁

st.divider()

# 5. 點名介面
st.write(f"今日日期：{today} | 課堂：{lesson_name}")
status_dict = {}

# 取得目前班級名單
current_students = students_data[classroom]

for student in current_students:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"**{student}**")
    with col2:
        # 根據快速操作按鈕的選擇，動態設定 index
        options = ["到校", "請假", "未到"]
        idx = options.index(st.session_state.default_status)
        
        # 使用 classroom + student 作為 key，確保換班級時狀態會重新連動
        status = st.radio(
            f"狀態-{student}", 
            options=options, 
            index=idx,
            horizontal=True, 
            key=f"{classroom}_{student}",
            label_visibility="collapsed"
        )
        status_dict[student] = status

st.divider()

# 6. 提交按鈕
if st.button("🚀 確認提交並同步至雲端 Excel", type="primary", use_container_width=True):
    with st.spinner('同步中，請稍候...'):
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
            st.success(f"🎉 成功！{classroom} 共 {success_count} 位同學紀錄已寫入雲端。")
            st.balloons()
        else:
            st.error(f"⚠️ 部分失敗 (成功: {success_count}/{len(status_dict)})，請檢查網路。")


