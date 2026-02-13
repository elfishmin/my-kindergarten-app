import streamlit as st  # 👈 這一行必須在最前面，且左邊不能有空格
import pandas as pd
from datetime import datetime
import requests
import json
import time

# ==========================================
# 1. 核心設定
# ==========================================
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxrOI14onlrt4TAEafHX1MfY60rN-dXHJ5RF2Ipx4iB6pp1A8lPPpE8evMNemg5tygtyQ/exec"

# 必須先執行 set_page_config
st.set_page_config(page_title="才藝點名系統 V32.3", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")

# --- 核心同步函數：從 Excel 撈資料 ---
@st.cache_data(ttl=3600)  # 👈 這裡就不會再報 NameError 了
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=10)
        raw_list = response.json()
        
        # 建立週一至週五結構
        structured_data = {day: {} for day in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        
        for row in raw_list:
            if len(row) < 3: continue
            class_name, student_name, subject = str(row[0]), str(row[1]), str(row[2])
            
            # 寬鬆匹配邏輯，確保班級不消失
            days = []
            s = subject.upper() # 轉大寫比對更準確
            if any(k in s for k in ["舞蹈", "感統A", "積木A"]): days = ["星期一"]
            elif any(k in s for k in ["美術", "陶土", "美語"]): days = ["星期二", "星期五"]
            elif any(k in s for k in ["桌遊", "足球"]): days = ["星期三"]
            elif any(k in s for k in ["感統B", "直排輪", "積木B"]): days = ["星期四"]
            
            for day in days:
                if subject not in structured_data[day]:
                    structured_data[day][subject] = []
                structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except Exception as e:
        # 如果失敗，在畫面上印出錯誤方便除錯
        st.error(f"連線失敗: {e}")
        return {}

# ... (其餘程式碼保持不變)
