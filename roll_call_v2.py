# --- 5. 儲存與下載部分 (僅節錄需修改的儲存邏輯) ---
with col_save:
    if st.button("🚀 儲存紀錄至雲端", type="primary", use_container_width=True):
        if active_class not in st.session_state.done_list: 
            st.session_state.done_list.append(active_class)
        
        # 修正傳送內容：移除 time，保留固定欄位供 GAS 比對
        payload = [
            {
                "date": today_str, 
                "lesson": item[0],     # 班級
                "classroom": active_class, # 課堂
                "name": item[1],       # 姓名
                "status": item[2],     # 狀態
                "note": item[3]        # 原因
            } for item in status_results.values()
        ]
        
        try:
            requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=2) # 增加 timeout 秒數確保完成
            st.toast("🎉 雲端儲存成功（橫向新增）！")
        except:
            st.toast("傳送失敗，請檢查網路")
            
        time.sleep(0.5)
        st.rerun()
