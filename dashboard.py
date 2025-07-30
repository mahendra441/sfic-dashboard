import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="SFIC Dashboard", layout="wide")

st.title("विभागीय जांच और FIR रिपोर्ट डैशबोर्ड\nBy SM Mahendra Yadav")

# ✅ आज की तारीख और समय दिखाएँ
today = datetime.now().strftime("%d-%m-%Y %H:%M")
st.markdown(f"🕒 **दिनांक और समय:** `{today}`")

# File Upload
file = st.file_uploader("Excel फ़ाइल अपलोड करें", type=["xlsx", "xls"])
if file:
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()

    # Optional cleaning
    df["हानि/गबन की राशि"] = pd.to_numeric(df["हानि/गबन की राशि"], errors="coerce")
    df["वसूली की गई राशि"] = pd.to_numeric(df["वसूली की गई राशि"], errors="coerce")
    df["FIR Date"] = pd.to_datetime(df["FIR Date"], errors="coerce")

    # Sidebar Filters
    st.sidebar.header("Filter Options")
    divisions = st.sidebar.multiselect("संभाग चुनें", df["संभाग का नाम"].dropna().unique())
    if divisions:
        df = df[df["संभाग का नाम"].isin(divisions)]

    # DDO Filter
    ddo_column = next((col for col in df.columns if "DDO" in col.upper()), None)
    if ddo_column:
        ddo_list = df[ddo_column].dropna().unique()
        selected_ddos = st.sidebar.multiselect("DDO चुनें", ddo_list)
        if selected_ddos:
            df = df[df[ddo_column].isin(selected_ddos)]

    # e-file no Filter
    if "e-file no" in df.columns:
        efile_list = df["e-file no"].dropna().unique()
        selected_efiles = st.sidebar.multiselect("E-File No चुनें", efile_list)
        if selected_efiles:
            df = df[df["e-file no"].isin(selected_efiles)]

    # KPIs
    st.subheader("📊 मुख्य आँकड़े:")
    col1, col2, col3 = st.columns(3)
    col1.metric("कुल प्रकरण", len(df))
    col2.metric("कुल हानि राशि", f"{df['हानि/गबन की राशि'].sum():,.2f} ₹")
    col3.metric("कुल वसूली", f"{df['वसूली की गई राशि'].sum():,.2f} ₹")

    # ✅ Division Wise Status (Grouped Bar Chart)
    st.subheader("📊 संभाग अनुसार हानि और वसूली की स्थिति (Division Wise Status)")
    div_chart_data = df.groupby("संभाग का नाम")[["हानि/गबन की राशि", "वसूली की गई राशि"]].sum().reset_index()

    fig_div = px.bar(
        div_chart_data,
        x="संभाग का नाम",
        y=["हानि/गबन की राशि", "वसूली की गई राशि"],
        barmode="group",
        title="Division Wise हानि/गबन की राशि vs वसूली की गई राशि",
        text_auto=True
    )

    fig_div.update_layout(
        yaxis_tickformat=',',
        yaxis_title="राशि (₹ में)"
    )
    fig_div.update_traces(
        hovertemplate='%{y:,.0f} ₹<extra></extra>'
    )

    st.plotly_chart(fig_div, use_container_width=True)

    # ✅ Recovery Percentage Summary Table
    st.subheader("📋 संभाग अनुसार हानि/गबन और वसूली प्रतिशत")
    summary = df.groupby("संभाग का नाम")[["हानि/गबन की राशि", "वसूली की गई राशि"]].sum()
    summary = summary[summary.index != "Total"]
    summary["वसूली प्रतिशत"] = (summary["वसूली की गई राशि"] / summary["हानि/गबन की राशि"]) * 100
    summary = summary.reset_index()
    st.dataframe(summary[["संभाग का नाम", "हानि/गबन की राशि", "वसूली की गई राशि", "वसूली प्रतिशत"]], use_container_width=True)

    # ✅ Download Button
    st.subheader("⬇️ Excel/CSV डाउनलोड करें")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="CSV डाउनलोड करें",
        data=csv,
        file_name="sfic_dashboard_data.csv",
        mime='text/csv'
    )

    # ✅ Full Table
    st.subheader("📋 पूरा डेटा")
    st.dataframe(df, use_container_width=True)
