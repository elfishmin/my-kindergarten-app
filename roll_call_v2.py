# ==========================================
# 1. 核心設定 (V35 排程動態化版)
# ==========================================
# 標題更新為 V35
st.set_page_config(page_title="才藝班點名系統 V35", page_icon="🏫", layout="wide")

# --- 修改後的資料獲取函數 ---
@st.cache_data(ttl=3600)
def fetch_cloud_data():
    try:
        # 向 GAS 請求包含學生與排程的資料封裝
        response = requests.get(f"{SCRIPT_URL}?action=get_students", timeout=10)
        json_data = response.json()
        
        raw_students = json_data.get("students", [])
        raw_schedule = json_data.get("schedule", []) # 來自 schedule 分頁
        
        # 建立課程對應星期的 dictionary: { '課程名': ['星期一', '星期二'] }
        course_to_days = {}
        for row in raw_schedule:
            if len(row) < 2: continue
            day_val = str(row[0]).strip()     # A 欄：星期
            course_val = str(row[1]).strip()  # B 欄：課程名稱
            if course_val not in course_to_days:
                course_to_days[course_val] = []
            course_to_days[course_val].append(day_val)
            
        # 依照星期結構組織資料
        structured_data = {day: {} for day in ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]}
        
        for row in raw_students:
            if len(row) < 3: continue
            class_name, student_name, subject = str(row[0]), str(row[1]), str(row[2])
            
            # 從 schedule 的對應關係中找出該課程屬於哪幾天
            target_days = course_to_days.get(subject, [])
            
            for day in target_days:
                if day in structured_data:
                    if subject not in structured_data[day]:
                        structured_data[day][subject] = []
                    structured_data[day][subject].append((class_name, student_name))
        return structured_data
    except Exception as e:
        st.error(f"資料同步失敗: {e}")
        return {}

# (其餘 UI 與儲存邏輯維持不變...)
