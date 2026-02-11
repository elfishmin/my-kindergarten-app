import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# ==========================================
# 1. 在下面這行貼上您的 Google Apps Script 網址
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

st.set_page_config(page_title="雲端同步點名", page_icon="☁️")
st.title("🍎 幼稚園雲端同步點名系統")

# 學生名單資料
students_data = {
    "大班": ["王小明", "李小華", "張小花", "劉德華"],
    "中班": ["陳大文", "林小智", "吳美美", "周杰倫"],
    "小班": ["郭雪芙", "蔡依林", "張惠妹", "陳奕迅"]
}

# 側邊欄設定
classroom = st.sidebar.selectbox("選擇班級", list(students_data.keys()))
lesson_name = st.sidebar.text_input("課堂名稱", value="早自習")
today = datetime.now().strftime("%Y-%m-%d")

# 點名主畫面
st.write(f"### 班級：{classroom}")
status_dict = {}

# 產生點名按鈕
for student in students_data[classroom]:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"**{student}**")
    with col2:
        # 使用 radio 按鈕選擇狀態
        status = st.radio(
            f"狀態-{student}", 
            options=["到校", "請假", "未到"], 
            horizontal=True, 
            key=student, 
            label_visibility="collapsed"
        )
        status_dict[student] = status

st.divider()

# 提交按鈕
if st.button("確認提交並同步至雲端 Excel", type="primary", use_container_width=True):
    with st.spinner('正在將點名紀錄傳送到 Google 試算表...'):
        success_count = 0
        now_time = datetime.now().strftime("%H:%M:%S")
        
        # 逐筆將學生資料傳送到雲端
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
                # 這裡會連線到您的 Apps Script
                response = requests.post(SCRIPT_URL, data=json.dumps(payload))
                if response.status_code == 200:
                    success_count += 1
            except Exception as e:
                st.error(f"傳送 {name} 資料時發生錯誤: {e}")

        if success_count == len(status_dict):
            st.success(f"🎉 成功！全班 {success_count} 位同學紀錄已寫入雲端。")
            st.balloons()
        else:
            st.warning(f"同步完成，但成功數量不符（{success_count}/{len(status_dict)}）。")