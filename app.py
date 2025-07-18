import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="曲率修正計算器", layout="centered")

st.title("🔧 車削曲率修正計算器")

# 初始化 session state
if "history" not in st.session_state:
    st.session_state.history = []
if "gain" not in st.session_state:
    st.session_state.gain = 1.75

# 讀取上次紀錄（若有）
if os.path.exists("last_inputs.csv"):
    df_last = pd.read_csv("last_inputs.csv")
    if not df_last.empty:
        last_row = df_last.iloc[-1]
        default_design = last_row["設計曲率"]
        default_actual = last_row["目前曲率"]
        default_gain = last_row["比例"]
    else:
        default_design = default_actual = default_gain = ""
else:
    default_design = default_actual = default_gain = ""

# 使用者輸入
design_curvature = st.number_input("設計曲率", value=float(default_design) if default_design else 0.0, step=0.01)
actual_curvature = st.number_input("目前曲率", value=float(default_actual) if default_actual else 0.0, step=0.01)
gain = st.number_input("比例", value=float(default_gain) if default_gain else st.session_state.gain, step=0.01)
st.session_state.gain = gain

# 計算修正量
correction = (actual_curvature - design_curvature) / 10 * gain
st.metric(label="🔁 修正量", value=round(correction, 6))

# 紀錄當前輸入
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
record = {
    "時間": now,
    "修正量": round(correction, 6),
    "比例": gain,
    "設計曲率": design_curvature,
    "目前曲率": actual_curvature
}

if st.button("✅ 儲存紀錄"):
    st.session_state.history.append(record)
    st.success("已儲存！")

# 匯出 Excel 功能
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    df = df[["時間", "修正量", "比例", "設計曲率", "目前曲率"]]
    st.write("📜 歷史紀錄", df)

    # 匯出 Excel
    from io import BytesIO
    import openpyxl
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="紀錄")
        for col in writer.sheets["紀錄"].columns:
            writer.sheets["紀錄"].column_dimensions[col[0].column_letter].width = 15
    st.download_button("📥 下載 Excel", data=output.getvalue(), file_name="correction_history.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 儲存輸入值以供下次讀取
df_save = pd.DataFrame([record])
if os.path.exists("last_inputs.csv"):
    df_exist = pd.read_csv("last_inputs.csv")
    df_save = pd.concat([df_exist, df_save], ignore_index=True)
df_save.to_csv("last_inputs.csv", index=False)
