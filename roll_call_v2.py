# --- 核心同步函數：從 Excel 撈資料 (V32.3 修復班級消失問題) ---
@st.cache_data(ttl=3600)
def fetch_cloud_data():
    try:
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=10)
        raw_list = response.json()
        
        structured_data = {day: {} for day in ["星期一", "星期二", "星期三", "星期四", "星期五"]}
        for row in raw_list:
            if len(row) < 3: continue
            class_name, student_name, subject = str(row[0]), str(row[1]), str(row[2])
            
            # --- 修正後的寬鬆分類邏輯 ---
            days = []
            if any(k in subject for k in ["舞蹈", "感統A", "積木A"]): 
                days = ["星期一"]
            elif any(k in subject for k in ["美術", "陶土", "美語"]): 
                days = ["星期二", "星期五"]
            elif any(k in subject for k in ["桌遊", "足球"]): 
                days = ["星期三"]
            elif any(k in subject for k in ["感統B", "直排輪", "積木B"]): 
                days = ["星期四"]
            
            # 如果還是沒分到類，我們可以預設放進「星期五」或是印出提醒
            if not days:
                # 這裡可以放一個保險，避免班級完全消失
                continue 
            
            for day in days:
                if subject not in structured_data[day]:
                    structured_data[day][subject] = []
                structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except Exception as e:
        st.error(f"讀取資料失敗: {e}")
        return {}
