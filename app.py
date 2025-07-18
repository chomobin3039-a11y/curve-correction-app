import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 儲存歷史資料的 CSV 檔案名稱
HISTORY_FILE = "curve_history.csv"

st.set_page_config(page_title="車削曲率修正計算", layout="centered")
st.title("📐 車削曲率修正量計算器")

# 初始化 session state
if "history" not in st.session_state:
    if os.path.exists(HISTORY_FILE):
        st.session_state.history = pd.read_csv(HISTORY_FILE)
    else:
        st.session_state.history = pd.DataFrame(columns=["日期時間", "設計曲率", "目前曲率", "比例", "修正量"])

# 使用者輸入
col1, col2 = st.columns(2)
with col1:
    design_curvature = st.number_input("設計曲率", format="%.3f")
with col2:
    current_curvature = st.number_input("目前曲率", format="%.3f")

# 預設比例常數
ratio = st.number_input("比例 (可調整，預設為 1.75)", value=1.75, step=0.01)

# 計算修正量
if st.button("計算修正量"):
    correction = (current_curvature - design_curvature) / 10 * ratio
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame({
        "日期時間": [timestamp],
        "設計曲率": [round(design_curvature, 3)],
        "目前曲率": [round(current_curvature, 3)],
        "比例": [round(ratio, 3)],
        "修正量": [round(correction, 5)]
    })
    st.session_state.history = pd.concat([new_data, st.session_state.history], ignore_index=True)
    st.success(f"修正量為：{correction:.5f}")

# 顯示歷史紀錄（修正量與比例位置對調）
st.subheader("📜 歷史紀錄")
reordered_cols = ["日期時間", "設計曲率", "目前曲率", "修正量", "比例"]
st.dataframe(st.session_state.history[reordered_cols], use_container_width=True)

# 匯出 Excel
if st.button("匯出 Excel"):
    excel_filename = f"curve_correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    st.session_state.history[reordered_cols].to_excel(excel_filename, index=False)

    # 自動調整欄寬
    from openpyxl import load_workbook
    wb = load_workbook(excel_filename)
    ws = wb.active
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width
    wb.save(excel_filename)

    st.success(f"✅ 匯出成功：{excel_filename}")
