# --- 3. 狀態管理 ---
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
# 確保這區塊的括號完整閉合
weekday_map = {
    0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"
}
current_day = weekday_map.get(today_dt.weekday(), "星期一")

if 'done_list' not in st.session_state: 
    st.session_state.done_list = []

if 'current_class' not in st.session_state:
    # 這裡也要確保括號完整
    default_classes = list(all_data.get(current_day, {}).keys())
    st.session_state.current_class = default_classes[0] if default_classes else "舞蹈A"
