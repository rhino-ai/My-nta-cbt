import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import json
import time
import pandas as pd
import plotly.express as px
from datetime import datetime
import zipfile

# Page Config
st.set_page_config(layout="wide", page_title="NTA Style CBT Portal")

# --- CUSTOM CSS FOR NTA LOOK ---
st.markdown("""
<style>
    .q-btn { border-radius: 50% 50% 0 0; margin: 2px; height: 40px; width: 40px; }
    .answered { background-color: #28a745 !important; color: white; }
    .not-answered { background-color: #dc3545 !important; color: white; }
    .marked { background-color: #6f42c1 !important; color: white; }
    .not-visited { border: 1px solid #ccc; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'test_data' not in st.session_state:
    st.session_state.test_data = []
if 'current_que' not in st.session_state:
    st.session_state.current_que = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'time_per_question' not in st.session_state:
    st.session_state.time_per_question = {}

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Admin: Create Test", "Student: Take Test", "Analysis Dashboard", "User History"])

# --- 1. ADMIN: CREATE TEST ---
if menu == "Admin: Create Test":
    st.header("📝 Create New Test from PDF")
    up_pdf = st.file_uploader("Upload Question Paper PDF", type="pdf")
    
    if up_pdf:
        doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
        if st.button("🤖 AI: Auto-Detect Questions"):
            new_data = []
            for page in doc:
                blocks = page.get_text("blocks")
                for b in blocks:
                    if "Q." in b[4] or (len(b[4]) > 0 and b[4][0].isdigit()):
                        rect = fitz.Rect(b[0]-2, b[1]-2, b[2]+2, b[3]+2)
                        pix = page.get_pixmap(clip=rect)
                        img = Image.open(io.BytesIO(pix.tobytes()))
                        new_data.append({"image": img, "text": b[4], "subject": "General"})
            st.session_state.test_data = new_data
            st.success(f"Detected {len(new_data)} Questions!")

# --- 2. STUDENT: TAKE TEST ---
elif menu == "Student: Take Test":
    if not st.session_state.test_data:
        st.warning("Please upload a test first in Admin section.")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1: # Question Area
            q_idx = st.session_state.current_que
            st.subheader(f"Question {q_idx + 1}")
            st.image(st.session_state.test_data[q_idx]["image"])
            
            # Options
            ans = st.radio("Select Answer:", ["A", "B", "C", "D"], key=f"q_{q_idx}")
            st.session_state.responses[q_idx] = ans
            
            # Buttons
            c1, c2, c3 = st.columns(3)
            if c1.button("Save & Next"):
                if st.session_state.current_que < len(st.session_state.test_data) - 1:
                    st.session_state.current_que += 1
                    st.rerun()
            if c2.button("Mark for Review"): pass
            if c3.button("Clear Response"): 
                st.session_state.responses[q_idx] = None
        
        with col2: # Palette & Timer
            st.write("### Time Left: 180:00")
            st.write("### Question Palette")
            # Grid of buttons
            for i in range(len(st.session_state.test_data)):
                if st.button(f"{i+1}", key=f"btn_{i}"):
                    st.session_state.current_que = i
                    st.rerun()
            
            if st.button("🏁 SUBMIT TEST", type="primary"):
                st.success("Test Submitted Successfully!")

# --- 3. ANALYSIS DASHBOARD ---
elif menu == "Analysis Dashboard":
    st.header("📊 Result Analysis")
    ans_pdf = st.file_uploader("Upload Answer Key PDF", type="pdf")
    if ans_pdf:
        # Dummy Analysis for now
        data = {
            "Subject": ["Physics", "Chemistry", "Maths"],
            "Score": [40, 35, 55],
            "Time (min)": [60, 50, 70]
        }
        df = pd.DataFrame(data)
        fig = px.pie(df, values='Score', names='Subject', title='Subject-wise Performance')
        st.plotly_chart(fig)
        st.table(df)


