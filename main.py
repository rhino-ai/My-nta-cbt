import streamlit as st
import fitz
from PIL import Image
import io
import json
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="NTA Exam Portal")

# CSS for NTA Look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .q-palette { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; }
    </style>
    """, unsafe_allow_html=True)

if 'responses' not in st.session_state: st.session_state.responses = {}

menu = st.sidebar.radio("Navigation", ["Admin: Create Test", "Student: Live Exam", "My Performance"])

# --- ADMIN: AUTO CROPPER ---
if menu == "Admin: Create Test":
    st.header("📤 Auto-Create Test")
    pdf_file = st.file_uploader("Upload Question PDF", type="pdf")
    if pdf_file:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        if st.button("Process Full Paper"):
            questions = []
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.open(io.BytesIO(pix.tobytes()))
                w, h = img.size
                for i in range(4): # 4 questions per page
                    crop = img.crop((0, i*(h/4), w, (i+1)*(h/4)))
                    questions.append(crop)
            st.session_state['qs'] = questions
            st.success(f"Test Created with {len(questions)} Questions!")

# --- STUDENT: NTA INTERFACE ---
elif menu == "Student: Live Exam":
    if 'qs' in st.session_state:
        st.subheader("JEE Main Mock Test 2025")
        col_q, col_p = st.columns([3, 1])
        
        with col_q:
            q_no = st.number_input("Question Number", 1, len(st.session_state['qs']), step=1)
            st.image(st.session_state['qs'][q_no-1], use_container_width=True)
            ans = st.radio("Select Option:", ["A", "B", "C", "D"], key=f"ans_{q_no}", index=None)
            
            c1, c2, c3 = st.columns(3)
            if c1.button("Save & Next"): st.session_state.responses[q_no] = ans
            c2.button("Mark for Review")
            if c3.button("Clear Response"): st.session_state.responses.pop(q_no, None)

        with col_p:
            st.write("⏱️ Time Left: 02:55:12")
            st.write("### Question Palette")
            for row in range((len(st.session_state['qs']) // 5) + 1):
                cols = st.columns(5)
                for i in range(5):
                    idx = row * 5 + i + 1
                    if idx <= len(st.session_state['qs']):
                        color = "primary" if idx in st.session_state.responses else "secondary"
                        cols[i].button(str(idx), key=f"btn_{idx}", type=color)
            
            if st.button("SUBMIT TEST", type="primary"):
                st.session_state.submitted = True
                st.balloons()

    else:
        st.warning("Admin: Upload PDF first!")

# --- ANALYSIS ---
elif menu == "My Performance":
    st.header("📊 Performance Analysis")
    m1, m2, m3 = st.columns(3)
    m1.metric("Predicted Percentile", "98.2 %ile")
    m2.metric("Accuracy", "85%")
    m3.metric("Time per Q", "1.2 min")
    
    # Sample Chart
    data = pd.DataFrame({"Subject": ["Phy", "Chem", "Math"], "Marks": [60, 80, 45]})
    fig = px.bar(data, x="Subject", y="Marks", color="Subject")
    st.plotly_chart(fig)
