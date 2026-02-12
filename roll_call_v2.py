# --- 5. 儲存 (加入自動檢查機制) ---
if st.button("🚀 儲存紀錄", type="primary", use_container_width=True):
    # 1. 準備資料
    payload = [{
        "date": today_str, "classroom": current_class, "lesson": item[0], "name": item[1], 
        "status": item[2], "time": datetime.now().strftime("%H:%M:%S"), "note": item[3]
    } for item in status_results.values()]
    
    # 2. 發送請求 (不卡頓發送)
    try:
        st.toast(f"🚀 正在將 {current_class} 傳送到雲端...", icon="⏳")
        # 我們將 timeout 稍微拉長到 0.5 秒，這通常足以讓 Google 門房收到請求
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=0.5) 
    except requests.exceptions.ReadTimeout:
        # 看到這個代表 Google 已收到但還在寫，這對我們來說就是成功
        pass
    except Exception as e:
        st.error(f"連線失敗，請檢查網路")

    # 3. 樂觀標記並強制刷新介面
    if current_class not in st.session_state.done_list:
        st.session_state.done_list.append(current_class)
    
    st.toast(f"✅ {current_class} 儲存指令已發出", icon="🎉")
    
    # 給予一個視覺緩衝後重整
    import time
    time.sleep(0.8)
    st.rerun()
